import os

os.environ["DJANGO_SETTINGS_MODULE"] = "recproject.settings"
import django

django.setup()

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVC
from sklearn.naive_bayes import ComplementNB
from sklearn import linear_model
import random, datetime, sys, time, datetime
from django.utils import timezone
from dateutil.parser import parse as parse_date
from django.core.mail import send_mail

from recapp import models

n_articles = 8

def lprint(*a):
    print("%.3f" % time.time(), *a)


def generate_recommendations(
    vectorizer, input_texts, all_articles, all_vectorized_articles
):
    lprint("fitting regression")

    svm = linear_model.LinearRegression()
    scored_articles = vectorizer.transform([text for text, score in input_texts])
    svm.fit(scored_articles, [(1 if score else -1) for text, score in input_texts])

    # words_by_score = ([ (word, svm.coef_[i]) for word, i in vectorizer.vocabulary_.items() ])
    # words_by_score.sort(key=lambda x: x[1])
    # print(words_by_score)

    lprint("predicting")
    predictions = svm.predict(all_vectorized_articles)

    lprint("sorting")
    all_articles = sorted(
        [(predictions[i], art) for i, art in enumerate(all_articles)],
        key=lambda p: p[0],
    )
    # print([ (p, a.title) for p, a in all_articles ])
    # for score, art in all_articles[-20:]:
    #    print(score, art)

    return [art for _, art in all_articles]


def fetch_inputs_and_generate_recommendations(
        vectorizer, all_articles, all_vectorized_articles, dashboard, last_recommendations,
        *, score_only_ids=None, n_articles=n_articles
):
    lprint("processing", dashboard)

    keywords = dashboard.keywords.split("\n")
    lprint("loading database")
    input_pairs = [
        (p.article, 1 if p.like_or_dislike == "like" else 0)
        for p in models.DashboardArticle.objects.filter(
            dashboard=dashboard
        ).prefetch_related("article")
        if p.like_or_dislike != "none"
    ]

    already_scored_ids = set([article.id for article, score in input_pairs])
    lprint("loaded database")

    r = random.Random(13)
    for i in range(5):
        input_pairs.append((r.choice(all_articles), 0))

    all_matching_kw = [
        a for a in all_articles if any(kw.lower() in a.title.lower() for kw in keywords)
    ][:100]
    lprint("all matching kw")
    for i in range(5):
        if all_matching_kw:
            input_pairs.append((r.choice(all_matching_kw), 1))

    input_pairs_hash = hash(tuple(input_pairs))

    if last_recommendations.get(dashboard.id) == input_pairs_hash:
        lprint("no changes")
        return

    last_recommendations[dashboard.id] = input_pairs_hash

    # concat title
    input_texts = [
        (article.text_for_recommender, score) for article, score in input_pairs
    ]
    input_texts += [(keyword, 1) for keyword in keywords]

    lprint("generating recommendations")

    sorted_articles = generate_recommendations(
        vectorizer, input_texts, all_articles, all_vectorized_articles
    )
    lprint("done")

    to_recommend = [
        art for art in sorted_articles
        if art.id not in already_scored_ids and ((not score_only_ids) or art.id in score_only_ids) ]
    to_recommend = to_recommend[-n_articles:]

    return to_recommend


def generate_and_save_recommendations(
        vectorizer, all_articles, all_vectorized_articles, dashboard, last_recommendations,
        n_articles
):
    to_recommend = fetch_inputs_and_generate_recommendations(
        vectorizer, all_articles, all_vectorized_articles, dashboard, last_recommendations,
        score_only_ids=None, n_articles=n_articles
    )
    if to_recommend is None:
        return
    
    models.DashboardArticle.objects.filter(
        dashboard=dashboard, like_or_dislike="none"
    ).exclude(article__id__in=[art.id for art in to_recommend]).update(
        is_no_longer_recommended=True
    )

    for art in to_recommend:
        try:
            a = models.DashboardArticle.objects.get(dashboard=dashboard, article=art)
            a.is_no_longer_recommended = False
            a.save()
        except models.DashboardArticle.DoesNotExist:
            models.DashboardArticle(
                dashboard=dashboard,
                article=art,
                added=timezone.now(),
                like_or_dislike="none",
                is_no_longer_recommended=False,
            ).save()

def train_tfidf(all_articles):    
    vectorizer = TfidfVectorizer()
    lprint("training tfidf", "(doc count = {})".format(len(all_articles)))
    all_vectorized_articles = vectorizer.fit_transform(
        [article.text_for_recommender for article in all_articles]
    )
    return vectorizer, all_vectorized_articles

notification_sender = 'root@localhost'

def send_notification_email(dashboard, to_recommend):
    body = '\n\n'.join([
        article.title + '\n' + article.url.url + '\n' + article.short_description
        for article in to_recommend
    ])
    send_mail(
        'Recommendations for %s' % dashboard.title,
        body,
        notification_sender,
        [dashboard.user.email],
        fail_silently=False,
    )

def send_notifications_for_dashboards(start_date, end_date, dashboards):
    all_articles = list(models.Article.objects.all())
    
    vectorizer, all_vectorized_articles = train_tfidf(all_articles)
    all_recommendable_article_ids = [
        article.id
        for article in all_articles
        if start_date <= article.created < end_date 
    ]

    for dashboard in dashboards:
        to_recommend = fetch_inputs_and_generate_recommendations(
            vectorizer, all_articles, all_vectorized_articles, dashboard, last_recommendations={},
            score_only_ids=set(all_recommendable_article_ids)
        )
        # send email
        send_notification_email(dashboard, to_recommend)

def send_notifications_for_frequency(frequency, end_date):
    dashboards = list(models.Dashboard.objects.filter(notifications=frequency))

    delta = {
        'daily': datetime.timedelta(days=1),
        'weekly': datetime.timedelta(days=7),
        'monthly': datetime.timedelta(days=31),
    }[frequency] 
    start_date = end_date - delta
    send_notifications_for_dashboards(start_date, end_date, dashboards)
    
def run_standard_recommendation(this_dashboard, once=False, n_articles=n_articles):
    all_articles = list(models.Article.objects.all())
    dashboards = list(models.Dashboard.objects.all())

    vectorizer, all_vectorized_articles = train_tfidf(all_articles)
    last_recommendations = {}

    while True:
        dashboards = list(models.Dashboard.objects.all())
        for dashboard in dashboards:
            if this_dashboard and this_dashboard != dashboard.title and this_dashboard != dashboard.user.username:
                continue
            generate_and_save_recommendations(
                vectorizer, all_articles, all_vectorized_articles, dashboard, last_recommendations,
                n_articles=n_articles
            )

        if once:
            break
        time.sleep(1)


def main():
    command = sys.argv[1]
    if command == 'notifications':
        frequency, start_date = sys.argv[2:]
        start_date = parse_date(start_date  + ' 00:00Z')
        send_notifications_for_frequency(frequency, start_date)
    elif command == 'standard':
        this_dashboard = sys.argv[2] if len(sys.argv) > 2 else None
        run_standard_recommendation(this_dashboard)
    else:
        print('bad command', command)
        sys.exit(1)

if __name__ == "__main__":
    main()

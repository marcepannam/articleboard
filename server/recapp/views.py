from django.shortcuts import render
from django.http import JsonResponse, QueryDict, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core import mail
from . import models
from django.utils import timezone
import json
from random import shuffle

def login_required(f):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            return f(request, *args, **kwargs)
        else:
            return HttpResponse('Unauthorized', status=401)

    return wrapper

@login_required
def dashboards(request):
    dashboards = models.Dashboard.objects.filter(user=request.user)
    return JsonResponse({
        'dashboards': [ {'id': dashboard.id, 'title': dashboard.title} for dashboard in dashboards ]
    })

@login_required
def dashboard(request):
    if request.method == 'PUT':
        dashboard = models.Dashboard.objects.get(id=request.GET['id'], user=request.user)
        data = QueryDict(request.body)
        dashboard.title = data['title']
        dashboard.keywords = data['keywords']
        dashboard.notifications = data['notifications']
        dashboard.save()
        return JsonResponse({'id': dashboard.id})

    if request.method == 'POST':
        dashboard = models.Dashboard(user=request.user)
        dashboard.title = request.POST['title']
        dashboard.keywords = request.POST['keywords']
        dashboard.notifications = request.POST['notifications']
        dashboard.save()
        return JsonResponse({'id': dashboard.id})
    
    if request.GET['id'] == 'all':
        articles = models.DashboardArticle.objects.filter(dashboard__user=request.user).order_by('?').prefetch_related('dashboard')
        dashboard_title = 'All'
        keywords = ''
        dashboard_notifications = ''
    else:
        dashboard = models.Dashboard.objects.get(id=request.GET['id'], user=request.user)
        articles = models.DashboardArticle.objects.filter(dashboard=dashboard).prefetch_related('dashboard')
        dashboard_title = dashboard.title
        keywords = dashboard.keywords
        dashboard_notifications = dashboard.notifications

    filter = request.GET.get('filter', 'new')
    like_or_dislike_filter = {
        'new': 'none',
        'liked': 'like',
        'disliked': 'dislike',
    }[filter]
    
    return JsonResponse({
        'dashboard_title': dashboard_title,
        'keywords': keywords,
        'notifications': dashboard_notifications,
        'articles': [
            {
                'id': p.id,
                'dashboard': p.dashboard.title,
                'title': p.article.title,
                'link': p.article.url.url,
                'short_description': p.article.short_description,
                'like_or_dislike': p.like_or_dislike,
                'added': p.added
            }
            for p in 
            articles.filter(like_or_dislike=like_or_dislike_filter, is_no_longer_recommended=False).prefetch_related('article', 'article__url')
        ]
    })

@login_required
def article(request):
    article = models.DashboardArticle.objects.get(dashboard__user=request.user, id=request.GET['id'])
    label = request.POST['label']
    if label == 'flag':
        label = 'dislike'
        mail.mail_managers('User flagged an article', 'article URL: {}\narticle title: {}\nuser: {}'.format(
            article.article.url,
            article.article.title,
            request.user
        ))
        
    article.like_or_dislike = label
    article.save()
    return JsonResponse({'status': 'ok'})

@login_required
def add_article_from_url(request):
    article = article_downloader.download_and_save_single_link(request.POST['url'])
    if article:
        dashboards = json.loads(request.POST['dashboards'])
        for dashboard in dashboards:
            dashboard = models.Dashboard.objects.get(id=dashboard, user=request.user)
            models.DashboardArticle(dashboard=dashboard, article=article,
                                    added=timezone.now(),
                                    like_or_dislike='like',
                                    is_no_longer_recommended=False).save()
            
    return JsonResponse({'ok': article is not None})

vectors = None

def suggest_keywords(request):
    from gensim.models import Word2Vec
    import gensim.downloader

    global vectors
    # lazy loading to improve start up performance
    if vectors is None:
        vectors = gensim.downloader.load('glove-twitter-25')

    words = request.GET['keywords'].split()
    words = [ word for word in words if word in vectors ]
    if words:
        words = [ word for word, score in vectors.most_similar(words) ]
    return JsonResponse({'words': words})

def index_html(request, _):
    return HttpResponse(open('build/index.html').read())

def main_page(request):
    return render(request, 'index.html')

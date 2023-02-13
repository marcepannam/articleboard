from django.test import TestCase
from recapp.models import Url, Response, Article, DashboardArticle
from django.test import Client
from django.contrib.auth.models import User
import generate_recommendation

class TestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client = Client()
        self.client.login(username='testuser', password='12345')

    def test_add_dashboard(self):
        response = self.client.get('/dashboards')
        self.assertEquals(response.json()['dashboards'], [])

        response = self.client.post('/dashboard', {'title': '1', 'keywords': 'kw', 'notifications': ''})
        id = (response.json()['id'])

        response = self.client.get('/dashboards')
        self.assertEquals(response.json()['dashboards'], [
            {'id': id, 'title': '1'}
        ])

    def insert_article(self, url, title, body):
        url = Url(url=url)
        url.save()
        article = Article(url=url, title=title, article_text=body, short_description=body)
        article.save()

    def insert_some_articles(self):
        self.insert_article('http://1', 'Hello world', 'world!')
        self.insert_article('http://2', 'Python stuff', 'python is a programming langauge')

        self.insert_article('http://3', 'Ruby stuff', 'ruby is a programming language!')

    def test_recommendation_by_keyword(self):
        self.insert_some_articles()
        self.client.post('/dashboard', {'title': '1', 'keywords': 'python', 'notifications': ''})
        generate_recommendation.run_standard_recommendation(None, once=True, n_articles=1)
        
        dashboard = self.client.get('/dashboard?id=1').json()
        self.assertEquals([ a['title'] for a in dashboard['articles'] ], ['Python stuff'])


    def test_recommendation_by_likes(self):
        self.insert_some_articles()
        self.client.post('/dashboard', {'title': '1', 'keywords': 'foo', 'notifications': ''})

        generate_recommendation.run_standard_recommendation(None, once=True, n_articles=3)

        python_art = DashboardArticle.objects.get(article__title='Python stuff')
        r = self.client.post('/article?id=' + str(python_art.id), {'label': 'like'})
        self.assertEquals(r.json(), {'status': 'ok'})

        generate_recommendation.run_standard_recommendation(None, once=True, n_articles=1)
        
        dashboard = self.client.get('/dashboard?id=1').json()
        print(dashboard)
        self.assertEquals([ a['title'] for a in dashboard['articles'] ], ['Ruby stuff'])

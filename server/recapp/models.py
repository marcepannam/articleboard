from django.db import models
from django.contrib.auth.models import User
import datetime

# Create your models here.

class Dashboard(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=500, unique=True)
    keywords = models.TextField(max_length=10_000, default='')
    created = models.DateTimeField(auto_now_add=True)

    notifications = models.CharField(max_length=100, choices=[('weekly', 'weekly'), ('daily', 'daily'), ('monthly', 'monthly'), ('disabled', 'disabled')], default='disabled')
    
    def __str__(self):
        return 'Dashboard(%r, %r)' % (self.user, self.title)

class Url(models.Model):
    url = models.CharField(max_length=200, unique=True)
    source = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add=True)

class Response(models.Model):
    url = models.ForeignKey(Url, on_delete=models.CASCADE, default="")
    timestamp = models.DateTimeField(default=datetime.datetime(2000,1,1))
    status_code = models.IntegerField(default=None, null=True)
    was_successful = models.BooleanField(default=False)
    error_type = models.CharField(max_length=200, choices=[('HttpError', 'HttpError'), ('GeneralError', 'GeneralError'), ('TimeoutError', 'TimeoutError'), ('ParserError', 'ParserError'), ('none', 'none')], default='none', blank=True, null=True)
    error_message = models.CharField(max_length=200, default='', blank=True, null=True) 

class CrawlingTarget(models.Model):
    url = models.CharField(max_length=200, unique=True)
    created = models.DateTimeField(auto_now_add=True)

class Article(models.Model):
    title = models.CharField(max_length=1000)
    url = models.OneToOneField(Url, on_delete=models.CASCADE, related_name='article', unique=True)
    article_text = models.TextField(max_length=1_000_000)
    short_description = models.TextField(max_length=10_000)
    created = models.DateTimeField(auto_now_add=True)

    @property
    def text_for_recommender(self):
        return self.title + '\n' + self.article_text[:1000]

    def __str__(self):
        return 'Article(url=%r, title=%r)' % (self.url.url, self.title)
    
class DashboardArticle(models.Model):
    like_or_dislike = models.CharField(max_length=200, choices=[('like', 'like'), ('dislike', 'dislike'), ('none', 'none')], default='none')
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    dashboard = models.ForeignKey(Dashboard, on_delete=models.CASCADE)
    added = models.DateTimeField()
    is_no_longer_recommended = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('dashboard', 'article',)

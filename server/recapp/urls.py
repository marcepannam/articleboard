from django.urls import path, include, re_path
from . import views
from django.shortcuts import redirect


urlpatterns = [
    path('', views.main_page, name='main_page'),
    path('dashboards', views.dashboards, name='dashboards'),
    path('dashboard', views.dashboard, name='dashboard'),
    path('article', views.article, name='article'),
    path('add-article-from-url', views.add_article_from_url, name='article'),
    path('suggest-keywords', views.suggest_keywords, name='suggest_keywords'),
    re_path('app/(.*)', views.index_html, name='index'),
]

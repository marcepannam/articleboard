# Fetches article URLs using HackerNews API
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'recproject.settings'
import django, requests, json
django.setup()

from recapp.models import Url

from .article_downloader import download_and_save

headers = {'user-agent': 'article-recommender'}

def get_urls_from_hn(index):
    # Get the top 100 stories
    url = "https://hacker-news.firebaseio.com/v0/" + index + ".json?print=pretty"
    results = requests.get(url, headers=headers)

    articles = json.loads(results.content)

    for article in articles:
        url_str = requests.get("https://hacker-news.firebaseio.com/v0/item/" + str(article) + ".json?print=pretty")
        content = json.loads(url_str.content)
        if content is not None and 'url' in content:
            yield json.loads(url_str.content)['url']

def get_urls(index):
    urls = get_urls_from_hn(index)
    for url in urls:
        if not Url.objects.filter(url=url).exists():
            Url( 
                url = url,
                was_downloaded = False
            ).save()
            
if __name__ == '__main__':
    # download most recent stories
    get_urls('newstories')
    # ...and current high scored ones
    get_urls('topstories')
    
    download_and_save()

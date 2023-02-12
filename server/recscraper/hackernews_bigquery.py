import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'recproject.settings'
import django, requests, json
django.setup()

from recapp.models import Url
from csv import DictReader

urls = DictReader(open('../bq-results-20230113-215544-1673646997814.csv'))

for x in urls:
    url = x['url']
    if url != '':
        print(url)
        Url.objects.get_or_create(url=url, source='hackernews_bigquery')
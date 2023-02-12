import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'recproject.settings'

import django, requests, json
django.setup()

from recapp.models import Url, CrawlingTarget

import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.item import Item, Field
from scrapy.spiders import Rule
from scrapy.linkextractors import LinkExtractor

def crawl(urls):
    domains = [ url.split('/')[2] for url in urls ]
    print('crawling', urls, ' allowed domains:', domains)
    
    class Crawler(scrapy.spiders.CrawlSpider):
        name = 'crawl'
        allowed_domains = domains
        start_urls = urls
        rules = (
            Rule(LinkExtractor(allow=r''), callback='on_visit', follow=True),
        )

        def on_visit(self, response):
            print(response.url)
            try:
                Url.objects.get_or_create(url=response.url, source='crawler')
            except django.db.utils.IntegrityError:
                pass
                
    settings = dict()
    settings['USER_AGENT'] = 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
    settings['ITEM_PIPELINES'] = dict()
    settings['DEPTH_PRIORITY'] = 1
    settings['DEPTH_LIMIT'] = 3
    
    process = CrawlerProcess(settings=settings)
    process.crawl(Crawler)
    process.start()

def crawl_all():
    url = [ target.url for target in CrawlingTarget.objects.all() ]
    crawl(url)
    
if __name__ == '__main__':
    crawl_all()

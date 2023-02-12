import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'recproject.settings'
import django, requests, json, random
django.setup()

import requests
import traceback
import json
from recapp.models import Article, Url, Response
from django.utils import timezone
from distutils.log import error
from readability import Document
from bs4 import BeautifulSoup
from bs4.element import Comment
import requests
import logging, readability
import multiprocessing.pool
from requests.exceptions import HTTPError
from .exceptions import ResponseError
from lxml.etree import ParseError

user_agent = {
    "User-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36"
}


def tag_visible(element):
    if element.parent.name in [
        "style",
        "script",
        "head",
        "title",
        "meta",
        "[document]",
    ]:
        return False
    if isinstance(element, Comment):
        return False
    return True


def text_from_html(texts):
    visible_texts = filter(tag_visible, texts)
    return " ".join(t.strip().replace("\n", " ") for t in visible_texts)


def download_title_and_text(url_object):
    
    url = url_object.url
    
    try:
        response = requests.get(url, headers=user_agent, timeout=60)
        response.raise_for_status()

    except HTTPError as exc:
        raise ResponseError(
            status_code = response.status_code,
            type = 'HTTPError',
            message = str(exc)
        )

    except TimeoutError as exc:
        raise ResponseError(
            status_code = response.status_code,
            type = 'TimeoutError',
            message = str(exc)
    )

    except ConnectionError as exc:
        raise ResponseError(
            status_code = None,
            type = 'ConnectionError',
            message = str(exc)
    )
 

    except Exception as exc:
        raise ResponseError(
            status_code = None,
            type = 'GeneralError',
            message = str(exc)
        )


    if not response.headers['content-type'].startswith('text/html'):
        raise ResponseError(
            status_code = None,
            type='NonHtmlContent',
            message = 'non-html content {0}'.format(response.headers['content-type'])
        )

    try:
        doc = Document(response.text)
        soup = BeautifulSoup(doc.summary(), "html.parser")
        texts = soup.findAll(text=True)
        title = doc.title()
        text = text_from_html(texts)
    except (ParseError, readability.readability.Unparseable) as exc:
        raise ResponseError(
            status_code = None,
            type = 'ParserError',
            message = str(exc)
        )

    return (title, text, response)

def download_link(new_url):

    assert isinstance(new_url, Url)

    existing = Article.objects.filter(url=new_url)

    print("existing: ",existing)

    if existing.exists():
        print('already downloaded', new_url.url)
        return existing[0]

    print('downloading', new_url.url)
    try:
        title, text, response = download_title_and_text(new_url)

        article = Article(
            title=title,
            article_text=text,
            short_description=text[:1000],
            url=new_url,
        )
        article.save()

        Response(
        url=new_url,
        timestamp=timezone.now(),
        status_code=response.status_code,
        was_successful=True).save()

        return article

    except ResponseError as e:

        Response(
        url=new_url,
        timestamp=timezone.now(),
        status_code=e.status_code,
        was_successful=False,
        error_type = e.type,
        error_message = e.message
        ).save()


def download_and_save():
    new_urls = list(Url.objects.filter(article=None))
    random.shuffle(new_urls)

    pool = multiprocessing.pool.ThreadPool(8)
    pool.map(download_link, new_urls)

def download_and_save_single_link(link):

    new_url, _ = Url.objects.get_or_create(url=link)

    new_url.save()

    return download_link(new_url) 

if __name__ == '__main__':
    download_and_save()


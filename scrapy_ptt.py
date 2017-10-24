#!/usr/bin/python
# -*- coding:utf-8 -*-
# From the tutorial in below reference link:
# https://github.com/leVirve/CrawlerTutorial

# Standard import
import urlparse
from multiprocessing import Pool
#from contextlib import closing

# Installed import
import requests
from bs4 import BeautifulSoup

# Self-defined import
from utility_print import pretty_print

INDEX = 'https://www.ptt.cc/bbs/Tech_Job/index.html'
PTT_INDEX = 'https://www.ptt.cc'
NOT_EXIST = BeautifulSoup('<a>本文已被刪除</a>', 'html.parser').a
PAGE_NUM = 2

def get_web_page(url):
    """The function is used to get the url content"""
    resp = requests.get(
        url=url,
        cookies={'over18': '1'}
    )
    if resp.status_code != 200:
        print('Invalid url:', resp.url)
        return None
    else:
        return resp.text

def get_posts_on_page(url):
    """The function that collect the info of the posts on one page and return the next page link"""
    page = get_web_page(url)
    posts = list()
    if page:
        soup = BeautifulSoup(page, 'html.parser')
        articles = soup.find_all('div', 'r-ent')
        controls = soup.find('div', 'btn-group-paging').find_all('a', 'btn')
        link = controls[1].get('href')
        for article in articles:
            meta = article.find('div', 'title').find('a') or NOT_EXIST
            posts.append({
                'title': meta.getText().encode('utf-8').strip(),
                'link': meta.get('href') if meta.get('href') is None else meta.get('href').encode('utf-8'),
                'push': article.find('div', 'nrec').getText().encode('utf-8'),
                'date': article.find('div', 'date').getText().encode('utf-8'),
                'author': article.find('div', 'author').getText().encode('utf-8')
            })
    return posts, link

def get_pages(num):
    """The function that gets posts in specific numbers (num) of pages"""
    page_url = INDEX
    all_posts = list()
    for i in range(num):
        posts, link = get_posts_on_page(page_url)
        all_posts += posts
        page_url = urlparse.urljoin(INDEX, link)
    return all_posts

def fetch_article_content(link):
    """Get content of each article"""
    #if(link is None):
    #    print('[WARNING]: None')
    #    return 'Null link'
    #elif(not type(link) is 'list'):
    #    ii = 0
    #    for i_link in link:
    #        if i_link is None:
    #            print('[WARNING]: None in list')
    #        else:
    #            print('[WARNING ' + str(ii) + ']:' + i_link)
    #            ii = ii+1
    #    return 'Null link'
    #else:
    #    print('[WARNING]:' + link)
    #url = urlparse.urljoin(PTT_INDEX, str(link))
    if link[0] is not None:
        url = urlparse.urljoin(PTT_INDEX, link[0].encode('utf-8'))
        response = requests.get(url)
        return response.text
    else:
        return 'No content!'

def get_articles(metadata):
    """Get each article info via multithread"""
    #print('Enter get_articles')
    post_links = [[meta['link']] for meta in metadata]
    #with closing(Pool(processes=8)) as pool:
    #    contents = pool.map(fetch_article_content, post_links)
    # In Python 2.x and 3.0, 3.1 and 3.2, multiprocessing.Pool() objects are not context managers. 
    # You cannot use them in a with statement.
    pool = Pool(processes=8)
    contents = pool.map(fetch_article_content, post_links)
    return contents

if __name__ == '__main__':
    #for post in get_pages(PAGE_NUM):
    #    pretty_print(post['push'], post['title'], post['date'], post['author'])
    metadata_main = get_pages(PAGE_NUM)
    articles_main = get_articles(metadata_main)

    print('共%d項結果：' % len(articles_main))
    for post, content in zip(metadata_main, articles_main):
        #pretty_print(post['push'], post['title'], post['date'], post['author'])
        print('%s %s %s, 網頁內容共 %s 字' % (post['date'], post['author'], post['title'], len(content)))
        #print('{0} {1: <15} {2}, 網頁內容共 {3} 字'.format(post['date'], post['author'], post['title'], len(content)))
# encoding=utf-8

import os
from time import sleep
import settings
import requests
from bs4 import BeautifulSoup


def crawl(offset=20):
    url = 'https://www.zhihu.com/node/ProfileFollowersListV2'
    params = {
        'method': 'next',
        '_xsrf': settings.PARAMS_XSRF,
        'params': '{"offset":%d,"order_by":"created","hash_id":"%s"}' % (offset, settings.PARAMS_HASH_ID)
    }
    response = requests.get(url,
                            data=params,
                            headers=settings.HEADERS,
                            cookies=settings.COOKIES)

    if response.status_code == 200:
        return parse_page(response.text)
    else:
        print 'Unexpected status code: %d' % response.status_code
        print 'Body: ', response.text
        return False


def parse_page(html):
    soup = BeautifulSoup(html, 'html.parser')
    has_next_page = soup.find(id='zh-load-more')
    if has_next_page:
        imgs = soup.findAll('img', {'class': 'zm-item-img-avatar'})
        for img in imgs:
            try:
                download_image(img['src'])
                sleep(settings.DOWNLOAD_DELAY)
            except requests.exceptions.ConnectionError:
                print 'Download image timeout.'
                continue
        return True
    else:
        print 'No more pages.'
        print 'HTML Content:', html
        return False


def download_image(url):
    response = requests.get(url, timeout=3)
    avatar_dir = settings.DOWNLOAD_PATH
    filename = os.path.join(avatar_dir, url.split('/')[-1])

    if not os.path.exists(avatar_dir):
        os.mkdir(avatar_dir)

    with open(filename, 'wb') as fp:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                fp.write(chunk)
        fp.close()


if __name__ == '__main__':
    for offset in xrange(20, 140, 20):
        if not crawl(offset):
            break

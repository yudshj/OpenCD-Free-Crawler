import configparser
import requests
import bs4
import re

from http import cookiejar
from itertools import chain

BASEURL = 'https://open.cd/torrents.php'
DOWNLOAD_URL = 'https://open.cd/download.php?id={id}&passkey={passkey}'

NOT_DOWNLOADED_FREE = '?inclbookmarked=0&incldead=1&spstate=2&option-torrents=6&page={0}'
NOT_DOWNLOADED_FREE_2x = '?inclbookmarked=0&incldead=1&spstate=4&option-torrents=6&page={0}'
ALL_FREE = '?inclbookmarked=0&incldead=1&spstate=2&option-torrents=0&page={0}'
ALL_FREE_2x = '?inclbookmarked=0&incldead=1&spstate=4&option-torrents=0&page={0}'
# 6 for not downloaded only, 0 for all

def get_page_data(cookie_jar, url, passkey, more_page=False):
    respon = requests.get(url, cookies=cookie_jar)
    dom = bs4.BeautifulSoup(respon.text, features="html.parser")
    form = dom.find('form', {'id': 'form_torrent'})
    try:
        torrents = [re.match(r'.*id=([0-9]*).*?', td.find('a').get('href')).group(1) for td in form.find_all('table', {'class': 'torrentname'})]
        ret = (DOWNLOAD_URL.format(id=x, passkey=passkey) for x in torrents)
        pages = set(BASEURL + x.get('href') for x in form.find('p').find_all('a')) if more_page else None
        return ret, pages
    except Exception as e:
        print(url)
        print(e)
        return [], []

def work(url, cookieJar, passkey):
    page_0, more_pages_url = get_page_data(cookieJar, url.format(0), passkey, True)
    pages = (get_page_data(cookieJar, x, passkey)[0] for x in more_pages_url)
    result = set((url for page in chain([page_0], pages) for url in page))
    return result


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('config.ini')
    passkey = config['account']['passkey']
    cj = cookiejar.MozillaCookieJar(config['account']['path'])
    cj.load()
    fi = work(BASEURL + NOT_DOWNLOADED_FREE, cj, passkey) | work(BASEURL + NOT_DOWNLOADED_FREE_2x, cj, passkey)
    for i in fi:
        print(i)
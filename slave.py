import configparser
import requests
import bs4
import re

from functools import reduce
from http import cookiejar
from itertools import chain

BASEURL = 'https://open.cd/torrents.php'
DOWNLOAD_URL = 'https://open.cd/download.php?id={id}&passkey={passkey}'

NOT_DOWNLOADED_FREE = '?inclbookmarked=0&incldead=1&spstate=2&option-torrents=6&page={0}'
NOT_DOWNLOADED_FREE_2x = '?inclbookmarked=0&incldead=1&spstate=4&option-torrents=6&page={0}'
ALL_FREE = '?inclbookmarked=0&incldead=1&spstate=2&option-torrents=0&page={0}'
ALL_FREE_2x = '?inclbookmarked=0&incldead=1&spstate=4&option-torrents=0&page={0}'
# 6 for not downloaded only, 0 for all
EXTENDED_URL = [NOT_DOWNLOADED_FREE, NOT_DOWNLOADED_FREE_2x]

CONFIG = configparser.ConfigParser()
CONFIG.read('config.ini')
PASSKEY = CONFIG['account']['passkey']
COOKIEJAR = cookiejar.MozillaCookieJar(CONFIG['account']['path'])
COOKIEJAR.load()


def get_page_data(cookie_jar, url, passkey, more_page=False, additional_logger=None):
    respon = requests.get(url, cookies=cookie_jar)
    dom = bs4.BeautifulSoup(respon.text, features="html.parser")
    form = dom.find('form', {'id': 'form_torrent'})
    try:
        torrents = [re.match(r'.*id=([0-9]*).*?', td.find('a').get('href')).group(1)
                    for td in form.find_all('table', {'class': 'torrentname'})]
        ret = (DOWNLOAD_URL.format(id=x, passkey=passkey) for x in torrents)
        pages = set(BASEURL + x.get('href')
                    for x in form.find('p').find_all('a')) if more_page else None
        return ret, pages
    except Exception as err:
        msg = f"Exception Caught when processing {url}, message: {err}"
        if additional_logger is not None:
            additional_logger.append(msg)
        return [], []


def work_url(url, cookieJar, passkey, additional_logger=None):
    page_0, more_pages_url = get_page_data(
        cookieJar, url.format(0), passkey, True, additional_logger)
    pages = (get_page_data(cookieJar, x, passkey, additional_logger)
             [0] for x in more_pages_url)
    result = set((url for page in chain([page_0], pages) for url in page))
    return result


def get_all_result(baseurl=BASEURL, cookie_jar=COOKIEJAR, passkey=PASSKEY, extended_url=EXTENDED_URL, logger=None):
    result = list(reduce(lambda x, y: x | y, (work_url(
        baseurl + x, cookie_jar, passkey, additional_logger=logger) for x in extended_url)))
    return result

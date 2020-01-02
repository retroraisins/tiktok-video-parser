from threading import Thread
import requests
from lxml import html
import logging
import os
from selenium import webdriver
import sys


logger = logging.getLogger()
TIKITOKS_URL = 'https://tikitoks.com/'
TIKTOK_URL = 'https://www.tiktok.com/'
DOG = '@'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36'
    }

PROXIES = {
    'http': 'http://79.190.145.141:3128',
    'https': 'https://95.79.57.206:53281'
}
LINKS_NOT_FOUND_OR_SERVER_ERR = 'Links videos not found. Or it is possible error on server side. Script stopped'


def download_user_videos(username=None):

    def get_user_video_urls_with_selenium(url):
        driver = webdriver.Chrome()
        driver.get(url, )
        element = driver.find_element_by_link_text('Load more...')
        element.click()
        page = driver.page_source
        tree = html.fromstring(page)
        hrefs = tree.xpath('//a/@href')
        pat = username + '/video'
        user_video_urls = list(filter(lambda x: pat in x, hrefs))
        if len(user_video_urls) == 0:
            sys.exit(LINKS_NOT_FOUND_OR_SERVER_ERR)
        return user_video_urls

    def get_user_video_urls(url):
        try:
            page = requests.get(url, headers=HEADERS, proxies=PROXIES)
        except Exception as e:
            logger.error(e)
        else:
            tree = html.fromstring(page.content)
            hrefs = tree.xpath('//a/@href')

            pat = username + '/video'
            user_video_urls = list(filter(lambda x: pat in x, hrefs))
            if len(user_video_urls) == 0:
                sys.exit('Links videos not found. Or it is possible error on server side. Script stopped')
            return user_video_urls

    if not username:
        logger.warning('Username not found')
    else:
        import time
        t0 = time.clock()
        user_home_page_url = ''.join([TIKITOKS_URL + DOG + username])
        tikitoks_video_urls = get_user_video_urls_with_selenium(user_home_page_url)
        tikitoks_video_ids = list(url.split('/')[-2] for url in tikitoks_video_urls)
        tiktok_video_urls = list(map(
            lambda _id: ''.join([TIKTOK_URL, DOG, username,  '/video/', _id]),
            tikitoks_video_ids))
        put_urls_in_file(tiktok_video_urls)
        threading_requests(tiktok_video_urls, get_video_src)
        logger.info('Exec time: {}'.format(time.clock() - t0))


def get_first_frame(in_filename):
    out_filename = ''.join([in_filename.split('.')[0], '.jpg'])
    ffmpg_cmd = 'ffmpeg -i {} -ss 00:00:00.000 -vframes 1 {}'.format(
        in_filename, out_filename
    )
    os.system(ffmpg_cmd)


def get_video_src(url):
    page = requests.get(url, headers=HEADERS)
    tree = html.fromstring(page.content)
    source = tree.xpath('//video/@src')
    with open('video_src.txt', 'a') as f:
        f.write(source[0])
    download_video(source[0])


def put_urls_in_file(urls):
    with open('video_url.txt', 'w') as f:
        for url in urls:
            print(url, file=f)


def threading_requests(items_to_request, func):
    threads = []
    for item in items_to_request:
        process = Thread(target=func, args=[item])
        process.start()
        threads.append(process)
    for process in threads:
        process.join()


def download_video(url):
    r = requests.get(url)
    logging.info('start downloading from {}'.format(url[0:32]))
    filename = url[24:44] + '.mp4'
    with open(filename, 'wb') as f:
        f.write(r.content)
    get_first_frame(filename)
    logging.info('finished')


tiktok_user = 'egorkreed'
download_user_videos(tiktok_user)


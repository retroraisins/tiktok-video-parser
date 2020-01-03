from threading import Thread
import requests
from lxml import html
import logging
import os
from selenium import webdriver
import sys
from conf import HEADERS, PROXIES, SRC_FILE_PATH, URLS_FILE_PATH, \
    VIDEOS_FILES_PATH, FRAMES_FILES_PATH


logger = logging.getLogger()
TIKITOKS_URL = 'https://tikitoks.com/'
TIKTOK_URL = 'https://www.tiktok.com/'
DOG = '@'

LINKS_NOT_FOUND_OR_SERVER_ERR = 'Links videos not found. Or it is possible ' \
                                'error on server side. Script stopped'


def download_user_videos(username=None):
    def get_links_with_video(driver, url):
        driver.get(url)
        page = driver.page_source
        tree = html.fromstring(page)
        hrefs = tree.xpath('//a/@href')
        pat = username + '/video'
        return list(filter(lambda x: pat in x, hrefs))

    def get_user_video_urls_with_selenium(url):
        driver = webdriver.Chrome()
        user_video_urls = get_links_with_video(driver, url)
        while len(user_video_urls) <= 30:
            element = driver.find_element_by_link_text('Load more...')
            element.click()
            user_video_urls = get_links_with_video(driver, url)
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
                sys.exit(LINKS_NOT_FOUND_OR_SERVER_ERR)
            return user_video_urls

    if not username:
        logger.warning('Username not found')
    else:
        user_home_page_url = ''.join([TIKITOKS_URL + DOG + username])
        tikitoks_video_urls = get_user_video_urls_with_selenium(
            user_home_page_url)
        tikitoks_video_ids = list(url.split('/')[-2] for url in tikitoks_video_urls)
        tiktok_video_urls = list(map(
            lambda _id: ''.join([TIKTOK_URL, DOG, username,  '/video/', _id]),
            tikitoks_video_ids))
        put_urls_in_file(tiktok_video_urls)
        threading_requests(tiktok_video_urls, get_video_src)


def get_first_frame(in_file_path):
    out_filename = ''.join([os.path.basename(in_file_path).split('.')[0], '.jpg'])
    os.makedirs(os.path.dirname(FRAMES_FILES_PATH), exist_ok=True)
    out = ''.join([os.path.abspath(FRAMES_FILES_PATH), '/', out_filename])
    print('frames to:', out)
    ffmpg_cmd = 'ffmpeg -i {} -ss 00:00:00.000 -vframes 1 {}'.format(
        in_file_path, out)
    os.system(ffmpg_cmd)


def get_video_src(url):
    page = requests.get(url, headers=HEADERS)
    tree = html.fromstring(page.content)
    source = tree.xpath('//video/@src')
    os.makedirs(os.path.dirname(SRC_FILE_PATH), exist_ok=True)
    with open(SRC_FILE_PATH, 'a') as f:
        f.write(source[0])
    download_video(source[0])


def put_urls_in_file(urls):
    os.makedirs(os.path.dirname(URLS_FILE_PATH), exist_ok=True)
    with open(URLS_FILE_PATH, 'w') as f:
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
    save_to = VIDEOS_FILES_PATH + filename
    os.makedirs(os.path.dirname(save_to), exist_ok=True)
    with open(save_to, 'wb') as f:
        f.write(r.content)
    get_first_frame(save_to)
    logging.info('finished')


tiktok_user = 'egorkreed'
download_user_videos(tiktok_user)


from threading import Thread
import requests
from lxml import html
import logging
import os
import sys
import json
from conf import HEADERS, PROXIES,  \
    URLS_FILE_PATH, FRAMES_FILES_PATH, \
    VIDEOS_FILES_PATH


logger = logging.getLogger()
TIKITOKS_URL = 'https://tikitoks.com/'
TIKTOK_URL = 'https://www.tiktok.com/'
DOG = '@'

LINKS_NOT_FOUND_OR_SERVER_ERR = 'Links videos not found. Or it is possible ' \
                                'error on server side. Script stopped'


def download_user_videos(username=None):
    result = []

    def get_user_id_from_tree(tree):
        hrefs = tree.xpath('//a/@href')
        pat = '/users/{}'.format(username)
        return list(filter(lambda x: pat in x, hrefs))[0].split('/')[-1]

    def get_video_url_from_tree(tree):
        hrefs = tree.xpath('//a/@href')
        pat = username + '/video'
        return list(filter(lambda x: pat in x, hrefs))

    def get_page_with_load_more(tree):
        data_page = tree.xpath('//a/@data-page')[0]

        user_id = get_user_id_from_tree(tree)
        url = '{}@{}/loadVideos/{}?page={}'.format(TIKITOKS_URL, username,
                                                   user_id, data_page)
        headers = {
            'X-Requested-With': 'XMLHttpRequest'
        }
        resp = requests.get(url, headers=headers)
        import json
        data = json.loads(resp.text)
        return data['html']

    def get_user_video_urls(url):
        try:
            page = requests.get(url, headers=HEADERS)
        except Exception as e:
            logger.error(e)
        else:
            tree = html.fromstring(page.content)
            user_video_urls = get_video_url_from_tree(tree)
            content = get_page_with_load_more(tree)
            tree = html.fromstring(content)
            user_video_urls_2 = get_video_url_from_tree(tree)
            user_video_urls += user_video_urls_2
            if len(user_video_urls) == 0:
                sys.exit(LINKS_NOT_FOUND_OR_SERVER_ERR)
            return user_video_urls

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
        download_video(source[0], url)

    def threading_requests(items_to_request, func):
        threads = []
        for item in items_to_request:
            process = Thread(target=func, args=[item])
            process.start()
            threads.append(process)
        for process in threads:
            process.join()

        return result

    def download_video(src, url):
        BEGIN = 24
        END = 44
        r = requests.get(src)
        logging.info('start downloading from {}'.format(src[0:32]))
        filename = src[BEGIN:END] + '.mp4'
        save_to = VIDEOS_FILES_PATH + filename
        os.makedirs(os.path.dirname(save_to), exist_ok=True)
        with open(save_to, 'wb') as f:
            f.write(r.content)
        result.append({
            'src': src,
            'video_url': url,
            'first_frame_path': save_to,
            'nowatermark_video_url': ''
        })
        get_first_frame(save_to)
        logging.info('finished')

    if not username:
        logger.warning('Username not found')
    else:
        user_home_page_url = ''.join([TIKITOKS_URL + DOG + username])
        tikitoks_video_urls = get_user_video_urls(user_home_page_url)
        tikitoks_video_ids = list(url.split('/')[-2] for url in tikitoks_video_urls)
        tiktok_video_urls = list(map(
            lambda _id: ''.join([TIKTOK_URL, DOG, username,  '/video/', _id]),
            tikitoks_video_ids))
        return threading_requests(tiktok_video_urls, get_video_src)


url = 'https://tiktok.com/@egorkreed/video/6778760522310438150'


def get_no_watermark_video(tiktok_url):
    filename = tiktok_url.split('/')[-1]
    page = requests.get('https://downloadtiktokvideos.com/?' + tiktok_url)
    tree = html.fromstring(page.content)
    source = tree.xpath('//source/@src')
    r = requests.get(source)
    with open(filename, 'wb') as f:
        f.write(r.content)




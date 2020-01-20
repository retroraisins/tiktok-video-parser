from threading import Thread
import requests
from lxml import html
import logging
import os
import sys
import json
from conf import HEADERS, PROXIES, FRAMES_FILES_PATH, \
    VIDEOS_FILES_PATH
from collections import namedtuple
no_watermark_resource = namedtuple('no_watermark_resource',
                                   'resource, url, xpath, request_type, params')




logger = logging.getLogger()
TIKITOKS_URL = 'https://tikitoks.com/'
TIKTOK_URL = 'https://tiktok.com/'
DOG = '@'

LINKS_NOT_FOUND_OR_SERVER_ERR = 'Links videos not found. Or it is possible ' \
                                'error on server side. Script stopped'
USER_NOT_FOUND_ERR = 'Couldn''t find this account'


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

    def load_more_videos(tree):
        data_page = tree.xpath('//a/@data-page')[0]

        user_id = get_user_id_from_tree(tree)
        url = '{}@{}/loadVideos/{}?page={}'.format(TIKITOKS_URL, username,
                                                   user_id, data_page)
        headers = {
            'X-Requested-With': 'XMLHttpRequest'
        }
        resp = requests.get(url, headers=headers)
        data = json.loads(resp.text)
        return data['html']

    def is_user_found(tree):
        page_title = tree.xpath('title')
        page_title = page_title[0]
        if page_title == USER_NOT_FOUND_ERR:
            return False
        return True

    def get_user_video_urls(url):
        page = requests.get(url, headers=HEADERS)
        tree = html.fromstring(page.content)
        user_video_urls = get_video_url_from_tree(tree)
        content = load_more_videos(tree)
        tree = html.fromstring(content)
        user_video_urls += get_video_url_from_tree(tree)
        return user_video_urls

    def get_first_frame(in_file_path):
        out_filename = ''.join([os.path.basename(in_file_path).split('.')[0], '.jpg'])
        os.makedirs(os.path.dirname(FRAMES_FILES_PATH), exist_ok=True)
        out = ''.join([os.path.abspath(FRAMES_FILES_PATH), '/', out_filename])
        print('frames to:', out)
        ffmpg_cmd = 'ffmpeg -i {} -ss 00:00:00.000 -vframes 1 {}'.format(
            in_file_path, out)
        os.system(ffmpg_cmd)

    def get_no_watermark_video_src(url):
        return get_video_src(url)

    def get_video_src(url):
        page = requests.get(url, headers=HEADERS)
        tree = html.fromstring(page.content)
        res = tree.xpath('//video/@src')
        try:
            source = res[0]
        except IndexError:
            return None
        else:
            return source

    def threading_requests(items_to_request, func):
        threads = []
        for item in items_to_request:
            process = Thread(target=func, args=[item])
            process.start()
            threads.append(process)
        for process in threads:
            process.join()

        return result

    def get_video_data(video_id):
        tik_tok_url = ''.join([TIKTOK_URL, DOG, username,  '/video/', video_id])
        data = {
            video_id: {
                'tik_tok_url': tik_tok_url,
                'no_watermark_video_src': get_no_watermarked_video_src(tik_tok_url),
                'watermark_video_src': get_watermarked_video_src(tik_tok_url)
            }
        }
        result.append(data)
        # return data

    def get_no_watermark_video_url_2(tiktok_url):
        headers = HEADERS.copy()
        headers['content-type'] = 'application/x-www-form-urlencoded'
        params = {'url': tiktok_url}
        _url = 'https://www.expertsphp.com/download.php'
        resp = requests.post(_url, data=params, headers=headers)
        if not resp:
            print('No response from {}'.format(_url))
            return None
        tree = html.fromstring(resp.content)
        source = tree.xpath('//source/@src')[0]
        return source

    # _url = 'https://downloadtiktokvideos.com'

    def get_no_watermarked_video_src(tiktok_url):
        tiki_toks_url = tiktok_url.replace(TIKTOK_URL, TIKITOKS_URL)
        resp = requests.get(tiki_toks_url, headers=HEADERS)
        tree = html.fromstring(resp.content)
        try:
            source = tree.xpath('//video/@src')[0]
        except IndexError:
            return None
        else:
            return source

    def get_watermarked_video_src(tiktok_url):
        return get_video_src(tiktok_url)

    def download_video(src):
        BEGIN = 24
        END = 44
        r = requests.get(src)
        filename = src[BEGIN:END] + '.mp4'
        save_to = VIDEOS_FILES_PATH + filename
        os.makedirs(os.path.dirname(save_to), exist_ok=True)
        with open(save_to, 'wb') as f:
            f.write(r.content)
        return save_to

    # def get_tik_tok_video_url(video_id):
    #     return ''.join([TIKTOK_URL, DOG, username, ''])

    def get_video_urls_from_tiki_toks():
        user_home_page_url = ''.join([TIKITOKS_URL + DOG + username])
        return get_user_video_urls(user_home_page_url)

    def get_urls_from_tik_tok():
        pass

    if not username:
        logger.warning('Username not found')
    else:

        urls = get_video_urls_from_tiki_toks()
        video_ids = (url.split('/')[-2] for url in urls)
        return threading_requests(video_ids, get_video_data)


url = 'https://tiktok.com/@egorkreed/video/6778760522310438150'
url_2 = 'https://www.tiktok.com/@egorkreed/video/6778834583266905349'

username = 'egorkreed'
res = download_user_videos(username)
print(json.load(res))
# from pprint import pprint
# pprint(res)


def say_hello_user_tiktok_homepage(user):
    headers = {
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN,zh;q=0.9',
        'pragma': 'no-cache',
        'cache-control': 'no-cache',
        'upgrade-insecure-requests': '1',
        'user-agent': "Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1",
        'cookie': '_ga=GA1.2.451251963.1579009961; _gid=GA1.2.465797066.1579009961'
    }
    response = requests.get(TIKTOK_URL + '@' + user, headers=headers)
    if response:
        return response
    return None


def get_user_data(content):
    tree = html.fromstring(content)
    data = tree.xpath('//*[@id="__NEXT_DATA__"]')[0]
    json_data = json.loads(data.text)
    props = json_data.get('props')
    pageProps = props.get('pageProps')
    return pageProps.get('userData')


def get_user_videos(user):
    response = say_hello_user_tiktok_homepage(user)
    user_data = get_user_data(response.content)
    headers = {
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36'

    }
    params = {
        'secUid': user_data.get('secUid'),
        'id': 6568346904743116806,#user_data.get('userId'),
        'type': 1,
        'count': 30,
        'minCursor': 0,
        'maxCursor': 0,
        'shareUid': '',
        '_signature': 'QNUoGgAgEBnMwKX.LRgSlEDVKQAAB7M'#generate_signature(user_data.get('userId'))
    }
    response = requests.get('https://m.tiktok.com/share/item/list',
                            headers=headers, params=params)

    data = json.loads(response.content)
    body = data.get('body')
    itemsListData = data.get('itemsListData')
    video_identifiers = [item.get('itemInfos').get('id') for item in itemsListData]
    video_urls = [item.get('itemInfos').get('video').get('urls')
                  for item in itemsListData]
    return video_urls

from threading import Thread
import requests
from lxml import html
import logging

import json
from conf import HEADERS, PROXIES, TIKTOK_URL, TIKITOKS_URL
from collections import namedtuple
no_watermark_resource = namedtuple('no_watermark_resource',
                                   'resource, url, xpath, request_type, params')


logger = logging.getLogger()

DOG = '@'

LINKS_NOT_FOUND_OR_SERVER_ERR = 'Links videos not found. Or it is possible ' \
                                'error on server side. Script stopped'
USER_NOT_FOUND_ERR = 'Couldn''t find this account'


class TikTokUserVideoApi:
    def __init__(self, username=None):
        self.username = username
        self._video_data = []

    def _get_user_id_from_tree(self, tree):
        hrefs = tree.xpath('//a/@href')
        pat = '/users/{}'.format(self.username)
        return list(filter(lambda x: pat in x, hrefs))[0].split('/')[-1]

    def _get_video_url_from_tree(self, tree):
        hrefs = tree.xpath('//a/@href')
        pat = self.username + '/video'
        return list(filter(lambda x: pat in x, hrefs))

    def _load_more_videos(self, tree):
        data_page = tree.xpath('//a/@data-page')[0]

        user_id = self._get_user_id_from_tree(tree)
        url = '{}@{}/loadVideos/{}?page={}'.format(TIKITOKS_URL, self.username,
                                                   user_id, data_page)
        headers = {
            'X-Requested-With': 'XMLHttpRequest'
        }
        resp = requests.get(url, headers=headers)
        data = json.loads(resp.text)
        return data['html']

    def _is_user_found(self, tree):
        page_title = tree.xpath('title')
        page_title = page_title[0]
        if page_title == USER_NOT_FOUND_ERR:
            return False
        return True

    def _get_user_video_urls_from_homepege(self, url):
        resp = requests.get(url, headers=HEADERS)
        tree = html.fromstring(resp.content)
        user_video_urls = self._get_video_url_from_tree(tree)
        content = self._load_more_videos(tree)
        tree = html.fromstring(content)
        user_video_urls += self._get_video_url_from_tree(tree)
        return user_video_urls

    def _get_video_src(self, url):
        resp = requests.get(url, headers=HEADERS)
        if resp.status_code == requests.codes.not_found:
            return None
        tree = html.fromstring(resp.content)
        try:
            source = tree.xpath('//video/@src')[0]
        except IndexError:
            return None
        else:
            return source

    def _threading_requests(self, items_to_request, func):
        threads = []
        for item in items_to_request:
            process = Thread(target=func, args=[item])
            process.start()
            threads.append(process)
        for process in threads:
            process.join()

    def _get_video_data(self, video_id):
        tik_tok_url = ''.join([TIKTOK_URL, DOG, self.username, '/video/', video_id])
        data = {
            video_id: {
                'tik_tok_url': tik_tok_url,
                'no_watermark_video_src': self.get_no_watermarked_video_src_2(
                    tik_tok_url),
                'watermark_video_src': self._get_watermarked_video_src(
                    tik_tok_url)
            }
        }
        self._video_data.append(data)

    def _get_watermark_video_url_2(self, tiktok_url):
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

    @staticmethod
    def get_no_watermarked_video_src_2(tiktok_url):
        resp = requests.get(DOWNLOADTIKTOKVIDEOS, params={'url': tiktok_url})
        tree = html.fromstring(resp.content)
        try:
            source = tree.xpath('//source/@src')[0]
        except IndexError:
            return None
        else:
            return source

    @staticmethod
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

    def _get_watermarked_video_src(self, tiktok_url):
        return self._get_video_src(tiktok_url)

    def _get_video_urls_from_tiki_toks(self):
        user_home_page_url = ''.join([TIKITOKS_URL + DOG + self.username])
        return self._get_user_video_urls_from_homepege(user_home_page_url)

    @property
    def video_data(self):
        if not self.username:
            logger.warning('Username not found')
        else:
            urls = self._get_video_urls_from_tiki_toks()
            video_ids = (url.split('/')[-2] for url in urls)
            self._threading_requests(video_ids, self._get_video_data)
            return self._video_data

from threading import Thread
import requests
from requests import HTTPError
from lxml import html
import logging
import re
import json
from conf import HEADERS, PROXIES, TIKTOK_URL, TIKITOKS_URL, \
    EXPERTSPHP
from collections import namedtuple
no_watermark_resource = namedtuple('no_watermark_resource',
                                   'resource, url, xpath, request_type, params')


logger = logging.getLogger()

DOG = '@'

LINKS_NOT_FOUND_OR_SERVER_ERR = 'Links videos not found. Or it is possible ' \
                                'error on server side. Script stopped'
USER_NOT_FOUND_ERR = 'Couldn''t find this account'


class TikTokUserVideoApi:
    def __init__(self, username=None, proxies=None):
        self.username = username
        self._video_data = []
        self._proxies = proxies

    def _get_user_id_from_tree(self, tree):
        hrefs = tree.xpath('//a/@href')
        pat = '/users/{}'.format(self.username)
        return list(filter(lambda x: pat in x, hrefs))[0].split('/')[-1]

    def _get_video_url_from_tree(self, tree):
        hrefs = tree.xpath('//a/@href')
        pat = self.username.lstrip('@') + '/video'
        return list(filter(lambda x: pat in x, hrefs))

    def _load_more_videos(self, tree):
        try:
            data_page = tree.xpath('//a/@data-page')[0]

            user_id = self._get_user_id_from_tree(tree)
            url = '{}@{}/loadVideos/{}?page={}'.format(TIKITOKS_URL, self.username,
                                                       user_id, data_page)
            headers = {
                'X-Requested-With': 'XMLHttpRequest'
            }
            resp = requests.get(url, headers=headers, verify=False)
            resp.raise_for_status()
            data = json.loads(resp.text)
        except Exception as e:
            return ''
        else:
            return data['html']

    def _get_user_video_urls_from_homepege(self, url):
        resp = requests.get(url, headers=HEADERS, verify=False)
        if not resp:
            return None
        tree = html.fromstring(resp.content)
        user_video_urls = self._get_video_url_from_tree(tree)
        if user_video_urls:
            content = self._load_more_videos(tree)
            if content:
                tree = html.fromstring(content)
                user_video_urls += self._get_video_url_from_tree(tree)
            return user_video_urls
        else:
            return None

    def _get_video_src(self, url):
        resp = requests.get(url, headers=HEADERS, verify=False)
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
        tik_tok_url = ''.join([TIKTOK_URL, self.username, '/video/', video_id])
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
        if not TikTokUserVideoApi.validate_tik_tok_url(tiktok_url) or \
                not TikTokUserVideoApi.is_exist(TikTokUserVideoApi.get_username_from_url(tiktok_url)):
            return None
        try:
            resp = requests.post(EXPERTSPHP, data={'url': tiktok_url})
            resp.raise_for_status()
            tree = html.fromstring(resp.content)
            source = tree.xpath("//a[text()='Download Link']/@href")[0]
        except IndexError:
            return None
        except HTTPError as err:
            raise err
        else:
            return source


    @staticmethod
    def get_username_from_url(tiktok_url):
        res = re.search('https://www.tiktok.com/(@\w+)/video/\d+', tiktok_url)
        if res:
            return res.group(1)
        return None

    @staticmethod
    def validate_tik_tok_url(tiktok_url):
        return bool(re.fullmatch(r'https://www.tiktok.com/@\w+/video/\d{19}', tiktok_url))


    @staticmethod
    def is_exist(username):
        tik_tok_user_url = ''.join([TIKTOK_URL, username])
        resp = requests.get(tik_tok_user_url, headers=HEADERS, verify=False)
        if resp.status_code == 404:
            return False
        return True


    @staticmethod
    def get_no_watermarked_video_src(tiktok_url):
        if not TikTokUserVideoApi.validate_tik_tok_url(tiktok_url) or \
                not TikTokUserVideoApi.is_exist(TikTokUserVideoApi.get_username_from_url(tiktok_url)):
            return None
        try:
            tiki_toks_url = tiktok_url.replace('tiktok.com', 'tikitoks.com')
            resp = requests.get(tiki_toks_url, headers=HEADERS, verify=False)
            resp.raise_for_status()
            tree = html.fromstring(resp.content)
            source = tree.xpath('//video/@src')[0]
        except IndexError as e:
            return None
        except requests.exceptions.ConnectionError:
            return None
        else:
            return source

    def _get_watermarked_video_src(self, tiktok_url):
        return self._get_video_src(tiktok_url)

    def _get_video_urls_from_tiki_toks(self):
        user_home_page_url = ''.join([TIKITOKS_URL + self.username])
        if not requests.get(user_home_page_url, verify=False):
            return None
        return self._get_user_video_urls_from_homepege(user_home_page_url)

    @property
    def video_data(self):
        try:
            if not self.username or not TikTokUserVideoApi.is_exist(self.username):
                logger.warning('Username not found')
                return None
            else:
                urls = self._get_video_urls_from_tiki_toks()
                if urls:
                    video_ids = (url.split('/')[-2] for url in urls)
                    self._threading_requests(video_ids, self._get_video_data)
                    return self._video_data
                return None
        except requests.exceptions.HTTPError:
            raise

# from threading import Thread
from conf import HEADERS, PAYLOAD
import requests
import json
import re
import logging


logger = logging.getLogger()
ERROR = 'Count can''t be negative'
tiktok_url = 'https://tikitoks.com/'


def download_user_videos(username=None):
    def get_user_video_urls():
        try:
            content = requests.post("https://tikitoks.com/@" + username,
                                    data=json.dumps(PAYLOAD),
                                    headers=HEADERS).content
        except Exception as e:
            logger.error(e)
        else:
            return map(str, re.findall(b'/video/[0-9]+', content))
    if not username:
        logger.warning('Username not found')
    else:
        for url in get_user_video_urls():
            download_video(url)

    # if 1 < video_cn <= VIDEOS_COUNT:
    #     for _ in range(video_cn):
    #         create_downloading_thread()
    # else:
    #     print(ERROR)


def download_video(url):
    # import urllib.request
    full_url = ''.join([tiktok_url, '@', tiktok_user, url])

    # urllib.request.urlretrieve(full_url, '{}.mp4'.format(url[-19:]))
    with open(full_url, 'wb')


def create_downloading_thread():
    pass
    # thread = Thread(download_video, args=())


tiktok_user = 'egorkreed'
download_user_videos(tiktok_user)

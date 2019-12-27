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
    if not username:
        print('Username not found')
    else:
        user_homepage_url = ''.join([tiktok_url, '@', username])
        try:
            content = requests.post("https://tikitoks.com/@" + username,
                                    data=json.dumps(PAYLOAD),
                                    headers=HEADERS).content
        except Exception as e:
            logger.error(e)
        else:

            video_pattern = re.compile(b'/video/[0-9]+')
            user_videos = re.findall(video_pattern, content)
            print('Videos count: {}'.format(len(user_videos)))

    # if 1 < video_cn <= VIDEOS_COUNT:
    #     for _ in range(video_cn):
    #         create_downloading_thread()
    # else:
    #     print(ERROR)


def download_video():
    pass


def create_downloading_thread():
    pass
    # thread = Thread(download_video, args=())


tiktok_user = 'egorkreed'
download_user_videos(tiktok_user)

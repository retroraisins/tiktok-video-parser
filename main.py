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
            text = requests.post("https://tikitoks.com/@" + username,
                                 data=json.dumps(PAYLOAD),
                                 headers=HEADERS).text
        except Exception as e:
            logger.error(e)
        else:
            urls = re.findall('https://tikitoks.com/.+/video/[0-9]+', text)
            put_urls_in_file(urls)
            return urls[0:3]
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


def put_urls_in_file(urls):
    with open('video_url.txt', 'w') as f:
        for url in urls:
            print(url, file=f)


def download_video(url):
    resp = requests.get(url).text
    video_src = re.search
    match = re.search(r'\d+', url)
    if match:
        filename = ''.join([match.group(0), '.mp4'])
        logging.warning('start downloading from {}'.format(url))
        with open(filename, 'wb') as f:
            f.write(resp.content)
        logging.warning('finished')


def create_downloading_thread():
    pass
    # thread = Thread(download_video, args=())


tiktok_user = 'egorkreed'
download_user_videos(tiktok_user)

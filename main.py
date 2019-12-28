import requests
from lxml import html
import logging


logger = logging.getLogger()
ERROR = 'Count can''t be negative'
TIKTOK_URL = 'https://tikitoks.com/'
DOG = '@'


def download_user_videos(username=None):
    def get_user_video_urls():
        try:
            url = ''.join([TIKTOK_URL + DOG + username])
            page = requests.get(url)
        except Exception as e:
            logger.error(e)
        else:
            tree = html.fromstring(page.content)
            hrefs = tree.xpath('//a/@href')
            pat = username + '/video'
            return filter(lambda x: pat in x, hrefs)

    if not username:
        logger.warning('Username not found')
    else:
        for url in get_user_video_urls():
            download_video(url)

    def get_video_src(url):
        page = requests.get(url)
        tree = html.fromstring(page.content)
        source = tree.xpath('//video/@src')
        return source[0]

    
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

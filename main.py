from threading import Thread
import requests
from lxml import html
import logging
from selenium import webdriver


logger = logging.getLogger()
ERROR = 'Count can''t be negative'
TIKTOK_URL = 'https://tikitoks.com/'
DOG = '@'


def download_user_videos(username=None):

    def get_more_videos_from_homepage(url):
        driver = webdriver.Firefox()
        driver.get(url)
        buttons = driver.find_elements_by_xpath('//a/@href="#"/')

        buttons[-1].click()

    def get_user_video_urls(url):
        try:

            page = requests.get(url)
        except Exception as e:
            logger.error(e)
        else:
            tree = html.fromstring(page.content)
            hrefs = tree.xpath('//a/@href')
            pat = username + '/video'
            return filter(lambda x: pat in x, hrefs)

    def threading_requests(urls):
        threads = []
        for url in urls:
            process = Thread(target=download_video, args=[url])
            process.start()
            threads.append(process)
        # We now pause execution on the main thread by 'joining' all of our started threads.
        # This ensures that each has finished processing the urls.
        for process in threads:
            process.join()

    if not username:
        logger.warning('Username not found')
    else:
        import time
        t0 = time.clock()
        user_home_page_url = ''.join([TIKTOK_URL + DOG + username])
        # get_more_videos_from_homepage(user_home_page_url)
        urls_data = get_user_video_urls(user_home_page_url)
        threading_requests(urls_data)
        logger.info('Exec time: {}'.format(time.clock() - t0))


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
    file_name = url.split('/')[-2]
    r = requests.get(get_video_src(url))
    logging.warning('start downloading from {}'.format(url))
    with open(file_name + '.mp4', 'wb') as f:
        f.write(r.content)
    logging.warning('finished')


def create_downloading_thread():
    pass


tiktok_user = 'egorkreed'
download_user_videos(tiktok_user)

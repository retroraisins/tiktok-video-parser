from threading import Thread
import requests
from lxml import html
import logging
import ffmpeg
import re
from selenium import webdriver
from selenium.webdriver.common.by import By


logger = logging.getLogger()
ERROR = 'Count can''t be negative'
TIKITOKS_URL = 'https://tikitoks.com/'
TIKTOK_URL = 'https://www.tiktok.com/'
DOG = '@'
CHROME_PROFILE_LOCATION = '/Users/RRustam/Library/Application Support/Google/Chrome/'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36'
    }


def test_msedge_driver():
    import time

    driver = webdriver.Edge()  # Optional argument, if not specified will search path.
    driver.get('http://www.google.com/')
    time.sleep(5)  # Let the user actually see something!
    search_box = driver.find_element_by_name('q')
    search_box.send_keys('EdgeDriver')
    search_box.submit()
    time.sleep(5)  # Let the user actually see something!
    driver.quit()


def test_chrome_driver():
    import time

    driver = webdriver.Chrome()  # Optional argument, if not specified will search path.
    driver.get('http://www.google.com/')
    time.sleep(5)  # Let the user actually see something!
    search_box = driver.find_element_by_name('q')
    search_box.send_keys('ChromeDriver')
    search_box.submit()
    time.sleep(5)  # Let the user actually see something!
    driver.quit()


def download_user_videos(username=None):
    def get_chrome_profile():
        options = webdriver.ChromeOptions()
        options.add_argument('--user-data-dir={}'.format(CHROME_PROFILE_LOCATION))
        return options

    def get_user_video_urls_with_selenium(url):
        options = get_chrome_profile()
        driver = webdriver.Chrome(options=options)
        driver.get(url)
        page = driver.page_source
        tree = html.fromstring(page)
        hrefs = tree.xpath('//a/@href')
        if len(hrefs) == 0:
            raise Exception('links on videos not found')
        pat = username + '/video'
        return filter(lambda x: pat in x, hrefs)

    def get_user_video_urls(url):
        try:

            page = requests.get(url, headers=HEADERS)
        except Exception as e:
            logger.error(e)
        else:
            tree = html.fromstring(page.content)
            hrefs = tree.xpath('//a/@href')
            if len(hrefs) == 0:
                raise Exception('links on videos not found')
            pat = username + '/video'
            return filter(lambda x: pat in x, hrefs)

    if not username:
        logger.warning('Username not found')
    else:
        import time
        t0 = time.clock()
        user_home_page_url = ''.join([TIKITOKS_URL + DOG + username])
        tikitoks_video_urls = get_user_video_urls(user_home_page_url)
        tikitoks_video_ids = (url.split('/')[-2] for url in tikitoks_video_urls)
        tiktok_video_urls = list(map(
            lambda _id: ''.join([TIKTOK_URL, DOG, username,  '/video/', _id]),
            tikitoks_video_ids))
        threading_requests(tiktok_video_urls, get_video_src)
        logger.info('Exec time: {}'.format(time.clock() - t0))


def read_frame_as_jpeg(filename, frame_num=1):
    # import ffmpeg as ffmpeg
    out, err = (
        ffmpeg
        .input(filename)
        .filter('select', 'gte(n,{})'.format(frame_num))
        .output('pipe:', vframes=1, format='image2', vcodec='mjpeg')
        .run(capture_stdout=True)
    )
    return out


# def get_video_frame(path, frame_num=1):
#     import os
#     os.system('ffmpeg -i {} -ss 00:00:00.000 -vframes 1 thumb1.jpg'.format(path))


def get_video_src(url):
    page = requests.get(url, headers=HEADERS)
    tree = html.fromstring(page.content)
    source = tree.xpath('//video/@src')
    print(source[0])
    download_video(source[0])


def put_urls_in_file(urls):
    with open('video_url.txt', 'w') as f:
        for url in urls:
            print(url, file=f)


def threading_requests(items_to_request, func):
    threads = []
    for item in items_to_request:
        process = Thread(target=func, args=[item])
        process.start()
        threads.append(process)
    # We now pause execution on the main thread by 'joining' all of our started threads.
    # This ensures that each has finished processing the urls.
    for process in threads:
        process.join()


def download_video(url):
    r = requests.get(url)
    logging.warning('start downloading from {}'.format(url[0:32]))
    with open(url[24:44] + '.mp4', 'wb') as f:
        f.write(r.content)
    logging.warning('finished')


def get_video_id_from(url):
    id = re.search(r'\d+', url)
    return id

def create_downloading_thread():
    pass


tiktok_user = 'egorkreed'
download_user_videos(tiktok_user)

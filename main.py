import os
from threading import Thread
import requests
from lxml import html
import logging
import ffmpeg
from selenium import webdriver


logger = logging.getLogger()
ERROR = 'Count can''t be negative'
TIKITOKS_URL = 'https://tikitoks.com/'
TIKTOK_URL = 'https://www.tiktok.com/'
DOG = '@'


def test_chrome_driver():
    import time

    driver = webdriver.Chrome()  # Optional argument, if not specified will search path.
    driver.get('http://www.google.com/');
    time.sleep(5)  # Let the user actually see something!
    search_box = driver.find_element_by_name('q')
    search_box.send_keys('ChromeDriver')
    search_box.submit()
    time.sleep(5)  # Let the user actually see something!
    driver.quit()


def download_user_videos(username=None):

    def get_home_page_with_webdriver(url):
        driver = webdriver.Firefox()
        driver.get(url)
        buttons = driver.find_elements_by_xpath('//a/@href="#"/')

        buttons[-1].click()

    def get_user_video_urls(url):
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36'
            }

            page = requests.get(url, headers=headers)
        except Exception as e:
            logger.error(e)
        else:
            tree = html.fromstring(page.content)
            hrefs = tree.xpath('//a/@href')
            if len(hrefs) == 0:
                raise Exception('links on videos not found')
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
test_chrome_driver()
# filename = '/Users/RRustam/tiktok-video-parser/6720911711047650565.mp4'
# download_user_videos(tiktok_user)
# read_frame_as_jpeg(filename)

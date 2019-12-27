from threading import Thread
from conf import VIDEOS_COUNT

ERROR = 'Count can''t be negative'


def download_user_videos(username=None, video_cn=VIDEOS_COUNT):
    if 1 < video_cn <= VIDEOS_COUNT:
        for _ in range(video_cn):
            create_downloading_thread()
    else:
        print(ERROR)


def download_video():
    pass


def create_downloading_thread():
    thread = Thread(download_video, args=())

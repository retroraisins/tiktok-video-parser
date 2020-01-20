from conf import HEADERS, PROXIES, FRAMES_FILES_PATH, VIDEOS_FILES_PATH
import os
import requests


def get_first_frame(in_file_path):
    out_filename = ''.join([os.path.basename(in_file_path).split('.')[0], '.jpg'])
    os.makedirs(os.path.dirname(FRAMES_FILES_PATH), exist_ok=True)
    out = ''.join([os.path.abspath(FRAMES_FILES_PATH), '/', out_filename])
    print('frames to:', out)
    ffmpg_cmd = 'ffmpeg -i {} -ss 00:00:00.000 -vframes 1 {}'.format(
        in_file_path, out)
    os.system(ffmpg_cmd)


def download_video(src):
    BEGIN = 24
    END = 44
    r = requests.get(src)
    filename = src[BEGIN:END] + '.mp4'
    save_to = VIDEOS_FILES_PATH + filename
    os.makedirs(os.path.dirname(save_to), exist_ok=True)
    with open(save_to, 'wb') as f:
        f.write(r.content)
    return save_to
# tiktok-video-parser

# 1. Создать виртуальное окружение(опционально):
  создать виртуальное окружение:
`virtualenv --python=python3.6 venv`  
# 2. Установить зависимости
`pip install -r requirements.txt`


# 3. Запуск
  Импортировать метод `download_user_videos`
  Передать на вход методу tiktok логин юзера `download_user_videos(username)`
# 4.Настройки
  в файл conf.py можно задать проки(PROXY) и относительные пути куда сохранять urls видео, sources видео,
  папку для сохранения загруженных видео и фреймов
  по умолчанию установленые следующие пути:
```
  SRC_FILE_PATH = './sources/video_src.txt'`
  URLS_FILE_PATH = './urls/video_urls.txt'
  VIDEOS_FILES_PATH = './videos/'
  FRAMES_FILES_PATH = 'frames/'
```  

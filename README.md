# tiktok-video-parser

# 1. Создать виртуальное окружение(опционально):
  создать виртуальное окружение:
`virtualenv --python=python3.6 venv`  
# 2. Установить зависимости
`pip install -r requirements.txt`


# 3. Использованпие
  создать экземпляр класс `TikTokUserVideoApi`
```
    #python
    user_api = TikTokUserVideoApi('egorkreed')
    data = user_api.video_data
```
  
# 4.Настройки
  в файл conf.py можно задать проки(PROXY) и относительные пути куда сохранять загруженные видео и фреймы
  по умолчанию установленые следующие пути:
```
  VIDEOS_FILES_PATH = './videos/'
  FRAMES_FILES_PATH = 'frames/'
```  

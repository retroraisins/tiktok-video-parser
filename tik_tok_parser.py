def say_hello_user_tiktok_homepage(user):
    headers = {
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN,zh;q=0.9',
        'pragma': 'no-cache',
        'cache-control': 'no-cache',
        'upgrade-insecure-requests': '1',
        'user-agent': "Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1",
        'cookie': '_ga=GA1.2.451251963.1579009961; _gid=GA1.2.465797066.1579009961'
    }
    response = requests.get(TIKTOK_URL + '@' + user, headers=headers)
    if response:
        return response
    return None


def get_user_data(content):
    tree = html.fromstring(content)
    data = tree.xpath('//*[@id="__NEXT_DATA__"]')[0]
    json_data = json.loads(data.text)
    props = json_data.get('props')
    pageProps = props.get('pageProps')
    return pageProps.get('userData')


def get_user_videos(user):
    response = say_hello_user_tiktok_homepage(user)
    user_data = get_user_data(response.content)
    headers = {
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36'

    }
    params = {
        'secUid': user_data.get('secUid'),
        'id': 6568346904743116806,#user_data.get('userId'),
        'type': 1,
        'count': 30,
        'minCursor': 0,
        'maxCursor': 0,
        'shareUid': '',
        '_signature': 'QNUoGgAgEBnMwKX.LRgSlEDVKQAAB7M'#generate_signature(user_data.get('userId'))
    }
    response = requests.get('https://m.tiktok.com/share/item/list',
                            headers=headers, params=params)

    data = json.loads(response.content)
    body = data.get('body')
    itemsListData = data.get('itemsListData')
    video_identifiers = [item.get('itemInfos').get('id') for item in itemsListData]
    video_urls = [item.get('itemInfos').get('video').get('urls')
                  for item in itemsListData]
    return video_urls

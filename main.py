from urllib.parse import quote
import requests as r
from parsel import Selector
import re
from os import makedirs
from os.path import exists


def get_song_name(str):
    pattern = r'title=\"(.*?)\">'
    result = re.search(re.compile(pattern, re.S), str)
    if result == None:
        print('Error matching song name\n')
        return
    else:
        return result.group(1)


def get_search_url(name):
    base_url = 'https://www.kumeiwp.com/index/search/data?page=1&limit=50&word='
    tail_url = '&scope=all'
    url = base_url + quote(name) + tail_url
    return url


def get_songs_data(url):
    result = r.get(url, headers=headers, proxies=proxy)
    dict = result.json()
    if len(dict['data']) == 0:
        print('No result matching search\n')
        return []
    dict['data'][0]['file_id']
    songs_data = []
    for item in dict['data']:
        songs_data.append([item['file_id'], item['file_downs'], item['title']])
    sorted_songs_data = sorted(songs_data, key=lambda x: x[1], reverse=True)

    return sorted_songs_data


def get_song_detail_url(file_id):
    song_detail_url = f'https://www.kumeiwp.com/file/{file_id}.html'

    return song_detail_url


def get_download_link(detail_url):
    song_detail = r.get(detail_url, headers=headers, proxies=proxy)
    selector = Selector(text=song_detail.text)
    download_url = selector.xpath(
        '/html/body/div[2]/div[6]/div[2]/div[1]/div/div[1]/div/div[2]/div[6]/a[1]/@href').get()

    return download_url


def download_audio(url, name):
    RESULT_DIR = 'Audios'
    exists(RESULT_DIR) or makedirs(RESULT_DIR)
    audio = r.get(url, stream=True)
    with open(f'Audios/{name}.mp3', 'wb') as f:
        f.write(audio.content)
        f.flush()


headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}
proxy = {
    'https': 'http://127.0.0.1:33210',
    'http': 'http://127.0.0.1:33210'
}
if __name__ == '__main__':
    with open('songs.txt', 'r', encoding='utf-8') as f:
        songs = [line.strip() for line in f.readlines()]
    songs = list(filter(lambda name: name != '', songs))
    print(f'Read {len(songs)} songs in file')

    for name in songs:
        search_url = get_search_url(name)
        songs_data = get_songs_data(search_url)
        print(f'scraping {name}, {len(songs_data)} results found')
        cnt = len(songs_data)
        if cnt == 0:
            continue
        else:
            print(f'Top results:')
            for i in range(0, min(3, cnt)):
                print(f'{i}.{get_song_name(songs_data[i][2])}')
        choice = int(input())
        if choice > 2:
            continue
        else:
            song_id = songs_data[choice][0]
            song_name = get_song_name(songs_data[choice][2])
            song_detail_url = get_song_detail_url(song_id)
            download_link = get_download_link(song_detail_url)
            download_audio(download_link, song_name)
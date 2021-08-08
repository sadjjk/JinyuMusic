import requests
from datetime import datetime


class QingtingFM:
    title = '蜻蜓FM'

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36'
        }

    def get_all_categories(self):
        target_url = 'https://rapi.qingting.fm/categories?type=channel'
        response = requests.get(target_url, headers=self.headers)
        response.raise_for_status()
        response_json = response.json()
        data = [{'name': cate.get('id'),
                 'title': cate.get('title')} for cate in response_json.get('Data')[:11]]

        return data

    def get_categories_radio(self, categories_id=433):
        target_url = f'https://webapi.qingting.fm/api/mobile/radiopage/list/{categories_id}'
        response = requests.get(target_url, headers=self.headers)
        response.raise_for_status()
        response_json = response.json()

        radio_list = [{'id': radio.get('content_id'),
                       'img_url': radio.get('cover'),
                       'title': radio.get('title'),
                       'platform': self.__class__.__name__} for radio in response_json.get('radioList')]
        return radio_list

    def get_radio_detail(self, radio_id):
        target_url = f'https://webapi.qingting.fm/api/pc/radio/{radio_id}'
        response = requests.get(target_url, headers=self.headers)
        response.raise_for_status()
        response_json = response.json()

        radio_info = response_json.get('album')
        source_url = f'https://www.qingting.fm/radios/{radio_id}'
        img_url = radio_info.get('cover')
        title = radio_info.get('title')
        tags = [radio_info.get('top_category_title', '')]
        create_time = radio_info.get('update_time').split(' ')[0]
        description = radio_info.get('description')
        first_key_name = list(response_json.get('pList').keys())[0]
        song_list = [{'song_id': f'{radio_id}_{datetime.now().strftime("%Y%m%d")}_' +
                                 f'{song.get("start_time").replace(":", "")}_' +
                                 f'{song.get("end_time").replace(":", "")}'
                                 f'_24_0',
                      'album': title,
                      'album_id': radio_id,
                      'img_url': img_url,
                      'title': song.get('title'),
                      'source_url': source_url,
                      'start_time': song.get('start_time'),
                      'platform': self.__class__.__name__,
                      'platform_name': self.__class__.title
                      } for song in response_json.get('pList').get(first_key_name)
                     if song.get('end_time') < datetime.now().strftime("%H:%M:%S")]

        now_play_song = {
            'song_id': f'live/{radio_id}/64k',
            'album': title,
            'album_id': radio_id,
            'img_url': img_url,
            'title': radio_info.get('nowplaying').get('title'),
            'source_url': source_url,
            'start_time': radio_info.get('nowplaying').get('start_time'),
            'platform': self.__class__.__name__,
            'platform_name': self.__class__.title

        }

        song_list.append(now_play_song)

        song_list = song_list[::-1]

        return {
            'source_url': source_url,
            'radio_id': radio_id,
            'img_url': img_url,
            'title': title,
            'tags': tags,
            'description': description,
            'create_time': create_time,
            'song_list': song_list,
            'song_total': len(song_list),
            'platform': self.__class__.__name__
        }

    def get_song_play_url(self, song_id):

        if 'live' in song_id:

            play_url = f'https://lhttp.qingting.fm/{song_id}.mp3'

        else:
            song_info_list = song_id.split('_')
            radio_id = song_info_list[0]
            cur_date = song_info_list[1]
            play_url = f'https://lcache.qingting.fm/cache/{cur_date}/{radio_id}/{song_id}.aac'

        return {'platform': self.__class__.__name__,
                'play_url': play_url}

    def get_song_lyric(self, song_id):
        lyric = '暂无歌词'
        return {'platform': self.__class__.__name__,
                'lyric': lyric}


if __name__ == '__main__':
    qing = QingtingFM()
    # qing.get_all_categories()
    qing.get_radio_detail(387)

    qing.get_song_play_url('387_20210807_030000_040000_24_0')

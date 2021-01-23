from Crypto.Cipher import AES
from Music.platforms import BaseMusic
import requests
import random
import base64
import codecs
import math
import json
import time
import re


class NeteaseMusic(BaseMusic):
    title = '网易云音乐'

    def __init__(self):
        super(NeteaseMusic, self).__init__()
        self.headers['Referer'] = 'https://music.163.com/'
        self.headers['Host'] = 'music.163.com'

    def _create_secret_key(self, size):
        string = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        random_string = ""
        for i in range(0, size):
            random_string = random_string + string[math.floor(random.random() * len(string))]
        return random_string

    def _aes_encrypt(self, text, sec_key='0CoJUm6Qyw8W8jud'):
        sec_key = sec_key.encode('utf-8')
        iv = '0102030405060708'.encode('utf-8')
        cryptor = AES.new(sec_key, AES.MODE_CBC, iv)

        pad = 16 - len(text.encode('utf-8')) % 16
        text = text + pad * chr(pad)

        cipher_text = cryptor.encrypt(text.encode('utf-8'))

        return base64.b64encode(cipher_text).decode('utf-8')

    def _rsa_encrypt(self, text):
        modulus = '00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b72' \
                  '5152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbd' \
                  'a92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe48' \
                  '75d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7'
        key = '010001'
        text = text[::-1]
        rs = int(codecs.encode(text.encode('utf-8'), 'hex'), 16) ** int(key, 16) % int(modulus, 16)
        return format(rs, 'x').zfill(256)

    def _encrypted_request(self, text):
        text = json.dumps(text, separators=(',', ':'))
        sec_key = self._create_secret_key(16)
        enc_text = self._aes_encrypt(self._aes_encrypt(text), sec_key)
        enc_sec_key = self._rsa_encrypt(sec_key)
        data = {
            'csrf_token': '',
            'params': enc_text,
            'encSecKey': enc_sec_key
        }

        return data

    def _is_playable(self, fee):
        return fee not in (0, 1, 4)

    # 获取歌曲详情
    def _get_song_detail(self, song_ids):
        '''
        获取歌曲详情内容 可批量获取多首
        :param song_id: list or str
        :return: list 返回每首歌的歌曲详情内容
        '''
        target_url = 'https://music.163.com/weapi/v3/song/detail'

        song_ids = song_ids if isinstance(song_ids, list) else [song_ids]  # 单首传str 多首传list

        data = {
            "c": '[' + ','.join([f'{{"id":{id}}}' for id in song_ids]) + ']',
            "ids": '[' + ','.join([str(id) for id in song_ids]) + ']'
        }

        params_dict = self._encrypted_request(data)

        response = requests.post(target_url,
                                 data=params_dict,
                                 headers=self.headers)

        response.raise_for_status()
        song_detail_info = response.json()

        assert song_detail_info.get('code') == 200, '网易云音乐获取歌曲详情失败!请求地址:{}\n请求参数:{}\n返回结果:{}'.format(target_url, data,response.text)
        song_detail_info = song_detail_info.get('songs')

        return [
            {'song_id': item.get('id'),
             'title': item.get('name'),
             'artist': item.get('ar')[0].get('name'),
             'artist_id': item.get('ar')[0].get('id'),
             'album': item.get('al').get('name'),
             'album_id': item.get('al').get('id'),
             'img_url': item.get('al').get('picUrl'),
             'source_url': 'https://music.163.com/#/song?id={}'.format(item.get('id')),
             'platform': self.__class__.__name__,
             'platform_name': self.__class__.title
             }
            for item in song_detail_info if self._is_playable(item.get('fee'))
        ]

    # 获取歌曲播放地址
    def get_song_play_url(self, song_id):
        '''
        获取歌曲播放地址
        :param song_id: ID
        :return: 返回歌曲播放地址
        '''
        target_url = 'http://music.163.com/weapi/song/enhance/player/url/v1'

        data = {
            "ids": [str(song_id)],
            "level": "standard",
            "encodeType": "aac",
            "csrf_token": ""
        }

        params_dict = self._encrypted_request(data)
        response = requests.post(target_url,
                                 data=params_dict,
                                 headers=self.headers)

        response.raise_for_status()
        song_info = response.json()
        assert song_info.get('code') == 200, '网易云音乐播放地址获取失败!请求地址:{}\n请求参数:{}\n返回结果:{}'.format(target_url, data,response.text)
        play_url = song_info['data'][0].get('url')
        assert play_url, '版权原因 暂无法播放 请更换其他平台'
        return {'platform': self.__class__.__name__,
                'play_url': play_url}

    # 获取歌曲歌词
    def get_song_lyric(self, song_id):
        '''
        获取歌曲歌词
        :param song_id: 歌曲ID
        :return: 歌词
        '''
        target_url = 'http://music.163.com/api/song/lyric?id={}&lv=-1&kv=-1&tv=-1'.format(song_id)

        response = requests.get(target_url,
                                headers=self.headers)

        response.raise_for_status()
        lyric_info = response.json()

        assert lyric_info.get('code') == 200, '网易云音乐获取歌词失败!请求地址:{}\n请求参数:{}\n返回结果:{}'.format(target_url, '',response.text)

        lyric_detail = lyric_info.get('lrc')
        if lyric_detail:
            lyric = lyric_detail.get('lyric')
        else:
            lyric = ''

        return {'platform': self.__class__.__name__,
                'lyric': lyric}

    # 获取歌手详情
    def get_artist_detail(self, artist_id):
        target_url = f'http://music.163.com/api/artist/{artist_id}'

        response = requests.get(target_url,
                                headers=self.headers)

        response.raise_for_status()
        response_json = response.json()

        assert response_json.get('code') == 200, '网易云音乐歌手详情获取失败!请求地址:{}\n请求参数:{}\n返回结果:{}'.format(target_url, '',response.text)

        artist_info = response_json.get('artist')

        source_url = f'https://music.163.com/#/artist?id={artist_id}'
        img_url = artist_info.get('picUrl')
        title = artist_info.get('name')

        song_list = [
            {'song_id': song.get('id'),
             'title': song.get('name'),
             'artist': song.get('artists')[0].get('name'),
             'artist_id': song.get('artists')[0].get('id'),
             'album': song.get('album').get('name'),
             'album_id': song.get('album').get('id'),
             'img_url': song.get('album').get('picUrl'),
             'source_url': 'https://music.163.com/#/song?id={}'.format(song.get('id')),
             'platform': self.__class__.__name__,
             'platform_name': self.__class__.title
             } for song in response_json.get('hotSongs') if self._is_playable(song.get('fee'))
        ]

        return {
            'source_url': source_url,
            'artist_id': artist_id,
            'img_url': img_url,
            'title': title,
            'song_list': song_list,
            'platform': self.__class__.__name__,
            'song_total': len(song_list)
        }

    # 获取专辑详情
    def get_album_detail(self, album_id):
        '''
        获取专辑详情内容
        :param album_id: 专辑id
        :return: dict 返回专辑详情内容
        '''
        target_url = 'http://music.163.com/api/album/{}'.format(album_id)

        response = requests.get(target_url,
                                headers=self.headers)

        response.raise_for_status()
        response_json = response.json()

        assert response_json.get('code') == 200, '网易云音乐专辑详情获取失败!请求地址:{}\n请求参数:{}\n返回结果:{}'.format(target_url, '',response.text)

        album_info = response_json.get('album')

        source_url = 'http://music.163.com/#/album?id={}'.format(album_id)
        img_url = album_info.get('picUrl')
        title = album_info.get('name')
        description = album_info.get('description')
        create_time = time.strftime("%Y-%m-%d", time.localtime(album_info.get('publishTime') / 1000))

        song_list = [
            {'song_id': song.get('id'),
             'title': song.get('name'),
             'artist': song.get('artists')[0].get('name'),
             'artist_id': song.get('artists')[0].get('id'),
             'album': song.get('album').get('name'),
             'album_id': song.get('album').get('id'),
             'img_url': song.get('album').get('picUrl'),
             'source_url': 'https://music.163.com/#/song?id={}'.format(song.get('id')),
             'platform': self.__class__.__name__,
             'platform_name': self.__class__.title
             } for song in album_info.get('songs') if self._is_playable(song.get('fee'))
        ]

        return {
            'source_url': source_url,
            'album_id': album_id,
            'img_url': img_url,
            'title': title,
            'song_list': song_list,
            'description': description,
            'create_time': create_time,
            'platform': self.__class__.__name__,
            'song_total': len(song_list)

        }

    # 获取推荐歌单
    def get_recommend_playlist(self, page_size=20, page_num=1):
        page_size = int(page_size)
        page_num = int(page_num)
        target_url = 'http://music.163.com/discover/playlist/??order=hot&limit={}&offset={}'.format(page_size,
                                                                                                    20 * (page_num - 1))

        response = requests.get(target_url,
                                headers=self.headers)

        response.raise_for_status()

        content = response.text

        playlist_re = re.findall(
            r'''<div class="u-cover u-cover-1">\n<img class="j-flag" src="(.*?)"/>.*?<span class="nb">(.*?)</span>.*?href="/playlist\?id=(\d+)" class="tit f-thide s-fc0">(.*?)</a>.*?</li>''',
            content, re.S)

        assert playlist_re, '网易云音乐推荐歌单异常!请求地址:{}\n请求参数:{}\n返回结果:{}'.format(target_url, '',response.text)

        playlist_list = [
            {'id': str(playlist[2]),
             'img_url': playlist[0],
             'title': playlist[3],
             'subscribe_count': self.num_to_str(playlist[1]),
             'tags': [],
             'source_url': 'https://music.163.com/#/playlist?id={}'.format(playlist[2]),
             'platform': self.__class__.__name__
             } for playlist in playlist_re
        ]

        return playlist_list

    # 获取歌单详情
    def get_playlist_detail(self, playlist_id):
        '''
        获取歌单详情内容
        :param playlist_id: 歌单id
        :return: dict 返回歌单详情内容
        '''
        target_url = 'http://music.163.com/weapi/v3/playlist/detail'

        data = {
            'id': str(playlist_id),
            'offset': 0,
            'total': True,
            'limit': 1000,
            'n': 1000,
            'csrf_token': ''
        }

        params_dict = self._encrypted_request(data)

        response = requests.post(target_url,
                                 data=params_dict,
                                 headers=self.headers)

        response.raise_for_status()
        playlist_detail = response.json()

        assert playlist_detail.get('code') == 200, '网易云音乐歌单详情获取失败!请求地址:{}\n请求参数:{}\n返回结果:{}'.format(target_url, data,response.text)

        playlist = playlist_detail.get('playlist')
        source_url = f'http://music.163.com/#/playlist?id={playlist_id}'
        img_url = playlist.get('coverImgUrl')
        title = playlist.get('name')
        tags = playlist.get('tags')
        description = playlist.get('description')
        create_time = time.strftime("%Y-%m-%d", time.localtime(playlist.get('createTime') / 1000))
        subscribe_count = playlist.get('subscribedCount')
        song_ids = [item.get('id') for item in playlist.get('trackIds')]
        song_list = self._get_song_detail(song_ids)

        return {
            'source_url': source_url,
            'playlist_id': playlist_id,
            'img_url': img_url,
            'title': title,
            'tags': tags,
            'description': description,
            'create_time': create_time,
            'subscribe_count': self.num_to_str(subscribe_count),
            'song_list': song_list,
            'platform': self.__class__.__name__,
            'song_total': len(song_list)
        }

    # 获取排行榜
    def get_toplist(self):
        '''
        获取所有排行榜
        :return: list
        '''
        target_url = 'https://music.163.com/api/toplist'

        response = requests.get(target_url,
                                headers=self.headers)

        response.raise_for_status()
        response_json = response.json()

        assert response_json.get('code') == 200, '网易云音乐获取排行榜失败!请求地址:{}\n请求参数:{}\n返回结果:{}'.format(target_url, '',response.text)

        toplist_content = response_json.get('list')

        toplist_list = [{
            'id': toplist.get('id'),
            'img_url': toplist.get('coverImgUrl'),
            'title': toplist.get('name'),
            'tags': toplist.get('tags'),
            'subscribe_count': self.num_to_str(toplist.get('subscribedCount')),
            'source_url': 'https://music.163.com/#/discover/toplist?id={}'.format(toplist.get('id')),
            'platform': self.__class__.__name__
        } for toplist in toplist_content]

        return toplist_list

    # 获取排行榜歌单详情
    def get_toplist_detail(self, toplist_id):
        '''
        排行榜也是歌单 可调歌单详情获取内容
        :param toplist_id:  排行榜ID
        :return:
        '''
        toplist_dict = self.get_playlist_detail(toplist_id)
        toplist_dict['toplist_id'] = toplist_dict['playlist_id']

        return toplist_dict

    # 搜索
    def search(self, keyword, page_num=1, page_size=20):
        target_url = 'http://music.163.com/api/search/pc'

        data = {
            's': keyword,
            'offset': page_size * (page_num - 1),
            'limit': page_size,
            'type': 1,
        }

        response = requests.post(target_url,
                                 data=data,
                                 headers=self.headers)

        response.raise_for_status()
        search_info = response.json()

        assert search_info.get('code') == 200, '网易云音乐搜索失败!请求地址:{}\n请求参数:{}\n返回结果:{}'.format(target_url, data,response.text)

        total = search_info.get('result').get('songCount')

        if search_info.get('result').get('songs'):
            result = [{
                'song_id': data.get('id'),
                'title': data.get('name'),
                'artist': data.get('artists')[0].get('name'),
                'artist_id': data.get('artists')[0].get('id'),
                'album': data.get('album').get('name'),
                'album_id': data.get('album').get('id'),
                'img_url': data.get('album').get('picUrl'),
                'source_url': 'http://music.163.com/#/song?id={}'.format(data.get('id')),
                'platform': self.__class__.__name__,
                'platform_name': self.__class__.title
            } for data in search_info.get('result').get('songs') if self._is_playable(data.get('fee'))]
        else:
            result = []

        return {
            'list': result,
            'total': total
        }


if __name__ == '__main__':
    netease_music = NeteaseMusic()
    # netease_music.search('周杰伦')
    # netease_music.get_album_detail(97890473)
    # netease_music.get_song_detail(185809)
    # print(netease_music.get_playlist_detail(5218934316))
    # netease_music.get_playlist_detail(5308273663)
    # netease_music.get_toplist()
    # print(netease_music.get_toplist_detail(19723756))
    # netease_music.get_recommend_playlist()
    netease_music.get_song_lyric(1492318657)

    # netease_music.get_song_play_url('186016')

    # netease_music.get_artist_detail(6452)

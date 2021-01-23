from Music.platforms import BaseMusic
import requests
import hashlib
import time


class QianqianMusic(BaseMusic):
    title = '千千音乐'
    is_support_toplist = 0  # 没有排行榜

    def _is_playable(self, isVip):

        return isVip == 0

    def _calcSign(self, e):
        secret = '0b50b02fd0d73a9c4c8c3a781c30845f'
        n = list(e.keys())
        n.sort()
        i = f'{n[0]}={e[n[0]]}'
        for r in range(1, len(n)):
            o = n[r]
            i += f'&{o}={e[o]}'
        sign = hashlib.md5((i + secret).encode('utf-8')).hexdigest()
        return sign

    # 获取歌曲播放地址
    def get_song_play_url(self, song_id):
        target_url = 'https://music.taihe.com/v1/song/tracklink?TSID={}'.format(song_id)

        response = requests.get(target_url)
        response.raise_for_status()
        response_json = response.json()
        assert response_json.get('errno') == 22000, '千千音乐歌曲播放地址获取异常!请求地址:{}\n请求参数:{}\n返回结果:{}'.format(target_url, '',
                                                                                                      response.text)
        play_url = response_json['data']['path']
        return {'platform': self.__class__.__name__,
                'play_url': play_url}

    # 获取歌曲歌词
    def get_song_lyric(self, song_id):
        target_url = 'https://music.taihe.com/v1/song/tracklink?TSID={}'.format(song_id)

        response = requests.get(target_url, headers=self.headers)
        response.raise_for_status()
        response_json = response.json()
        assert response_json.get('errno') == 22000, '千千音乐歌词获取异常!请求地址:{}\n请求参数:{}\n返回结果:{}'.format(target_url, '',
                                                                                                  response.text)
        lyric_url = response_json['data']['lyric']

        if lyric_url.split('.')[-1] == 'txt':
            lyric = '暂无歌词'

        else:
            response = requests.get(lyric_url, headers=self.headers)

            lyric = response.text

        return {'platform': self.__class__.__name__,
                'lyric': lyric}

    # 获取专辑详情
    def get_album_detail(self, album_id):
        target_url = 'https://music.taihe.com/v1/album/info'
        params = {
            'albumAssetCode': album_id,
            'timestamp': str(int(time.time()))
        }
        sign = self._calcSign(params)
        params['sign'] = sign
        response = requests.get(target_url,
                                params=params,
                                headers=self.headers)

        response.raise_for_status()
        response_json = response.json()

        assert response_json.get('errno') == 22000, '千千音乐专辑详情获取异常!请求地址:{}\n请求参数:{}\n返回结果:{}'.format(target_url, params,
                                                                                                    response.text)

        album_info = response_json.get('data')

        source_url = 'https://music.taihe.com/songlist/{}'.format(album_id)
        img_url = album_info.get('pic')
        title = album_info.get('title')
        description = album_info.get('introduce')
        create_time = album_info.get('releaseDate').split('T')[0]

        song_list = [
            {'song_id': song.get('assetId'),
             'title': song.get('title'),
             'artist': song.get('artist')[0].get('name') if song.get('artist') else '',
             'artist_id': song.get('artist')[0].get('artistCode') if song.get('artist') else '',
             'album': title,
             'album_id': album_id,
             'img_url': img_url,
             'source_url': 'https://music.taihe.com/song/{}'.format(song.get('assetId')),
             'platform': self.__class__.__name__,
             'platform_name': self.__class__.title
             } for song in album_info.get('trackList') if self._is_playable(song.get('isVip', 0))
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

    # 获取歌手详情
    def get_artist_detail(self, artist_id, page_num=1, page_size=100):
        target_url = 'https://music.taihe.com/v1/artist/info'
        params = {
            'artistCode': artist_id,
            'timestamp': str(int(time.time()))
        }
        sign = self._calcSign(params)
        params['sign'] = sign
        response = requests.get(target_url,
                                params=params,
                                headers=self.headers)

        response.raise_for_status()
        response_json = response.json()

        assert response_json.get('errno') == 22000, '千千音乐歌手详情获取异常!请求地址:{}\n请求参数:{}\n返回结果:{}'.format(target_url, params,
                                                                                                    response.text)
        artist_info = response_json['data']

        source_url = 'https://music.taihe.com/artist/{}'.format(artist_id)
        img_url = artist_info.get('pic')
        title = artist_info.get('name')

        target_url = 'https://music.taihe.com/v1/artist/song'
        params = {
            'artistCode': artist_id,
            'pageNo': page_num,
            'pageSize': page_size,
            'timestamp': str(int(time.time()))
        }
        sign = self._calcSign(params)
        params['sign'] = sign
        response = requests.get(target_url,
                                params=params,
                                headers=self.headers)

        response.raise_for_status()
        response_json = response.json()

        assert response_json.get('errno') == 22000, '千千音乐歌手详情获取异常!请求地址:{}\n请求参数:{}\n返回结果:{}'.format(target_url, params,
                                                                                                    response.text)

        song_info_list = response_json['data']['result']
        song_list = [
            {'song_id': song.get('id'),
             'title': song.get('title'),
             'artist': song.get('artist')[0]['name'] if song.get('artist') else '',
             'artist_id': song.get('artist')[0]['artistCode'] if song.get('artist') else '',
             'album': song.get('albumTitle'),
             'album_id': song.get('albumAssetCode'),
             'img_url': song.get('pic'),
             'source_url': 'https://music.taihe.com/song/{}'.format(song.get('id')),
             'platform': self.__class__.__name__,
             'platform_name': self.__class__.title
             } for song in song_info_list if self._is_playable(song.get('isVip', 0))
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

    # 获取推荐歌单
    def get_recommend_playlist(self, page_size=20, page_num=1):
        '''
        获取推荐歌单
        :param page_size: 页码
        :param page_num:  页数 接口返回最多60个
        :return: list
        '''
        page_size = int(page_size)
        page_num = int(page_num)
        target_url = 'https://music.taihe.com/v1/tracklist/list?pageSize={}&pageNo={}'.format(page_size, page_num)
        response = requests.get(target_url,
                                headers=self.headers)

        response.raise_for_status()
        response_json = response.json()

        assert response_json.get('errno') == 22000, '千千音乐推荐歌单获取异常!请求地址:{}\n请求参数:{}\n返回结果:{}'.format(target_url, '',
                                                                                                    response.text)

        playlist_info = response_json['data']['result']

        playlist_list = [
            {'id': str(playlist.get('id')),
             'img_url': playlist.get('pic'),
             'title': playlist.get('title'),
             'subscribe_count': 0,
             'tags': playlist.get('tagList'),
             'source_url': 'https://music.taihe.com/songlist?subCateId=&pageNo={}'.format(page_num),
             'platform': self.__class__.__name__
             } for playlist in playlist_info
        ]

        return playlist_list

    # 获取歌单详情
    def get_playlist_detail(self, playlist_id):

        target_url = 'https://music.taihe.com/v1/tracklist/info?id={}&pageSize=200'.format(playlist_id)
        response = requests.get(target_url,
                                headers=self.headers)

        response.raise_for_status()
        response_json = response.json()

        assert response_json.get('errno') == 22000, '千千音乐歌单详情获取异常!请求地址:{}\n请求参数:{}\n返回结果:{}'.format(target_url, '',
                                                                                                    response.text)
        playlist_info = response_json.get('data')

        source_url = 'https://music.taihe.com/songlist/{}'.format(playlist_id)
        img_url = playlist_info.get('pic')
        title = playlist_info.get('title')
        tags = playlist_info.get('tags')
        description = playlist_info.get('desc')
        create_time = playlist_info.get('addDate').split('T')[0]
        subscribe_count = 0
        song_list = [
            {'song_id': song.get('id'),
             'title': song.get('title'),
             'artist': song.get('artist')[0].get('name') if song.get('artist') else '',
             'artist_id': song.get('artist')[0].get('artistCode') if song.get('artist') else '',
             'album': song.get('albumTitle'),
             'album_id': song.get('albumAssetCode'),
             'img_url': song.get('pic'),
             'source_url': 'https://music.taihe.com/song/{}'.format(song.get('id')),
             'platform': self.__class__.__name__,
             'platform_name': self.__class__.title
             } for song in playlist_info.get('trackList') if self._is_playable(song.get('isVip', 0))
        ]

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

    # 搜索
    def search(self, keyword, page_num=1, page_size=20):
        target_url = 'https://music.taihe.com/v1/search'
        params = {
            'word': keyword,
            'timestamp': str(int(time.time()))
        }
        sign = self._calcSign(params)
        params['sign'] = sign
        response = requests.get(target_url,
                                params,
                                headers=self.headers)

        response.raise_for_status()
        response_json = response.json()

        assert response_json.get('errno') == 22000, '千千音乐搜索异常!请求地址:{}\n请求参数:{}\n返回结果:{}'.format(target_url, '',
                                                                                                    response.text)

        search_info = response_json.get('data').get('typeTrack')

        total = len(search_info)
        if search_info:
            result = [
                {'song_id': song.get('id'),
                 'title': song.get('title'),
                 'artist': song.get('artist')[0].get('name') if song.get('artist') else '',
                 'artist_id': song.get('artist')[0].get('artistCode') if song.get('artist') else '',
                 'album': song.get('albumTitle'),
                 'album_id': song.get('albumAssetCode'),
                 'img_url': song.get('pic'),
                 'source_url': 'https://music.taihe.com/song/{}'.format(song.get('id')),
                 'platform': self.__class__.__name__,
                 'platform_name': self.__class__.title
                 } for song in search_info if self._is_playable(song.get('isVip'))
            ]
        else:
            result = []

        return {'list': result,'total': total}



if __name__ == '__main__':
    qian = QianqianMusic()
    # qian.get_song_play_url('T10038826794')
    # qian.get_song_lyric('T10055694869')
    # qian.get_album_detail('P10003395611')
    # qian.get_artist_detail('A10048883')
    # qian.get_recommend_playlist()
    # qian.get_playlist_detail('270592')
    qian.search('周')
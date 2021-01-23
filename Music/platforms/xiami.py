from Music.platforms import BaseMusic
import requests
from hashlib import md5
import time
import json


class XiamiMusic(BaseMusic):
    title = '虾米音乐'

    def __init__(self):
        super(XiamiMusic, self).__init__()

    def _get_session(self):
        self.session = requests.Session()
        self.session.get('https://www.xiami.com', headers=self.headers)
        self.token = self.session.cookies.get("xm_sg_tk").split("_")[0]

    def _get_params__s(self, api, _q='', token=''):
        '''
        :param api: URL的地址
        :param _q:  需要加密的参数
        :return: 加密字符串
        '''
        if not token:
            token = self.token
        data = token + "_xmMain_" + api + "_" + _q
        return md5(bytes(data, encoding="utf-8")).hexdigest()

    def _sign(self, params, token=''):
        appkey = '23649156'
        t = str(int(time.time() * 1000))
        request_str = {
            'header': {'appId': '200', 'platformId': 'h5'},
            'model': params
        }
        data = json.dumps({'requestStr': json.dumps(request_str)})
        sign = '%s&%s&%s&%s' % (token, t, appkey, data)
        sign = md5(sign.encode('utf-8')).hexdigest()

        return {
            't': t,
            'appKey': appkey,
            'sign': sign,
            'data': data
        }

    def _is_playable(self, status):
        return int(status) == 0

    # 获取歌曲播放地址
    def get_song_play_url(self, song_id):
        self._get_session()
        target_url = 'https://www.xiami.com/api/song/getPlayInfo'
        _q = "{{\"songIds\":[{}]}}".format(song_id)
        params = {
            '_s': self._get_params__s('/api/song/getPlayInfo', _q),
            '_q': _q
        }
        response = self.session.get(target_url,
                                    params=params)
        response.raise_for_status()
        response_json = response.json()

        assert response_json.get('code') == 'SUCCESS', '虾米音乐歌曲播放地址获取异常!请求地址:{}\n请求参数:{}\n返回结果:{}'.format(target_url, params,response.text)

        song_info = response_json["result"]["data"]["songPlayInfos"][0]
        play_url = song_info["playInfos"][0]["listenFile"] or song_info["playInfos"][1]["listenFile"]
        return {'platform': self.__class__.__name__,
                'play_url': play_url}

    # 获取歌曲歌词
    def get_song_lyric(self, song_id):
        self._get_session()
        target_url = 'https://www.xiami.com/api/song/initialize'
        _q = "{{\"songId\":{}}}".format(song_id)
        params = {
            '_s': self._get_params__s('/api/song/initialize', _q),
            '_q': _q
        }
        response = self.session.get(target_url,
                                    params=params)
        response.raise_for_status()
        response_json = response.json()

        assert response_json.get('code') == 'SUCCESS', '虾米音乐歌词获取异常!\n请求地址:{}\n请求参数:{}\n返回结果:{}'.format(target_url, params,response.text)

        song_lyric_list = response_json['result']['data']['songLyric']
        song_lyric = [lyric for lyric in song_lyric_list if lyric['type'] == 2]  # 选择lrc格式
        lyric = song_lyric[0]['content'] if song_lyric else ''
        return {'platform': self.__class__.__name__,
                'lyric': lyric}

    # 获取专辑详情
    def get_album_detail(self, album_id):
        self._get_session()
        target_url = 'https://www.xiami.com/api/album/getAlbumDetail'
        _q = "{\"albumId\":%s}" % str(album_id)
        params = {
            "_s": self._get_params__s('/api/album/getAlbumDetail', _q),
            '_q': _q
        }
        response = self.session.get(target_url,
                                    params=params)
        response.raise_for_status()
        response_json = response.json()

        assert response_json.get('code') == 'SUCCESS', '虾米音乐专辑详情获取异常!\n请求地址:{}\n请求参数:{}\n返回结果:{}'.format(target_url, params,response.text)

        album_info = response_json['result']['data']['albumDetail']

        source_url = 'https://www.xiami.com/album/{}'.format(album_info.get('albumStringId'))
        img_url = album_info.get('albumLogo')
        title = album_info.get('albumName')
        description = album_info.get('description')

        song_list = [
            {'song_id': str(song.get('songId')),
             'title': song.get('songName'),
             'artist': song.get('artistName'),
             'artist_id': str(song.get('artistId')),
             'album': song.get('albumName'),
             'album_id': str(song.get('albumId')),
             'img_url': song.get('albumLogo'),
             'source_url': 'https://www.xiami.com/song/{}'.format(song.get('songStringId')),
             'platform': self.__class__.__name__,
             'platform_name': self.__class__.title
             } for song in album_info.get('songs') if self._is_playable(song.get('songStatus', 0))
        ]

        return {
            'source_url': source_url,
            'album_id': album_id,
            'img_url': img_url,
            'title': title,
            'song_list': song_list,
            'description': description,
            'create_time': '',
            'platform': self.__class__.__name__,
            'song_total': len(song_list)
        }

    # 获取歌手详情
    def get_artist_detail(self, artist_id, page_num=1, page_size=30):
        self._get_session()
        target_url = "https://m.xiami.com/graphql?query=query{{artistDetail(artistId:%22{artist_id}%22,artistStringId:%22{artist_id}%22){{artistDetailVO{{artistName%20artistLogo}}}}}}".format(
            artist_id=artist_id)

        response = requests.get(target_url, headers=self.headers)

        response.raise_for_status()
        response_json = response.json()

        artist_info = response_json['data']['artistDetail']['artistDetailVO']
        source_url = 'https://www.xiami.com/artist/{}'.format(artist_id)
        title = artist_info['artistName']
        img_url = artist_info['artistLogo']

        target_url = 'https://www.xiami.com/api/song/getArtistSongs'
        _q = "{\"artistId\":%s,\"category\":0,\"pagingVO\":{\"page\":%d,\"pageSize\":%d}}" % (
            str(artist_id), page_num, page_size)
        params = {
            "_s": self._get_params__s('/api/song/getArtistSongs', _q),
            '_q': _q
        }
        response = self.session.get(target_url,
                                    params=params)
        response.raise_for_status()
        response_json = response.json()

        assert response_json.get('code') == 'SUCCESS', '虾米音乐歌手详情获取异常!\n' + response.text

        artist_songs = response_json.get('result')['data']['songs']

        song_list = [
            {'song_id': str(song.get('songId')),
             'title': song.get('songName'),
             'artist': song.get('artistName'),
             'artist_id': str(song.get('artistId')),
             'album': song.get('albumName'),
             'album_id': str(song.get('albumId')),
             'img_url': song.get('albumLogo'),
             'source_url': 'https://www.xiami.com/song/{}'.format(song.get('songStringId')),
             'platform': self.__class__.__name__,
             'platform_name': self.__class__.title
             } for song in artist_songs if self._is_playable(song.get('songStatus', 0))
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
        self._get_session()
        page_size = int(page_size)
        page_num = int(page_num)
        target_url = 'https://www.xiami.com/api/list/collect'
        _q = "{\"pagingVO\":{\"page\":%s,\"pageSize\":%s},\"dataType\":\"system\"}" % (str(page_num), str(page_size))
        params = {
            "_s": self._get_params__s('/api/list/collect', _q),
            '_q': _q
        }

        response = self.session.get(target_url,
                                    params=params)

        response.raise_for_status()
        response_json = response.json()

        assert response_json.get('code') == 'SUCCESS', '虾米音乐推荐歌单获取异常!\n请求地址:{}\n请求参数:{}\n返回结果:{}'.format(target_url, params,response.text)

        playlist_info = response_json.get('result').get('data').get('collects')

        playlist_list = [
            {'id': str(playlist.get('listId')),
             'img_url': playlist.get('collectLogo'),
             'title': playlist.get('collectName'),
             'subscribe_count': self.num_to_str(playlist.get('playCount')),
             'tags': playlist.get('tags'),
             'source_url': 'https://www.xiami.com/collect/{}'.format(playlist.get('listId')),
             'platform': self.__class__.__name__
             } for playlist in playlist_info
        ]
        return playlist_list

    # 获取歌单详情
    def get_playlist_detail(self, playlist_id):
        self._get_session()
        target_url = 'https://www.xiami.com/api/collect/getCollectStaticUrl'
        _q = "{\"listId\":%s}" % str(playlist_id)
        params = {
            "_s": self._get_params__s('/api/collect/getCollectStaticUrl', _q),
            '_q': _q
        }

        response = self.session.get(target_url,
                                    params=params)

        response.raise_for_status()
        response_json = response.json()

        assert response_json.get('code') == 'SUCCESS', '虾米音乐歌单详情获取异常!\n请求地址:{}\n请求参数:{}\n返回结果:{}'.format(target_url, params,response.text)

        playlist_url = response_json['result']['data']['data']['data']['url']

        response = self.session.get(playlist_url, headers=self.headers)
        response.raise_for_status()
        response_json = response.json()

        playlist_info = response_json.get('resultObj')

        source_url = 'https://www.xiami.com/collect/{}'.format(playlist_id)
        img_url = playlist_info.get('collectLogo')
        title = playlist_info.get('collectName')
        tags = playlist_info.get('tags')
        description = playlist_info.get('description')
        create_time = time.strftime("%Y-%m-%d", time.localtime(playlist_info.get('gmtCreate') / 1000))
        subscribe_count = self.num_to_str(playlist_info.get('playCount'))

        song_list = [
            {'song_id': str(song.get('songId')),
             'title': song.get('songName'),
             'artist': song.get('artistName'),
             'artist_id': str(song.get('artistId')),
             'album': song.get('albumName'),
             'album_id': str(song.get('albumId')),
             'img_url': song.get('albumLogo'),
             'source_url': 'https://www.xiami.com/song/{}'.format(song.get('songStringId')),
             'platform': self.__class__.__name__,
             'platform_name': self.__class__.title
             } for song in playlist_info.get('songs') if self._is_playable(song.get('songStatus', 0))
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

    # 获取排行榜
    def get_toplist(self):
        '''
        获取所有排行榜的
        :return: list
        '''
        self._get_session()
        target_url = 'https://www.xiami.com/api/billboard/getBillboards'
        params = {
            "_s": self._get_params__s('/api/billboard/getBillboards')
        }

        response = self.session.get(target_url,
                                    params=params)

        response.raise_for_status()
        response_json = response.json()

        assert response_json.get('code') == 'SUCCESS', '虾米音乐排行榜获取异常!\n请求地址:{}\n请求参数:{}\n返回结果:{}'.format(target_url, params,response.text)
        toplist_content = []
        data = response_json.get('result').get('data')
        toplist_content.extend(data.get('xiamiBillboards'))
        toplist_content.extend(data.get('globalBillboards'))
        toplist_content.extend(data.get('spBillboards'))

        toplist_list = [{
            'id': toplist.get('billboardId'),
            'img_url': toplist.get('logoMiddle'),
            'title': toplist.get('name'),
            'tags': [],
            'subscribe_count': 0,
            'source_url': 'https://www.xiami.com/billboard/' + str(toplist.get('billboardId')),
            'platform': self.__class__.__name__
        } for toplist in toplist_content]
        return toplist_list

    # 获取排行榜歌单详情
    def get_toplist_detail(self, toplist_id):
        self._get_session()
        target_url = 'https://www.xiami.com/api/billboard/getBillboardDetail'
        _q = "{{\"billboardId\":{}}}".format(toplist_id)
        params = {
            '_s': self._get_params__s('/api/billboard/getBillboardDetail', _q),
            '_q': _q
        }
        response = self.session.get(target_url,
                                    params=params)

        response.raise_for_status()
        response_json = response.json()

        assert response_json.get('code') == 'SUCCESS', '虾米音乐排行榜歌单详情获取异常!\n请求地址:{}\n请求参数:{}\n返回结果:{}'.format(target_url, params,response.text)

        toplist_info = response_json['result']['data']['billboard']
        source_url = 'https://www.xiami.com/billboard/' + str(toplist_info.get('billboardId'))
        img_url = toplist_info.get('logoMiddle')
        title = toplist_info.get('name')
        tags = []
        description = toplist_info.get('description')
        song_list = [
            {'song_id': str(song.get('songId')),
             'title': song.get('songName'),
             'artist': song.get('artistName'),
             'artist_id': str(song.get('artistId')),
             'album': song.get('albumName'),
             'album_id': str(song.get('albumId')),
             'img_url': song.get('albumLogo'),
             'source_url': 'https://www.xiami.com/song/{}'.format(song.get('songStringId')),
             'platform': self.__class__.__name__,
             'platform_name': self.__class__.title
             } for song in toplist_info.get('songs') if self._is_playable(song.get('songStatus', 0))
        ]

        return {
            'source_url': source_url,
            'toplist_id': toplist_id,
            'img_url': img_url,
            'title': title,
            'tags': tags,
            'description': description,
            'create_time': '',
            'subscribe_count': 0,
            'song_list': song_list,
            'platform': self.__class__.__name__,
            'song_total': len(song_list)
        }

    # 搜索
    def search(self, keyword, page_num=1, page_size=20):
        session = requests.Session()
        action = 'mtop.alimusic.music.songservice.getsongdetail'
        url = 'https://acs.m.xiami.com/h5/{action}/1.0/'.format(action=action)
        params = {'songId': '1'}
        response = session.get(url, params=self._sign(params))
        cookies = response.cookies.get_dict()
        token = cookies['_m_h5_tk'].split('_')[0]
        search_url = 'https://acs.m.xiami.com/h5/{action}/1.0/'.format(
            action='mtop.alimusic.search.searchservice.searchsongs')
        params = {
            'key': keyword,
            'pagingVO': {'page': page_num, 'pageSize': page_size}
        }
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36',
            'Referer': 'http://h.xiami.com',
            'Connection': 'keep-alive',
            'Accept-Language': 'zh-CN,zh;q=0.8,gl;q=0.6,zh-TW;q=0.4',
            'Accept-Encoding': 'gzip,deflate,sdch',
            'Accept': '*/*'
        }

        response = session.get(search_url, headers=headers, params=self._sign(params, token))

        response.raise_for_status()
        response_json = response.json()

        search_info = response_json['data']['data']
        total = search_info['pagingVO']['count']
        result = [{
            'song_id': data.get('songId'),
            'title': data.get('songName'),
            'artist': data.get('artistName'),
            'artist_id': data.get('artistId'),
            'album': data.get('albumName'),
            'album_id': data.get('albumId'),
            'img_url': data.get('albumLogo'),
            'playable': self._is_playable(data.get('songStatus', 0)),
            'source_url': 'https://music.migu.cn/v3/music/song/{}'.format(data.get('songStringId')),
            'platform': self.__class__.__name__,
            'platform_name': self.__class__.title
        } for data in search_info['songs'] if self._is_playable(data.get('songStatus', 0))
        ]

        return {
            'list': result,
            'total': total
        }


if __name__ == '__main__':
    xiami = XiamiMusic()
    # xiami.get_toplist()
    # xiami.get_playlist_detail('1311308308')
    # xiami.get_album_detail('2102793120')
    xiami.search('周杰伦')
    xiami.get_artist_detail('9dfJqQ18f19')

    # xiami.get_toplist_detail(328)

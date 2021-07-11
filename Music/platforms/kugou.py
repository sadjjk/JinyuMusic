from Music.platforms import BaseMusic
import requests
import hashlib
import time
import json
import execjs


class KugouMusic(BaseMusic):
    title = '酷狗音乐'

    def _random_string(self):
        """
        生成随机字符串
        :return:
        """
        generate_string = execjs.eval('(((1 + Math.random()) * 0x10000) | 0).toString(16).substring(1)')
        return generate_string

    def _hash_md5(self):
        """
        MD5加密
        :return: 返回加密后的字符串
        """
        # 组合随机字符串
        string = self._random_string() + self._random_string() + '-' + self._random_string() + '-' + self._random_string() + '-' + self._random_string() + '-' + self._random_string() + self._random_string() + self._random_string()
        hash_ = hashlib.md5()
        hash_.update(string.encode())
        kg_mid = hash_.hexdigest()
        return kg_mid

    def __init__(self):
        super(KugouMusic, self).__init__()
        self.headers['Referer'] = 'http://www.kugou.com/'

    def _is_playable(self, privilege):
        return int(privilege) <= 8

    # 获取歌曲播放地址
    def get_song_play_url(self, song_id):

        # 该接口无法获取付费歌曲
        # target_url = 'http://m.kugou.com/app/i/getSongInfo.php?cmd=playInfo&hash={}'.format(song_id)
        # response = requests.get(target_url,
        #                         headers=self.headers)

        # 获取歌曲详细信息 需要Cookie
        # https://github.com/YungGuo08/WebSpider/blob/184daf776e538e36c109d9706409dee23ed40411/Music_Download/Kugou_Music/kg_mid_generator.py
        cookie = {'kg_mid': 'aad44cc5d3cf31fe45f76e8c8561d8a3'}

        target_url = 'https://wwwapi.kugou.com/yy/index.php?r=play/getdata&callback=jQuery&hash={}'.format(song_id)
        response = requests.get(target_url, cookies=cookie)
        response.raise_for_status()
        response_json = json.loads(response.text.lstrip('jQuery(').rstrip(');\n'))

        assert response_json.get('err_code') == 0, '酷狗音乐歌曲播放地址获取异常!\n请求地址:{}\n返回结果:{}'.format(target_url, response.text)
        play_url = response_json.get('data').get('play_url')
        album_id = response_json.get('data').get('album_id')

        if not play_url:
            target_url = 'https://wwwapi.kugou.com/yy/index.php?r=play/getdata&callback=jQuery&hash={}&album_id={}'.format(
                song_id, album_id)
            response = requests.get(target_url, cookies=cookie)
            response.raise_for_status()
            response_json = json.loads(response.text.lstrip('jQuery(').rstrip(');\n'))

            assert response_json.get('err_code') == 0, '酷狗音乐歌曲播放地址获取异常!\n请求地址:{}\n返回结果:{}'.format(target_url,
                                                                                                  response.text)
            play_url = response_json.get('data').get('play_url')

        return {'platform': self.__class__.__name__,
                'play_url': play_url}

    # 获取歌曲歌词
    def get_song_lyric(self, song_id):
        target_url = 'http://m.kugou.com/app/i/krc.php'
        params = {
            'cmd': '100',
            'timelength': '999999',
            'hash': song_id
        }
        response = requests.get(target_url,
                                params=params,
                                headers=self.headers)

        response.encoding = 'utf-8'
        response.raise_for_status()
        lyric = response.text
        return {'platform': self.__class__.__name__,
                'lyric': lyric}

    # 获取专辑详情
    def get_album_detail(self, album_id):
        target_url = 'http://mobilecdnbj.kugou.com/api/v3/album/info?albumid={}'.format(album_id)
        response = requests.get(target_url, headers=self.headers)
        response.raise_for_status()
        response_json = response.json()
        assert response_json.get('errcode') == 0, '酷狗音乐专辑详情获取异常!\n请求地址:{}\n请求参数:{}\n返回结果:{}'.format(target_url, '',
                                                                                                    response.text)

        album_info = response_json.get('data')
        source_url = 'https://www.kugou.com/album/{}.html'.format(album_id)
        img_url = album_info.get('imgurl').replace('{size}', '400')
        title = album_info.get('albumname')
        description = album_info.get('intro')
        create_time = album_info.get('publishtime')
        artist_id = album_info.get('singerid')
        artist = album_info.get('singername')

        target_url = 'http://ioscdn.kugou.com/api/v3/album/song?albumid={}&page=1&pagesize=-1'.format(album_id)
        response = requests.get(target_url, headers=self.headers)
        response.raise_for_status()
        response_json = response.json()
        assert response_json.get('errcode') == 0, '酷狗音乐专辑歌曲详情获取异常!\n请求地址:{}\n请求参数:{}\n返回结果:{}'.format(target_url, '',
                                                                                                      response.text)

        album_song_info = response_json['data']['info']
        song_list = [
            {'song_id': song.get('hash'),
             'title': song.get('filename').split('-')[-1].strip(),
             'artist': artist,
             'artist_id': artist_id,
             'album': title,
             'album_id': song.get('album_id'),
             'img_url': img_url,
             'source_url': 'https://www.kugou.com/song/#hash={}'.format(song.get('hash')),
             'platform': self.__class__.__name__,
             'platform_name': self.__class__.title
             } for song in album_song_info
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
        target_url = 'http://mobilecdnbj.kugou.com/api/v3/singer/info?singerid={}'.format(artist_id)
        response = requests.get(target_url, headers=self.headers)
        response.raise_for_status()
        response_json = response.json()
        assert response_json.get('errcode') == 0, '酷狗音乐歌手详情获取异常!\n请求地址:{}\n请求参数:{}\n返回结果:{}'.format(target_url, '',
                                                                                                    response.text)

        artist_info = response_json.get('data')
        source_url = 'https://www.kugou.com/singer/{}.html'.format(artist_id)
        img_url = artist_info.get('imgurl').replace('{size}', '400')
        title = artist_info.get('singername')
        description = artist_info.get('intro')

        target_url = 'http://mobilecdnbj.kugou.com/api/v3/singer/song?singerid={}&page=1&pagesize=-1'.format(artist_id)
        response = requests.get(target_url, headers=self.headers)
        response.raise_for_status()
        response_json = response.json()
        assert response_json.get('errcode') == 0, '酷狗音乐歌手歌曲详情获取异常!\n请求地址:{}\n请求参数:{}\n返回结果:{}'.format(target_url, '',
                                                                                                      response.text)

        artist_song_info = response_json['data']['info']
        song_list = [
            {'song_id': song.get('hash'),
             'title': song.get('filename').split('-')[-1].strip(),
             'artist': title,
             'artist_id': artist_id,
             'img_url': img_url,
             'source_url': 'https://www.kugou.com/song/#hash={}'.format(song.get('hash')),
             'platform': self.__class__.__name__,
             'platform_name': self.__class__.title
             } for song in artist_song_info
        ]

        return {
            'source_url': source_url,
            'artist_id': artist_id,
            'img_url': img_url,
            'title': title,
            'song_list': song_list,
            'description': description,
            'platform': self.__class__.__name__,
            'song_total': len(song_list)
        }

    # 获取推荐歌单
    def get_recommend_playlist(self, page_size=20, page_num=1):
        '''
        获取推荐歌单
        :param page_size: 页码
        :param page_num:  页数
        :return: list
        '''
        page_num = int(page_num)
        target_url = 'http://m.kugou.com/plist/index&json=true&page={}'.format(page_num)
        response = requests.get(target_url,
                                headers=self.headers)

        response.raise_for_status()
        response_json = response.json()

        playlist_info = response_json['plist']['list']['info']

        playlist_list = [
            {'id': str(playlist.get('specialid')),
             'img_url': playlist.get('imgurl').replace('{size}', '400'),
             'title': playlist.get('specialname'),
             'subscribe_count': self.num_to_str(playlist.get('playcount')),
             'tags': playlist.get('tags'),
             'source_url': 'https://www.kugou.com/yy/special/single/{}.html'.format(playlist.get('specialid')),
             'platform': self.__class__.__name__
             } for playlist in playlist_info
        ]
        return playlist_list

    # 获取歌单详情
    def get_playlist_detail(self, playlist_id):
        target_url = 'http://m.kugou.com/plist/list/{}?json=true'.format(playlist_id)

        response = requests.get(target_url,
                                headers=self.headers)

        response.raise_for_status()
        response_json = response.json()

        playlist_info = response_json['info']['list']

        source_url = 'https://www.kugou.com/yy/special/single/{}.html'.format(playlist_info.get('specialid'))
        img_url = playlist_info.get('imgurl').replace('{size}', '400')
        title = playlist_info.get('specialname')
        tags = [] if not playlist_info.get('tags') else [tag.get('tagname') for tag in playlist_info.get('tags')]
        description = playlist_info.get('intro')
        create_time = playlist_info.get('publishtime')
        subscribe_count = playlist_info.get('playcount')

        playlist_song_info = response_json['list']['list']['info']
        song_list = [
            {'song_id': song.get('hash'),
             'title': song.get('filename').split('-')[-1].strip(),
             'artist': song.get('filename').split('-')[0],
             'img_url': img_url,
             'source_url': 'https://www.kugou.com/song/#hash={}'.format(song.get('hash')),
             'platform': self.__class__.__name__,
             'platform_name': self.__class__.title
             } for song in playlist_song_info
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
        target_url = 'http://m.kugou.com/rank/list&json=true'

        response = requests.get(target_url,
                                headers=self.headers)

        response.raise_for_status()
        response_json = response.json()
        toplist_content = response_json.get('rank').get('list')
        toplist_list = [{
            'id': toplist.get('rankid'),
            'img_url': toplist.get('imgurl').replace('{size}', '400'),
            'title': toplist.get('rankname'),
            'tags': [],
            'platform': self.__class__.__name__
        } for toplist in toplist_content]

        return toplist_list

    # 获取排行榜歌单详情
    def get_toplist_detail(self, toplist_id):
        target_url = 'http://mobilecdnbj.kugou.com/api/v3/rank/info?rankid={}'.format(toplist_id)
        response = requests.get(target_url,
                                headers=self.headers)
        response.raise_for_status()
        response_json = response.json()
        assert response_json.get('errcode') == 0, '酷狗音乐排行榜歌单详情获取异常!\n请求地址:{}\n请求参数:{}\n返回结果:{}'.format(target_url, '',
                                                                                                       response.text)

        toplist_info = response_json.get('data')
        source_url = 'https://www.kugou.com/yy/rank/home/1-{}.html'.format(toplist_id),
        description = toplist_info.get('intro')
        img_url = toplist_info.get('imgurl').replace('{size}', '400')
        title = toplist_info.get('rankname')
        tags = []

        target_url = 'http://mobilecdnbj.kugou.com/api/v3/rank/song?pagesize=-1&page=1&rankid={}'.format(toplist_id)
        response = requests.get(target_url,
                                headers=self.headers)
        response.raise_for_status()
        response_json = response.json()
        assert response_json.get('errcode') == 0, '酷狗音乐排行榜歌单详情获取异常!\n请求地址:{}\n请求参数:{}\n返回结果:{}'.format(target_url, '',
                                                                                                       response.text)
        toplist_song_info = response_json['data']['info']
        song_list = [
            {'song_id': song.get('hash'),
             'title': song.get('filename').split('-')[-1].strip(),
             'artist': song.get('filename').split('-')[0],
             'img_url': img_url,
             'source_url': 'https://www.kugou.com/song/#hash={}'.format(song.get('hash')),
             'platform': self.__class__.__name__,
             'platform_name': self.__class__.title
             } for song in toplist_song_info if self._is_playable(song.get('privilege', 0))
        ]

        return {
            'source_url': source_url,
            'toplist_id': toplist_id,
            'img_url': img_url,
            'title': title,
            'tags': tags,
            'description': description,
            'song_list': song_list,
            'platform': self.__class__.__name__,
            'song_total': len(song_list)
        }

    # 搜索
    def search(self, keyword, page_num=1, page_size=20):

        # target_url = 'http://songsearch.kugou.com/song_search_v2?keyword={}&page={}&pagesize={}'.format(
        #     keyword,
        #     page_num,
        #     page_size)
        # response = requests.get(target_url,
        #                         headers=self.headers)

        target_url = 'https://complexsearch.kugou.com/v2/search/song'

        now = round(time.time() * 1000)
        text = '''NVPh5oo715z5DIWAeQlhMDsWXXQV4hwtbitrate=0callback=jQueryclienttime=%sclientver=2000dfid=-inputtype=0iscorrection=1isfuzzy=0keyword=%smid=%spage=%dpagesize=%dplatform=WebFilterprivilege_filter=0srcappid=2919tag=emuserid=-1uuid=%sNVPh5oo715z5DIWAeQlhMDsWXXQV4hwt''' % (
            now, keyword, now, page_num, page_size, now)
        sign = hashlib.md5(text.encode('utf-8')).hexdigest()
        parameters = {
            'callback': 'jQuery',
            'keyword': keyword,
            'page': str(page_num),
            'pagesize': str(page_size),
            'bitrate': '0',
            'isfuzzy': '0',
            'tag': 'em',
            'inputtype': '0',
            'platform': 'WebFilter',
            'userid': '-1',
            'clientver': '2000',
            'iscorrection': '1',
            'privilege_filter': '0',
            'srcappid': '2919',
            'clienttime': now,
            'mid': now,
            'uuid': now,
            'dfid': '-',
            'signature': sign.upper()
        }

        response = requests.get(target_url, params=parameters)
        response.raise_for_status()
        response_json = json.loads(response.text.lstrip('jQuery(').rstrip(')\n'))

        assert response_json.get('error_code') == 0, '酷狗音乐搜索歌曲失败!请求地址:{}\n请求参数:{}\n返回结果:{}'.format(target_url, '',
                                                                                                   response.text)

        search_info = response_json.get('data')

        total = search_info.get('total')
        if search_info.get('lists'):
            result = [
                {'song_id': song.get('FileHash'),
                 # 'title': song.get('OriSongName'),
                 'title': song.get('SongName').replace('<em>', '').replace('</em>', ''),
                 # 'artist': song.get('SingerName'),
                 'artist': song.get('SingerName').replace('<em>', '').replace('</em>', ''),
                 'artist_id': song.get('SingerId')[0] if song.get('SingerId') and song.get('SingerId')[0] != 0 else '',
                 'album': song.get('AlbumName'),
                 'album_id': song.get('AlbumID'),
                 'img_url': '/static/images/album.png',
                 'source_url': 'https://www.kugou.com/song/#hash={}'.format(song.get('FileHash')),
                 'platform': self.__class__.__name__,
                 'platform_name': self.__class__.title
                 } for song in search_info.get('lists')
            ]
        else:
            result = []

        return {'list': result, 'total': total}


if __name__ == '__main__':
    kugou = KugouMusic()
    kugou.get_song_play_url('86C62136A60108030A7E7A4543502485')
    # kugou._get_song_info('1E52D25621767A487828053B34E70FA4')
    # kugou.get_album_detail('965221')
    # kugou.get_playlist_detail('3397773')
    # kugou.get_artist_detail('3525')
    # kugou.get_toplist_detail('6666')
    # kugou.get_recommend_playlist()
    kugou.search('我的心太乱')
    # kugou.get_toplist()

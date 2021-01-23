from Music.platforms import BaseMusic
import requests
import json
import random
import time


class KuwoMusic(BaseMusic):
    title = '酷我音乐'

    def __init__(self):
        super(KuwoMusic, self).__init__()
        self.headers['CSRF'] = 'EPD2G1HA6QU'
        self.headers[
            'Cookie'] = '_ga=GA1.2.826457381.1601966209; _gid=GA1.2.2047788394.1602239607; Hm_lvt_cdb524f42f0ce19b169a8071123a4797=1601966209,1602061688,1602061747,1602239608; Hm_lpvt_cdb524f42f0ce19b169a8071123a4797=1602239608; kw_token=EPD2G1HA6QU'
        self.headers['Referer'] = 'http://www.kuwo.cn/'

    def _is_playable(self, num):
        play_flag = num != '1111'
        return play_flag

    # 获取歌曲播放地址
    def get_song_play_url(self, song_id):
        target_url = 'http://antiserver.kuwo.cn/anti.s?type=convert_url&rid={0}&format=mp3&response=url'.format(song_id)
        response = requests.get(target_url,
                                headers=self.headers)
        response.raise_for_status()
        play_url = response.text
        return {'platform': self.__class__.__name__,
                'play_url': play_url}

    # 获取歌曲歌词
    def get_song_lyric(self, song_id):
        target_url = 'http://m.kuwo.cn/newh5/singles/songinfoandlrc?musicId={}'.format(song_id)
        response = requests.get(target_url, headers=self.headers)
        response.raise_for_status()
        response_json = response.json()

        assert response_json.get('status') == 200, '酷我音乐歌词获取异常!\n请求地址:{}\n请求参数:{}\n返回结果:{}'.format(target_url, '',
                                                                                                   response.text)

        lyric_list = response_json['data']['lrclist']
        lyric = ''
        for lrc in lyric_list:
            str = lrc.get('lineLyric')
            t = float(lrc.get('time'))
            m = int(t / 60)
            s = int(t - m * 60)
            ms = int((t - m * 60 - s) * 100)
            lyric += '[{:02d}:{:02d}.{:02d}]{}\n'.format(m, s, ms, str)

        return {'platform': self.__class__.__name__,
                'lyric': lyric}

    # 获取专辑详情
    def get_album_detail(self, album_id):
        target_url = 'http://search.kuwo.cn/r.s?pn=0&rn=1000&stype=albuminfo&albumid={}&alflac=1&pcmp4=1&encoding=utf8&vipver=MUSIC_8.7.7.0_W4'.format(
            album_id)
        response = requests.get(target_url,
                                headers=self.headers)

        response.raise_for_status()
        response_json = json.loads(response.text.replace('\'', '"'))

        source_url = 'http://www.kuwo.cn/album_detail/{}'.format(album_id)
        img_url = response_json.get('img')
        title = response_json.get('name')
        description = response_json.get('info').replace('&lt;br&gt;', '  ').replace('&nbsp;', '')
        create_time = response_json.get('pub')

        song_list = [
            {'song_id': song.get('id'),
             'title': song.get('name'),
             'artist': song.get('artist'),
             'artist_id': song.get('artistid'),
             'album': title,
             'album_id': album_id,
             'img_url': img_url,
             'source_url': 'http://www.kuwo.cn/play_detail/{}'.format(song.get('id')),
             'platform': self.__class__.__name__,
             'platform_name': self.__class__.title
             } for song in response_json.get('musiclist') if self._is_playable(song['payInfo'].get('play', 0))
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
        target_url = 'http://search.kuwo.cn/r.s?stype=artistinfo&artistid={}&encoding=utf8'.format(artist_id)
        response = requests.get(target_url,
                                headers=self.headers)
        response.raise_for_status()
        response_json = json.loads(response.text.replace('\'', '"'))

        source_url = 'http://www.kuwo.cn/singer_detail/{}'.format(artist_id)
        img_url = response_json.get('hts_pic')
        title = response_json.get('name')
        description = response_json.get('desc')

        target_url = 'http://search.kuwo.cn/r.s?stype=artist2music&sortby=0&alflac=1&pcmp4=1&encoding=utf8&artistid={}&pn={}&rn={}'.format(
            artist_id, int(page_num) - 1, page_size)
        response = requests.get(target_url,
                                headers=self.headers)
        response.raise_for_status()
        response_json = json.loads(response.text.replace('\'', '"'))
        song_list = [
            {'song_id': song.get('musicrid'),
             'title': song.get('name'),
             'artist': song.get('artist'),
             'artist_id': song.get('artistid'),
             'album': song.get('album'),
             'album_id': song.get('albumid'),
             'img_url': img_url,
             'source_url': 'http://www.kuwo.cn/play_detail/{}'.format(song.get('musicrid')),
             'platform': self.__class__.__name__,
             'platform_name': self.__class__.title
             } for song in response_json.get('musiclist') if self._is_playable(song['payInfo'].get('play', 0))
        ]
        return {
            'source_url': source_url,
            'artist_id': artist_id,
            'img_url': img_url,
            'title': title,
            'description': description,
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

        # 接口不支持默认推荐 需要类目ID
        CATE_DICT = {
            1265: '经典',
            621: '网络',
            1879: '网红',
            180: '影视',
            578: '器乐',
            1877: '游戏',
            181: '二次元',
            393: '流行',
            389: '摇滚',
            392: '民谣',
            37: '华语'
        }
        # 随机选一个类目
        target_url = 'http://www.kuwo.cn/www/categoryNew/getPlayListInfoUnderCategory?type=taglist&digest=10000&id={}&start={}&count={}'.format(
            random.choice(list(CATE_DICT.keys())), (int(page_num) - 1) * int(page_size), int(page_size))
        response = requests.get(target_url,
                                headers=self.headers)

        response.raise_for_status()
        response_json = json.loads(response.text.strip())
        playlist_info = response_json['data'][0]['data']

        playlist_list = [
            {'id': playlist.get('id'),
             'img_url': playlist.get('img'),
             'title': playlist.get('name'),
             'tags': [],
             'source_url': 'http://www.kuwo.cn/playlist_detail/{}'.format(playlist.get('id')),
             'platform': self.__class__.__name__
             } for playlist in playlist_info
        ]

        return playlist_list

    # 获取歌单详情
    def get_playlist_detail(self, playlist_id):
        target_url = 'http://nplserver.kuwo.cn/pl.svc?op=getlistinfo&pn=0&rn=200&encode=utf-8&keyset=pl2012&pid={}&vipver=MUSIC_9.0.2.0_W1&newver=1'.format(
            playlist_id)

        response = requests.get(target_url,
                                headers=self.headers)

        response.raise_for_status()
        response_json = json.loads(response.text.strip())

        source_url = 'http://www.kuwo.cn/playlist_detail/{}'.format(playlist_id)
        img_url = response_json.get('pic')
        title = response_json.get('title')
        tags = [] if not response_json.get('tag') else response_json.get('tag').split(',')
        description = response_json.get('info')
        create_time = time.strftime("%Y-%m-%d", time.localtime(response_json.get('ctime')))
        subscribe_count = response_json.get('playnum')

        playlist_song_info = response_json['musiclist']
        song_list = [
            {'song_id': song.get('id'),
             'title': song.get('name'),
             'artist': song.get('artist'),
             'artist_id': song.get('artistid'),
             'album': song.get('album'),
             'album_id': song.get('albumid'),
             'img_url': img_url,
             'source_url': 'http://www.kuwo.cn/play_detail/{}'.format(song.get('id')),
             'platform': self.__class__.__name__,
             'platform_name': self.__class__.title
             } for song in playlist_song_info if self._is_playable(song['payInfo'].get('play', 0))
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
        target_url = 'http://www.kuwo.cn/api/www/bang/bang/bangMenu?httpsStatus=1'
        response = requests.get(target_url, headers=self.headers)
        response.raise_for_status()
        response_json = json.loads(response.text.strip())
        assert response_json.get('code') == 200, '酷我音乐排行榜获取异常!\n请求地址:{}\n请求参数:{}\n返回结果:{}'.format(target_url, '',
                                                                                                  response.text)
        toplist_content = [j for i in response_json.get('data') for j in i['list']]

        toplist_list = [{
            'id': toplist.get('sourceid'),
            'img_url': toplist.get('pic'),
            'title': toplist.get('name'),
            'tags': [],
            'source_url': 'http://www.kuwo.cn/rankList',
            'platform': self.__class__.__name__
        } for toplist in toplist_content]

        return toplist_list

    # 获取排行榜歌单详情
    def get_toplist_detail(self, toplist_id):
        # 这个接口很容易Gateway Timeout 增加重试
        target_url = 'http://www.kuwo.cn/api/www/bang/bang/bangMenu?httpsStatus=1'

        cnt = 1
        while cnt < 3:
            try:
                response = requests.get(target_url, headers=self.headers)
                if response.status_code == 200:
                    break
            except:
                cnt += 1

        response_json = json.loads(response.text.strip())
        assert response_json.get('code') == 200, '酷我音乐排行榜获取异常!\n请求地址:{}\n请求参数:{}\n返回结果:{}'.format(target_url, '',
                                                                                                  response.text)
        toplist_content = [j for i in response_json.get('data') for j in i['list'] if j['sourceid'] == toplist_id]

        if toplist_content:
            toplist_content = toplist_content[0]

        target_url = 'http://www.kuwo.cn/api/www/bang/bang/musicList?bangId={}&pn=0&rn=1000&httpsStatus=1'.format(
            toplist_id)
        cnt = 1
        while cnt < 3:
            try:
                response = requests.get(target_url, headers=self.headers)
                if response.status_code == 200:
                    break
            except:
                cnt += 1
        response_json = json.loads(response.text.strip())
        assert response_json.get('code') == 200, '酷我音乐排行榜获取异常!\n请求地址:{}\n请求参数:{}\n返回结果:{}'.format(target_url, '',
                                                                                                  response.text)
        song_info_list = response_json['data']['musicList']
        song_list = [
            {'song_id': song.get('rid'),
             'title': song.get('name'),
             'artist': song.get('artist'),
             'artist_id': str(song.get('artistid')) if song.get('artistid') else '',
             'album': song.get('album'),
             'album_id': str(song.get('albumid')) if song.get('albumid') else '',
             'img_url': song.get('albumpic'),
             'source_url': 'http://www.kuwo.cn/play_detail/{}'.format(song.get('rid')),
             'platform': self.__class__.__name__,
             'platform_name': self.__class__.title
             } for song in song_info_list if self._is_playable(song['payInfo'].get('play', 0))
        ]

        return {
            'source_url': 'http://www.kuwo.cn/rankList',
            'toplist_id': toplist_id,
            'img_url': toplist_content.get('pic'),
            'title': toplist_content.get('name'),
            'tags': [],
            'description': toplist_content.get('intro'),
            'song_list': song_list,
            'platform': self.__class__.__name__,
            'song_total': len(song_list)
        }

    # 搜索
    def search(self, keyword, page_num=1, page_size=20):
        target_url = 'http://www.kuwo.cn/api/www/search/searchMusicBykeyWord?key={}&pn={}&rn={}'.format(keyword,
                                                                                                        page_num,
                                                                                                        page_size)
        response = requests.get(target_url,
                                headers=self.headers)

        response.raise_for_status()
        response_json = json.loads(response.text.strip())
        assert response_json.get('code') == 200, '酷我音乐搜索歌曲失败!请求地址:{}\n请求参数:{}\n返回结果:{}'.format(target_url, '',
                                                                                               response.text)

        search_info = response_json.get('data')

        total = search_info.get('total')
        if search_info.get('list'):
            result = [
                {'song_id': song.get('rid'),
                 'title': song.get('name'),
                 'artist': song.get('artist'),
                 'artist_id': str(song.get('artistid')) if song.get('artistid') else '',
                 'album': song.get('album'),
                 'album_id': str(song.get('albumid')) if song.get('albumid') else '',
                 'img_url': song.get('albumpic'),
                 'source_url': 'http://www.kuwo.cn/play_detail/{}'.format(song.get('rid')),
                 'platform': self.__class__.__name__,
                 'platform_name': self.__class__.title
                 } for song in search_info.get('list') if self._is_playable(song['payInfo'].get('play', 0))
            ]
        else:
            result = []

        return {'list': result, 'total': total}


if __name__ == '__main__':
    kuwo = KuwoMusic()
    # kuwo.get_song_play_url('142655450')
    # kuwo.get_song_lyric('142655450')
    # kuwo.get_album_detail('14968708')
    # kuwo.get_artist_detail('896')
    kuwo.get_playlist_detail('3130463678')
    kuwo.get_toplist_detail('145')
    # kuwo.search('彩虹')

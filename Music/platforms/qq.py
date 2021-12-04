from Music.platforms import BaseMusic
import requests
import time


class QQMusic(BaseMusic):

    title = 'QQ音乐'
    is_support_playlist = 2
    is_support_toplist = 2

    def __init__(self):

        super(QQMusic, self).__init__()
        self.headers['referer'] = 'https://y.qq.com/'

    def _get_img_url(self, mid, type='album'):
        assert type in ('album', 'artist'), 'type 枚举值 仅支持 album 和 artist'

        if type == 'artist':
            category = 'T001R300x300M000'
        else:
            category = 'T002R300x300M000'

        url = f'https://y.gtimg.cn/music/photo_new/{category + mid}.jpg'
        return url

    def _is_playable(self, num):

        switch_flag = bin(num)[2:-1][::-1]
        play_flag = str(switch_flag[0])
        try_flag = str(switch_flag[13])
        #play_flag = (num != 1) and (int(bin(num)[2:-1][::-1][0]) == 1)
        return (play_flag == '1') or (play_flag == '1' and try_flag == '1')

    # 获取歌曲播放地址
    def get_song_play_url(self, song_id):

        target_url = f'https://u.y.qq.com/cgi-bin/musicu.fcg?format=json&data=%7B%22req_0%22%3A%7B%22module%22%3A%22vkey.GetVkeyServer%22%2C%22method%22%3A%22CgiGetVkey%22%2C%22param%22%3A%7B%22guid%22%3A%2210000%22%2C%22songmid%22%3A%5B%22{song_id}%22%5D%2C%22songtype%22%3A%5B0%5D%2C%22uin%22%3A%220%22%2C%22loginflag%22%3A1%2C%22platform%22%3A%2220%22%7D%7D%2C%22comm%22%3A%7B%22uin%22%3A0%2C%22format%22%3A%22json%22%2C%22ct%22%3A20%2C%22cv%22%3A0%7D%7D'
        response = requests.get(target_url,
                                headers=self.headers)

        response.raise_for_status()
        response_json = response.json()

        assert response_json.get('code') == 0, 'QQ音乐歌曲播放地址获取异常!\n' + response.text
        song_play_info = response_json.get('req_0').get('data')

        assert song_play_info.get('midurlinfo')[0].get('purl') != '', '版权原因 暂无法播放 请更换其他平台'

        play_url = song_play_info.get('sip')[0] + song_play_info.get('midurlinfo')[0].get('purl')

        return {'platform': self.__class__.__name__,
                'play_url': play_url}

    # 获取歌曲歌词
    def get_song_lyric(self, song_id):
        target_url = f'https://c.y.qq.com/lyric/fcgi-bin/fcg_query_lyric_new.fcg?format=json&nobase64=1&songmid={song_id}'

        response = requests.get(target_url,
                                headers=self.headers)

        response.raise_for_status()
        response_json = response.json()

        assert response_json.get('code') == 0, 'QQ音乐歌词获取异常!\n' + response.text

        lyric = response_json.get('lyric')
        return {'platform': self.__class__.__name__,
                'lyric': lyric}

    # 获取专辑详情
    def get_album_detail(self, album_id):
        target_url = f'https://i.y.qq.com/v8/fcg-bin/fcg_v8_album_info_cp.fcg?albummid={album_id}&format=json'
        response = requests.get(target_url,
                                headers=self.headers)

        response.raise_for_status()
        response_json = response.json()

        assert response_json.get('code') == 0, 'QQ音乐专辑获取异常!\n' + response.text

        album_info = response_json.get('data')

        source_url = f'https://y.qq.com/n/yqq/album/{album_id}.html'
        img_url = self._get_img_url(album_id)
        title = album_info.get('name')
        description = album_info.get('desc')
        create_time = album_info.get('aDate')

        song_list = [
            {'song_id': song.get('songmid'),
             'title': song.get('songname'),
             'artist': song.get('singer')[0].get('name'),
             'artist_id': song.get('singer')[0].get('mid'),
             'album': song.get('albumname'),
             'album_id': song.get('albummid'),
             'img_url': self._get_img_url(song.get('albummid')),
             'source_url': f"https://y.qq.com/n/yqq/song/{song.get('songmid')}.html",
             'platform': self.__class__.__name__,
             'platform_name': self.__class__.title
             } for song in album_info.get('list') if self._is_playable(song.get('switch'))
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
    def get_artist_detail(self, artist_id,page_num=1,page_size=100):
        target_url = f'https://i.y.qq.com/v8/fcg-bin/fcg_v8_singer_track_cp.fcg?format=json&begin={page_size * (page_num - 1)}&num={page_size}&order=listen&singermid={artist_id}'
        response = requests.get(target_url,
                                headers=self.headers)

        response.raise_for_status()
        response_json = response.json()

        assert response_json.get('code') == 0, 'QQ音乐歌手获取异常!\n' + response.text

        artist_info = response_json.get('data')

        source_url = f'https://y.qq.com/n/yqq/singer/{artist_id}.html'
        img_url = self._get_img_url(artist_id, 'artist')
        title = artist_info.get('singer_name')

        song_list = [
            {'song_id': artist.get('musicData').get('songmid'),
             'title': artist.get('musicData').get('songname'),
             'artist': artist.get('musicData').get('singer')[0].get('name'),
             'artist_id': artist.get('musicData').get('singer')[0].get('mid'),
             'album': artist.get('musicData').get('albumname'),
             'album_id': artist.get('musicData').get('albummid'),
             'img_url': self._get_img_url(artist.get('musicData').get('albummid')),
             'source_url': f"https://y.qq.com/n/yqq/song/{artist.get('musicData').get('songmid')}.html",
             'platform': self.__class__.__name__,
             'platform_name': self.__class__.title
             } for artist in artist_info.get('list') if self._is_playable(artist.get('musicData').get('switch'))
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
        target_url = f'https://c.y.qq.com/splcloud/fcgi-bin/fcg_get_diss_by_tag.fcg?format=json&inCharset=GB2312&outCharset=utf-8&categoryId=10000000&sin={(page_num - 1) * page_size}&ein={page_size * page_num - 1}'
        response = requests.get(target_url,
                                headers=self.headers)

        response.raise_for_status()
        response_json = response.json()

        assert response_json.get('code') == 0, 'QQ音乐推荐歌单获取异常!\n' + response.text

        playlist_info = response_json.get('data').get('list')

        playlist_list = [
            {'id': str(playlist.get('dissid')),
             'img_url': playlist.get('imgurl'),
             'title': playlist.get('dissname'),
             'subscribe_count': self.num_to_str(playlist.get('listennum')),
             'tags': [],
             'source_url': f'https://y.qq.com/#type=taoge&id={playlist.get("dissid")}',
             'platform': self.__class__.__name__
             } for playlist in playlist_info
        ]

        return playlist_list

    # 获取歌单详情
    def get_playlist_detail(self, playlist_id):
        target_url = f'https://i.y.qq.com/qzone-music/fcg-bin/fcg_ucc_getcdinfo_byids_cp.fcg?type=1&inCharset=GB2312&outCharset=utf-8&format=json&disstid={playlist_id}'

        response = requests.get(target_url,
                                headers=self.headers)

        response.raise_for_status()
        response_json = response.json()

        assert response_json.get('code') == 0, 'QQ音乐歌单详情获取异常!\n' + response.text

        playlist_info = response_json.get('cdlist')[0]

        source_url = f'https://y.qq.com/n/yqq/playlist/{playlist_id}.html'
        img_url = playlist_info.get('logo')
        title = playlist_info.get('dissname')
        tags = [] if not playlist_info.get('tags') else [tag.get('name') for tag in playlist_info.get('tags')]
        description = playlist_info.get('desc').replace('<br>','')
        create_time = time.strftime("%Y-%m-%d", time.localtime(playlist_info.get('ctime')))
        subscribe_count = playlist_info.get('visitnum')
        song_list = [
            {'song_id': song.get('songmid'),
             'title': song.get('songname'),
             'artist': song.get('singer')[0].get('name'),
             'artist_id': song.get('singer')[0].get('mid'),
             'album': song.get('albumname'),
             'album_id': song.get('albummid'),
             'img_url': self._get_img_url(song.get('albummid')),
             'source_url': f"https://y.qq.com/n/yqq/song/{song.get('songmid')}.html",
             'platform': self.__class__.__name__,
             'platform_name':self.__class__.title
             } for song in playlist_info.get('songlist') if self._is_playable(song.get('switch'))
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
        target_url = 'https://c.y.qq.com/v8/fcg-bin/fcg_myqq_toplist.fcg?format=json'

        response = requests.get(target_url,
                                headers=self.headers)

        response.raise_for_status()
        response_json = response.json()

        assert response_json.get('code') == 0, 'QQ音乐排行榜获取异常!\n' + response.text

        toplist_content = response_json.get('data').get('topList')

        toplist_list = [{
            'id': toplist.get('id'),
            'img_url': toplist.get('picUrl'),
            'title': toplist.get('topTitle'),
            'tags': [],
            'subscribe_count': self.num_to_str(toplist.get('listenCount')),
            'source_url': f'https://y.qq.com/n/yqq/toplist/{toplist.get("id")}.html',
            'platform': self.__class__.__name__
        } for toplist in toplist_content if str(toplist.get('id')) != '75'] # 有声榜特殊 剔除

        return toplist_list

    # 获取排行榜歌单详情
    def get_toplist_detail(self, toplist_id):
        target_url = f'https://c.y.qq.com/v8/fcg-bin/fcg_v8_toplist_cp.fcg?type=top&topid={toplist_id}'

        response = requests.get(target_url,
                                headers=self.headers)

        response.raise_for_status()
        response_json = response.json()

        assert response_json.get('code') == 0, 'QQ音乐排行榜歌单详情获取异常!\n' + response.text

        toplist_info = response_json.get('topinfo')
        source_url = f'https://y.qq.com/n/yqq/toplist/{toplist_id}.html'
        img_url = toplist_info.get('pic_v12')
        title = toplist_info.get('ListName')
        tags = []
        description = toplist_info.get('info').replace('<br>','')
        create_time = response_json.get('date')
        subscribe_count = toplist_info.get('listennum')
        song_list = [
            {'song_id': song.get('data').get('songmid'),
             'title': song.get('data').get('songname'),
             'artist': song.get('data').get('singer')[0].get('name'),
             'artist_id': song.get('data').get('singer')[0].get('mid'),
             'album': song.get('data').get('albumname'),
             'album_id': song.get('data').get('albummid'),
             'img_url': self._get_img_url(song.get('data').get('albummid')),
             'source_url': f"https://y.qq.com/n/yqq/song/{song.get('data').get('songmid')}.html",
             'platform': self.__class__.__name__,
             'platform_name': self.__class__.title
             } for song in response_json.get('songlist') if self._is_playable(song.get('data').get('switch'))
        ]

        return {
            'source_url': source_url,
            'toplist_id': toplist_id,
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
        #target_url = f'https://c.y.qq.com/soso/fcgi-bin/search_for_qq_cp?format=json&w={keyword}&p={page_num}&n={page_size}'
        target_url = f'https://c.y.qq.com/soso/fcgi-bin/client_search_cp?g_tk=938407465&uin=0&format=json&inCharset=utf-8&outCharset=utf-8&notice=0&platform=h5&needNewCode=1&w={keyword}&zhidaqu=1&catZhida=1&t=0&flag=1&ie=utf-8&sem=1&aggr=0&perpage=20&n={page_size}&p={page_num}&remoteplace=txt.mqq.all&_=1459991037831'
        response = requests.get(target_url,
                                headers=self.headers)

        response.raise_for_status()
        response_json = response.json()

        assert response_json.get('code') == 0, 'QQ音乐搜索歌曲失败! 失败详情:' + response.text

        search_info = response_json.get('data').get('song')

        total = search_info.get('totalnum')
        if search_info.get('list'):
            result = [
                {'song_id': song.get('songmid'),
                 'title': song.get('songname'),
                 'artist': song.get('singer')[0].get('name'),
                 'artist_id': song.get('singer')[0].get('mid'),
                 'album': song.get('albumname'),
                 'album_id': song.get('albummid'),
                 'img_url': self._get_img_url(song.get('albummid')),
                 'source_url': f'https://y.qq.com/#type=song&mid=${song.get("songmid")}&tpl=yqq_song_detail',
                 'platform': self.__class__.__name__,
                 'platform_name': self.__class__.title
                 } for song in search_info.get('list') if self._is_playable(song.get('switch'))
            ]

        else:
            result = []
        return {'list': result,'total': total}


if __name__ == '__main__':
    q_music = QQMusic()

    # q_music.get_album_detail('002iQSAu0kuQ4H')
    # q_music.get_recommend_playlist(page_num=3,page_size=30)
    # q_music.get_playlist_detail('1767321860')
    # q_music.get_toplist()
    # q_music.get_toplist_detail(27)
    # q_music.search('彩虹')
    q_music.get_artist_detail('0025NhlN2yWrP4',page_num=2)

    # q_music.get_song_play_url('0039MnYb0qxYhV')
    # q_music.get_song_lyric('0039MnYb0qxYhV')

from Music.platforms import BaseMusic
import requests
import json
import re
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5 as PKCS1_cipher
from Crypto import Random
from Crypto.Cipher import AES
import base64
from hashlib import md5
from urllib import parse
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
import time
import os


class MiguMusic(BaseMusic):
    title = '咪咕音乐'

    def __init__(self):
        super(MiguMusic, self).__init__()
        self.phone_number = 'xxxx'  # 咪咕音乐账号
        self.password = 'xxxx'  # 咪咕音乐密码
        self.headers['Referer'] = 'http://music.migu.cn/v3/music/player/audio?from=migu'
        self.cookies_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'migu_cookies')
        if os.path.exists(self.cookies_path):
            self.save_cookies(self.phone_number, self.password)

    def _pad(self, data):
        length = 16 - (len(data) % 16)
        return data + (chr(length) * length).encode()

    def _bytes_to_key(self, data, salt, output=48):
        assert len(salt) == 8, len(salt)
        data += salt
        key = md5(data).digest()
        final_key = key
        while len(final_key) < output:
            key = md5(key + data).digest()
            final_key += key
        return final_key[:output]

    def _aes_encrypt(self, message, passphrase):
        message = message.encode()
        passphrase = passphrase.encode()
        salt = Random.new().read(8)
        key_iv = self._bytes_to_key(passphrase, salt, 32 + 16)
        key = key_iv[:32]
        iv = key_iv[32:]
        aes = AES.new(key, AES.MODE_CBC, iv)
        return base64.b64encode(b"Salted__" + salt + aes.encrypt(self._pad(message))).decode()

    def _get_song_list(self, content):
        song_list = []
        song_content_list = re.findall(
            r'<div class="row J_CopySong"\ndata-aid="(.*?)"\ndata-cid="(.*?)".*?/v3/music/artist/(.*?)" target="_blank".*?(/v3/music/album/\d+|/v3/music/digital_album/\d+|class="J-btn-share)".*?data-share=\'(.*?)\'\n>',
            content, re.S)

        for song_content in song_content_list:
            song_json = json.loads(song_content[4])
            song_list.append(
                {
                    'song_id': song_content[1],
                    'title': song_json.get('title'),
                    'artist': song_json.get('singer'),
                    'artist_id': song_content[2],
                    'album': song_json.get('album'),
                    'album_id': song_content[0] if song_content[0] else str(song_content[3].split('/')[-1]),
                    'img_url': 'http:' + song_json.get('imgUrl'),
                    'playable': True,
                    'source_url': 'https://music.migu.cn/v3/music/song/' + str(song_content[1]),
                    'platform': self.__class__.__name__,
                    'platform_name': self.__class__.title
                }
            )

        return song_list

    def get_recommend_playlist(self, page_size=20, page_num=1):
        target_url = 'https://music.migu.cn/v3/music/playlist?page={}'.format(page_num)

        response = requests.get(target_url,
                                headers=self.headers)

        response.raise_for_status()

        content = response.text

        playlist_re = re.findall(
            r'<li>.*?data-original="(.*?)" class="img-full.*?data-id="(.*?)" data-origin=.*?title=".*?">(.*?)</a>.*?<i class="iconfont cf-bofangliang"></i>\n(.*?)\n</div>\n</div>\n<div class="item-action">.*?</li>',
            content, re.S)

        assert playlist_re, '咪咕音乐推荐歌单异常!\nURL:{}\n正则匹配失败'.format(target_url)

        playlist_list = [
            {'id': str(playlist[1]),
             'img_url': 'http:' + playlist[0],
             'title': playlist[2],
             'subscribe_count': (playlist[3]),
             'tags': [],
             'source_url': 'http://music.migu.cn/v3/music/playlist/{}'.format(playlist[1]),
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
        target_url = 'http://music.migu.cn/v3/music/playlist/' + str(playlist_id)

        response = requests.get(target_url, headers=self.headers)

        response.raise_for_status()
        content = response.text

        palylist_detail = re.search(
            r'class="thumb-img"\nsrc="(.*?)"\nalt.*?<div class="content">\n<h1 class="title">(.*?)</h1>.*?<span>播放量：</span>\n(.*?)\n</div>.*?<span>标签：</span>\n(.*?)\n</div>.*?<div class="intro-details J_IntroDetails">(.*?)</div>.*?</div>',
            content, re.S).groups()

        source_url = 'https://music.migu.cn/v3/music/playlist' + str(playlist_id)
        img_url = 'http:' + palylist_detail[0]
        tags = re.findall(r'<i>(.*?)</i>', palylist_detail[3], re.S)
        title = palylist_detail[1]
        subscribe_count = palylist_detail[2]
        description = palylist_detail[4]
        song_list = []
        song_list.extend(self._get_song_list(content))

        # 寻找下一页
        next_content = re.search(r'<div class="page">.*?<a href="(.*?) class="page-c iconfont cf-next-page"></a>',
                                 content, re.S)
        while next_content:
            next_url = 'https://music.migu.cn' + re.findall(r'<a href="(.*?)"', next_content.groups()[0])[-1]
            content = requests.get(next_url, headers=self.headers).text
            song_list.extend(self._get_song_list(content))
            next_content = re.search(r'<div class="page">.*?<a href="(.*?) class="page-c iconfont cf-next-page"></a>',
                                     content, re.S)

        return {
            'source_url': source_url,
            'playlist_id': playlist_id,
            'img_url': img_url,
            'title': title,
            'tags': tags,
            'description': description,
            'subscribe_count': subscribe_count,
            'song_list': song_list,
            'platform': self.__class__.__name__,
            'song_total': len(song_list)
        }

    # 获取歌曲播放地址
    def get_song_play_url(self, song_id):
        '''
        获取歌曲播放地址
        :param song_id: ID
        :return: 返回歌曲播放地址
        '''

        publicKey = "-----BEGIN PUBLIC KEY-----\nMIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC8asrfSaoOb4je+DSmKdriQJKW\nVJ2oDZrs3wi5W67m3LwTB9QVR+cE3XWU21Nx+YBxS0yun8wDcjgQvYt625ZCcgin\n2ro/eOkNyUOTBIbuj9CvMnhUYiR61lC1f1IGbrSYYimqBVSjpifVufxtx/I3exRe\nZosTByYp4Xwpb1+WAQIDAQAB\n-----END PUBLIC KEY-----"
        key = '4ea5c508a6566e76240543f8feb06fd457777be39549c4016436afda65d2330e'

        cipher = PKCS1_cipher.new(RSA.importKey(str(publicKey)))
        secKey = parse.quote(base64.b64encode(cipher.encrypt(bytes(key.encode("utf8")))).decode())

        aesResult = parse.quote(
            self._aes_encrypt('{{"copyrightId":"{}","type":2,"auditionsFlag":0}}'.format(song_id), key))

        target_url = 'http://music.migu.cn/v3/api/music/audioPlayer/getPlayInfo?dataType=2&data={aesResult}&secKey={secKey}'.format(
            aesResult=aesResult, secKey=secKey)

        with open(self.cookies_path, 'r') as f:
            cookies = json.load(f)
        song_json = requests.get(target_url, headers=self.headers, cookies=cookies).json()

        # 若cookies失效则重试
        if song_json.get('returnCode') != '000000':
            self.save_cookies(self.phone_number, self.password)
            with open(self.cookies_path, 'r') as f:
                cookies = json.load(f)
            song_json = requests.get(target_url, headers=self.headers, cookies=cookies).json()

        play_url = 'https:' + song_json['data'].get('playUrl')
        return {'platform': self.__class__.__name__,
                'play_url': play_url}

    # 获取歌曲歌词
    def get_song_lyric(self, song_id):
        '''
        获取歌曲歌词
        :param song_id: 歌曲ID
        :return: 歌词
        '''
        target_url = 'http://music.migu.cn/v3/api/music/audioPlayer/getLyric?copyrightId={}'.format(song_id)

        response = requests.get(target_url,
                                headers=self.headers)

        response.raise_for_status()
        lyric_info = response.json()
        lyric = lyric_info.get('lyric')
        return {'platform': self.__class__.__name__,
                'lyric': lyric}

    # 获取歌手详情
    def get_artist_detail(self, artist_id):
        target_url = 'https://music.migu.cn/v3/music/artist/{}/song'.format(artist_id)

        response = requests.get(target_url, headers=self.headers)

        response.raise_for_status()
        content = response.text

        artist_detail = re.search(
            r'<div class="artist-avatar">.*?<img\nsrc="(.*?)" alt=.*?<div class="artist-name">\n<a href.*?">(.*?)</a>.*?<div class="content">(.*?)</div>',
            content, re.S).groups()

        img_url = 'http:' + artist_detail[0]
        title = artist_detail[1]
        description = artist_detail[2][:1000].strip()
        song_list = []
        song_list.extend(self._get_song_list(content))
        # 寻找下一页
        page_num = 0
        next_content = re.search(r'<a class="pagination-next" href="(.*?)"><i>', content, re.S)
        while next_content and page_num < 3:  # 歌手最多三页
            next_url = 'https://music.migu.cn' + next_content.groups()[0]
            content = requests.get(next_url, headers=self.headers).text
            song_list.extend(self._get_song_list(content))
            next_content = re.search(r'<a class="pagination-next" href="(.*?)"><i>', content, re.S)
            page_num += 1

        return {
            'source_url': 'https://music.migu.cn/v3/music/artist/{}'.format(artist_id),
            'artist_id': artist_id,
            'img_url': img_url,
            'title': title,
            'description': description,
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
        target_url = 'https://music.migu.cn/v3/music/album/{}'.format(album_id)

        response = requests.get(target_url, headers=self.headers)

        response.raise_for_status()
        content = response.text

        album_detail = re.search(
            r'class="thumb-img"\nsrc="(.*?)"\nalt.*?<div class="content">\n<h1 class="title">(.*?)</h1>.*?<span>发行时间：</span>(.*?)</div>.*?<div class="intro" title="(.*?)">',
            content, re.S).groups()

        img_url = 'http:' + album_detail[0]
        title = album_detail[1]
        create_time = album_detail[2]
        description = album_detail[3].strip()
        song_list = self._get_song_list(content)

        return {
            'source_url': target_url,
            'album_id': album_id,
            'img_url': img_url,
            'title': title,
            'song_list': song_list,
            'description': description,
            'create_time': create_time,
            'platform': self.__class__.__name__,
            'song_total': len(song_list)

        }

    # 获取排行榜
    def get_toplist(self):
        '''
        获取所有排行榜
        :return: list
        '''
        # 咪咕榜单暂无接口 需手动设定榜单
        DEFAULT_TOPLIST_LIST = [
            {
                'id': 'jianjiao_newsong',
                'title': '尖叫新歌榜',
                'img_url': 'http:////cdnmusic.migu.cn/tycms_picture/20/02/36/20020512065402_360x360_2997.png',
                'source_url': 'https://music.migu.cn/v3/music/top/jianjiao_newsong',
                'platform': self.__class__.__name__
            },
            {
                'id': 'jianjiao_hotsong',
                'title': '尖叫热歌榜',
                'img_url': 'http://cdnmusic.migu.cn/tycms_picture/20/04/99/200408163640868_360x360_6587.png',
                'source_url': 'https://music.migu.cn/v3/music/top/jianjiao_hotsong',
                'platform': self.__class__.__name__
            },
            {
                'id': 'jianjiao_original',
                'title': '尖叫原创榜',
                'img_url': 'http://cdnmusic.migu.cn/tycms_picture/20/04/99/200408163702795_360x360_1614.png',
                'source_url': 'https://music.migu.cn/v3/music/top/jianjiao_original',
                'platform': self.__class__.__name__
            },
            {
                'id': 'migumusic',
                'title': '音乐榜',
                'img_url': 'http://cdnmusic.migu.cn/tycms_picture/20/05/136/200515161733982_360x360_1523.png',
                'source_url': 'https://music.migu.cn/v3/music/top/migumusic',
                'platform': self.__class__.__name__
            },
            {
                'id': 'movies',
                'title': '影视榜',
                'img_url': 'http://cdnmusic.migu.cn/tycms_picture/20/05/136/200515161848938_360x360_673.png',
                'source_url': 'https://music.migu.cn/v3/music/top/movies',
                'platform': self.__class__.__name__
            },
            {
                'id': 'mainland',
                'title': '内地榜',
                'img_url': 'http://cdnmusic.migu.cn/tycms_picture/20/08/231/200818095104122_327x327_4971.png',
                'source_url': 'https://music.migu.cn/v3/music/top/mainland',
                'platform': self.__class__.__name__
            },
            {
                'id': 'hktw',
                'title': '港台榜',
                'img_url': 'http://cdnmusic.migu.cn/tycms_picture/20/08/231/200818095125191_327x327_2382.png',
                'source_url': 'https://music.migu.cn/v3/music/top/hktw',
                'platform': self.__class__.__name__
            },
            {
                'id': 'eur_usa',
                'title': '欧美榜',
                'img_url': 'http://cdnmusic.migu.cn/tycms_picture/20/08/231/200818095229556_327x327_1383.png',
                'source_url': 'https://music.migu.cn/v3/music/top/eur_usa',
                'platform': self.__class__.__name__
            },
            {
                'id': 'jpn_kor',
                'title': '日韩榜',
                'img_url': 'http://cdnmusic.migu.cn/tycms_picture/20/08/231/200818095259569_327x327_4628.png',
                'source_url': 'https://music.migu.cn/v3/music/top/jpn_kor',
                'platform': self.__class__.__name__
            },
            {
                'id': 'coloring',
                'title': '彩铃榜',
                'img_url': 'http://cdnmusic.migu.cn/tycms_picture/20/08/231/200818095356693_327x327_7955.png',
                'source_url': 'https://music.migu.cn/v3/music/top/coloring',
                'platform': self.__class__.__name__
            },
            {
                'id': 'ktv',
                'title': 'KTV榜',
                'img_url': 'http://cdnmusic.migu.cn/tycms_picture/20/08/231/200818095414420_327x327_4992.png',
                'source_url': 'https://music.migu.cn/v3/music/top/ktv',
                'platform': self.__class__.__name__
            },
            {
                'id': 'network',
                'title': '网络榜',
                'img_url': 'http://cdnmusic.migu.cn/tycms_picture/20/08/231/200818095442606_327x327_1298.png',
                'source_url': 'https://music.migu.cn/v3/music/top/network',
                'platform': self.__class__.__name__
            },
            {
                'id': 'itunes',
                'title': '美国iTunes榜',
                'img_url': 'http://cdnmusic.migu.cn/tycms_picture/20/08/231/200818095755771_327x327_9250.png',
                'source_url': 'https://music.migu.cn/v3/music/top/itunes',
                'platform': self.__class__.__name__
            },
            {
                'id': 'billboard',
                'title': '美国billboard榜',
                'img_url': 'http://cdnmusic.migu.cn/tycms_picture/20/08/231/20081809581365_327x327_4636.png',
                'source_url': 'https://music.migu.cn/v3/music/top/billboard',
                'platform': self.__class__.__name__
            },
            {
                'id': 'hito',
                'title': 'Hito中文榜',
                'img_url': 'http://cdnmusic.migu.cn/tycms_picture/20/08/231/200818095834912_327x327_5042.png',
                'source_url': 'https://music.migu.cn/v3/music/top/hito',
                'platform': self.__class__.__name__
            },
            {
                'id': 'top_mainland',
                'title': '中国TOP排行榜',
                'img_url': 'http://cdnmusic.migu.cn/tycms_picture/20/08/231/200818095858473_327x327_7022.png',
                'source_url': 'https://music.migu.cn/v3/music/top/top_mainland',
                'platform': self.__class__.__name__
            },
            {
                'id': 'mnet',
                'title': '韩国Melon榜',
                'img_url': 'http://cdnmusic.migu.cn/tycms_picture/20/08/231/200818095926828_327x327_3277.png',
                'source_url': 'https://music.migu.cn/v3/music/top/mnet',
                'platform': self.__class__.__name__
            },
            {
                'id': 'uk',
                'title': '英国UK榜',
                'img_url': 'http://cdnmusic.migu.cn/tycms_picture/20/08/231/200818095950791_327x327_8293.png',
                'source_url': 'https://music.migu.cn/v3/music/top/uk',
                'platform': self.__class__.__name__
            }
        ]
        return DEFAULT_TOPLIST_LIST

    # 获取排行榜歌单详情
    def get_toplist_detail(self, toplist_id):
        '''
        排行榜也是歌单 可调歌单详情获取内容
        :param toplist_id:  排行榜ID
        :return:
        '''
        target_url = 'https://music.migu.cn/v3/music/top/' + str(toplist_id)

        response = requests.get(target_url, headers=self.headers)

        response.raise_for_status()
        content = response.text

        toplist_detail = re.search(
            r'data-src="(.*?)"  id="top_cover".*?<div class="desc">\n<div class="top-title">(.*?)</div>\n<div class="update-time">(.*?)</div>',
            content, re.S).groups()

        img_url = 'http:' + toplist_detail[0]
        title = toplist_detail[1]
        description = toplist_detail[2]
        song_list = []
        song_content_list = re.findall(
            r'songlist-item" data-cid="(.*?)".*?/v3/music/artist/(.*?)".*?data-share="(.*?)"', content, re.S)
        for song_content in song_content_list:
            song_json = json.loads(song_content[2].replace('&#34;', '"'))
            song_list.append(
                {
                    'song_id': song_content[0],
                    'title': song_json.get('title'),
                    'artist': song_json.get('singer'),
                    'artist_id': song_content[1],
                    'album': '',
                    'album_id': '',
                    'img_url': 'http:' + song_json.get('imgUrl'),
                    'playable': True,
                    'source_url': 'https://music.migu.cn/v3/music/song/' + str(song_content[1]),
                    'platform': self.__class__.__name__,
                    'platform_name': self.__class__.title
                }
            )

        return {
            'source_url': target_url,
            'toplist_id': toplist_id,
            'img_url': img_url,
            'title': title,
            'description': description,
            'song_list': song_list,
            'platform': self.__class__.__name__,
            'song_total': len(song_list)
        }

    # 搜索
    def search(self, keyword, page_num=1, page_size=20):
        target_url = 'http://pd.musicapp.migu.cn/MIGUM3.0/v1.0/content/search_all.do'

        data = {
            'ua': 'Android_migu',
            'version': '5.0.1',
            'text': keyword,
            'pageNo': str(page_num),
            'pageSize': page_size,
            'searchSwitch': '{"song":1,"album":0,"singer":0,"tagSong":0,"mvSong":0,"songlist":0}',
        }

        response = requests.get(target_url,
                                params=data,
                                headers={
                                    'Referer': 'https://m.music.migu.cn/',
                                    'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.75 Mobile Safari/537.36'
                                })

        response.raise_for_status()
        search_info = response.json()

        assert search_info.get('code') == '000000', '咪咕音乐搜索歌曲失败!请求地址:{}\n请求参数:{}\n返回结果:{}'.format(target_url, data,
                                                                                                  response.text)

        total = search_info.get('songResultData').get('totalCount')
        result = [{
            'song_id': data.get('copyrightId'),
            'title': data.get('name'),
            'artist': data.get('singers')[0].get('name') if data.get('singers') else '',
            'artist_id': data.get('singers')[0].get('id') if data.get('singers') else '',
            'album': data.get('albums')[0].get('name') if data.get('albums') else '',
            'album_id': data.get('albums')[0].get('id') if data.get('albums') else '',
            'img_url': data.get('imgItems')[-1].get('img'),
            'playable': True,
            'source_url': 'https://music.migu.cn/v3/music/song/{}'.format(data.get('copyrightId')),
            'platform': self.__class__.__name__,
            'platform_name': self.__class__.title
        } for data in search_info.get('songResultData').get('result') if data.get('isInSalesPeriod') != '1']

        return {
            'list': result,
            'total': total
        }

    def save_cookies(self, phone_number='', password=''):

        options = Options()
        options.add_argument('--headless')
        driver = webdriver.Chrome(options=options)
        driver.get('https://music.migu.cn/v3')
        actions = ActionChains(driver)
        touxiang = driver.find_element_by_xpath('//div[@id="J-user-info"]//img[@class="default-avatar"]')
        actions.move_to_element(touxiang).perform()
        denglu = driver.find_element_by_xpath('//div[@class="user-info-action"]/a[@id="J-popup-login"]')
        denglu.click()
        driver.switch_to.frame('loginIframe53645')
        mimadenglu = driver.find_element_by_xpath(
            '//div[@class="form-login J_FormLogin formLoginW"]//li[@class="accountLg"]')
        mimadenglu.click()

        shouji1 = driver.find_element_by_xpath('//*[@id="J_AccountPsd"]')
        shouji1.send_keys(phone_number)

        mima = driver.find_element_by_xpath(
            '//div[@class="form-item"]/input[@class="txt J_NoTip J_DelectIcon J_PwPsd"]')
        mima.send_keys(password)

        submit = driver.find_element_by_xpath('/html/body/div[2]/div[1]/form[2]/div/div[5]/input')
        submit.click()

        time.sleep(2)

        cookies = driver.get_cookies()
        cookies_dict = {}
        for i in cookies:
            cookies_dict[i['name']] = i['value']
        with open(self.cookies_path, 'w') as f:
            f.write(json.dumps(cookies_dict))

        print('Cookies保存成功')


if __name__ == '__main__':
    migu_music = MiguMusic()
    migu_music.get_song_play_url('6005971JTR1')
    # migu_music.get_playlist_detail('179812779')
    # migu_music.get_toplist_detail('jianjiao_hotsong')
    # migu_music.search('Mojito')
    # migu_music.get_artist_detail(1004674393)
    # migu_music.get_album_detail('1136487194')

    # migu_music.save_cookies('XXXX','XXXX')

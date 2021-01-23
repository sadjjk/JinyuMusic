class BaseMusic:
    title = 'BaseMusic'
    is_support_playlist = 1  # 0 表示不支持歌单推荐  >=1 表示支持且权重值 选择最大的权重 作为默认显示的平台
    is_support_toplist = 1  # 0 表示不支持榜单  >=1 表示支持且权重值 选择最大的权重 作为默认显示的平台
    is_support_search = 1  # 0 表示不支持搜索 >=1 表示支持且权重值 选择最大的权重 作为默认显示的平台 若都为1 则进行全平台搜索

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36'
        }

    # 将较大的数转换成XX.XX万  较小的数保持不变
    # 常适用于播放量
    def num_to_str(self, num):
        '''
        将较大的数转换成XX.XX万  较小的数保持不变
        :param num: int
        :return: str
        '''

        if isinstance(num, str):
            target_str = num
        elif num < 10000:
            target_str = str(num)
        else:
            target_str = str(round(num / 10000, 2)) + '万'

        return target_str

    # 获取歌曲播放地址
    def get_song_play_url(self, song_id):
        pass

    # 获取歌曲歌词
    def get_song_lyric(self, song_id):
        pass

    # 获取歌手详情
    def get_artist_detail(self, artist_id):
        pass

    # 获取专辑详情
    def get_album_detail(self, album_id):
        pass

    # 获取推荐歌单
    def get_recommend_playlist(self, page_size=20, page_num=1):
        pass

    # 获取歌单详情
    def get_playlist_detail(self, playlist_id):
        pass

    # 获取排行榜
    def get_toplist(self):
        pass

    # 获取排行榜歌单详情
    def get_toplist_detail(self, toplist_id):
        pass

    # 搜索
    def search(self, keyword, curpage=1):
        pass

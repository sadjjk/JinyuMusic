from . import api
from flask import request, jsonify
from Music import platforms
from .utils import platform_required
import re


@api.route('/recommend_playlist', methods=['GET'])
@platform_required
def get_recommend_playlist():
    platform = request.args.get('platform', 'NeteaseMusic')
    page_size = request.args.get('page_size', 40)
    page_num = request.args.get('page_num', 1)
    music_obj = getattr(platforms, platform)()
    playlist_list = music_obj.get_recommend_playlist(page_size, page_num)
    return jsonify({'code': 200,
                    'errmsg': 'OK',
                    'data': playlist_list})


@api.route('/playlist_detail', methods=['GET'])
@platform_required
def get_playlist_detail():
    platform = request.args.get('platform', 'NeteaseMusic')
    playlist_id = request.args.get('playlist_id')
    if not playlist_id:
        return {'code': 500,
                'errmsg': '参数不完整'}
    music_obj = getattr(platforms, platform)()
    playlist_detail = music_obj.get_playlist_detail(playlist_id)
    return jsonify({'code': 200,
                    'errmsg': 'OK',
                    'data': playlist_detail})


@api.route('/playlist_load', methods=['GET'])
def load_playlist():
    url = request.args.get('url','')

    qq_pattern = 'y.qq.com/n/yqq/playlist/(\d+)'
    netease_pattern = 'music.163.com/#/playlist.*?id=(\d+)'

    if re.findall(qq_pattern, url):
        playlist_id = re.findall(qq_pattern, url)[0]
        music_obj = platforms.QQMusic()
        platform = 'QQMusic'
    elif re.findall(netease_pattern, url):
        playlist_id = re.findall(netease_pattern, url)[0]
        music_obj = platforms.NeteaseMusic()
        platform = 'NeteaseMusic'
    else:
        return jsonify({'code': 500, 'errmsg': '仅支持导入网易云音乐或QQ音乐的歌单'})

    playlist_info = music_obj.get_playlist_detail(playlist_id)

    data = {
        'songlist_type': 'playlist',
        'songlist_id': playlist_info.get('playlist_id'),
        'platform': platform,
        'title': playlist_info.get('title')
    }

    return jsonify({'code': 200,
                    'errmsg': 'OK',
                    'data': data})

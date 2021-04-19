import gevent
from . import api
from flask import request, jsonify, Response, current_app
from Music import platforms
from .utils import platform_required, get_all_platform
from itertools import zip_longest
from urllib.parse import quote
import urllib
import ssl

ssl._create_default_https_context = ssl._create_unverified_context


@api.route('/song_play_url', methods=['GET'])
@platform_required
def get_song_play_url():
    platform = request.args.get('platform', 'NeteaseMusic')
    song_id = request.args.get('song_id')
    music_obj = getattr(platforms, platform)()
    try:
        play_dict = music_obj.get_song_play_url(song_id)
        return jsonify({'code': 200,
                        'errmsg': 'OK',
                        'data': play_dict
                        })
    except Exception as e:
        return jsonify({'code': 500,
                        'errmsg': str(e),
                        })


@api.route('/download', methods=['POST'])
def download_song():
    platform = request.form.get('platform')
    song_id = request.form.get('song_id')
    song_name = request.form.get('song_name')

    music_obj = getattr(platforms, platform)()
    play_url = music_obj.get_song_play_url(song_id).get('play_url')

    r = urllib.request.urlopen(quote(play_url, safe='&/:?='))

    response = Response(
        r,
        content_type=r.headers['content-type'],
    )

    header = 'attachment; filename={0}; filename*=utf-8''{0}'.format(quote(song_name) + '.mp3')
    response.headers["Content-Disposition"] = header
    response.headers["Content-Length"] = r.headers['Content-Length']

    current_app.logger.info('开始下载音乐:{}'.format(song_name))
    try:
        ip = request.headers['X-Forwarded-For'].split(',')[0]
    except:
        ip = request.remote_addr
    current_app.logger.info('下载IP:{}\n'.format(ip))

    return response


@api.route('/song_lyric', methods=['GET'])
@platform_required
def get_song_lyric():
    platform = request.args.get('platform', 'NeteaseMusic')
    song_id = request.args.get('song_id')
    music_obj = getattr(platforms, platform)()
    lyric_dict = music_obj.get_song_lyric(song_id)
    return jsonify({'code': 200,
                    'errmsg': 'OK',
                    'data': lyric_dict
                    })


@api.route('/artist_detail', methods=['GET'])
@platform_required
def get_artist_detail():
    platform = request.args.get('platform', 'NeteaseMusic')
    artist_id = request.args.get('artist_id')
    music_obj = getattr(platforms, platform)()
    artist_detail = music_obj.get_artist_detail(artist_id)
    return jsonify({'code': 200,
                    'errmsg': 'OK',
                    'data': artist_detail
                    })


@api.route('/album_detail', methods=['GET'])
@platform_required
def get_album_detail():
    platform = request.args.get('platform', 'NeteaseMusic')
    album_id = request.args.get('album_id')
    music_obj = getattr(platforms, platform)()
    album_detail = music_obj.get_album_detail(album_id)
    return jsonify({'code': 200,
                    'errmsg': 'OK',
                    'data': album_detail
                    })


@api.route('/search', methods=['GET'])
def search():
    page_size = int(request.args.get('page_size', 20))
    page_num = int(request.args.get('page_num', 1))
    keyword = request.args.get('keyword')

    if not keyword:
        return jsonify({'code': 500,
                        'errmsg': '参数不完整'})

    platform = request.args.get('platform', '')

    if platform:
        music_obj = getattr(platforms, platform)()
        search_data = music_obj.search(keyword=keyword, page_num=page_num, page_size=page_size).get('list')

    else:
        # 全平台搜索
        platform_list = get_all_platform()
        platform_name_list = [i['name'] for i in platform_list if i['is_support_search'] == 1]

        jobs = [gevent.spawn(getattr(platforms, platform)().search, keyword, page_num, page_size) for platform in
                platform_name_list]
        gevent.joinall(jobs)

        search_data = [job.value.get('list') for job in jobs if job.value and job.value.get('list')]
        search_data = [j for i in list(zip_longest(*search_data)) for j in i if j]

    data = {
        'platform': platform,
        'page_num': page_num,
        'page_size': page_size,
        'search_list': search_data
    }

    return jsonify({'code': 200,
                    'errmsg': 'OK',
                    'data': data})

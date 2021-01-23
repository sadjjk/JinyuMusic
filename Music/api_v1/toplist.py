from . import api
from flask import request
from Music import platforms
from .utils import platform_required

@api.route('/toplist', methods=['GET'])
@platform_required
def get_toplist():
    platform = request.args.get('platform', 'NeteaseMusic')
    music_obj = getattr(platforms, platform)()
    toplist_list = music_obj.get_toplist()
    return {'code': 200,
            'errmsg': 'OK',
            'data': toplist_list}

@api.route('/toplist_detail', methods=['GET'])
@platform_required
def get_toplist_detail():
    platform = request.args.get('platform', 'NeteaseMusic')
    toplist_id = request.args.get('toplist_id')
    if not toplist_id:
        return {'code': 500,
                'errmsg': '参数不完整'}
    music_obj = getattr(platforms, platform)()
    toplist_detail = music_obj.get_toplist_detail(toplist_id)
    return {'code': 200,
            'errmsg': 'OK',
            'data': toplist_detail}
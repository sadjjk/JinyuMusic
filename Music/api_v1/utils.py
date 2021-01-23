import functools
from flask import request, jsonify
from Music.platforms import BaseMusic


def get_all_subclasses(cls):
    return cls.__subclasses__() + [g for s in cls.__subclasses__() for g in get_all_subclasses(s)]


def get_all_platform():
    platform_list = [{'name': platform.__name__,
                      'title': platform.title,
                      'is_support_playlist': getattr(platform, 'is_support_playlist', 1),
                      'is_support_toplist': getattr(platform, 'is_support_toplist', 1),
                      'is_support_search': getattr(platform, 'is_support_search', 1)} for platform in
                     get_all_subclasses(BaseMusic)]
    return platform_list


def platform_required(view_func):
    @functools.wraps(view_func)
    def wrapper(*args, **kwargs):

        if request.method == 'GET':
            data = request.args

        else:
            data = request.get_json(force=True)

        platform = data.get('platform', 'NeteaseMusic')

        platform_list = get_all_platform()

        if platform not in [i['name'] for i in platform_list]:
            return jsonify(code=500, errmsg=f'{platform} 该音乐平台不存在!')
        else:

            return view_func(*args, **kwargs)

    return wrapper

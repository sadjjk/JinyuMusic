from . import api
from flask import jsonify
from .utils import get_all_platform

@api.route('/platform', methods=['GET'])
def get_platform():
    platform_list = get_all_platform()
    return jsonify({'code': 200,
                    'errmsg': 'OK',
                    'data': platform_list
                    })
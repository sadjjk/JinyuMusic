from . import api
from flask import jsonify, request
from Music.platforms import QingtingFM


@api.route('/fm/cate', methods=['GET'])
def get_fm_cate():
    fm_obj = QingtingFM()
    data = fm_obj.get_all_categories()
    return jsonify({'code': 200,
                    'errmsg': 'OK',
                    'data': data
                    })


@api.route('/fm/radio', methods=['GET'])
def get_fm_radio():
    categories_id = request.args.get('cate_id', 433)
    fm_obj = QingtingFM()
    data = fm_obj.get_categories_radio(categories_id)

    return jsonify({'code': 200,
                    'errmsg': 'OK',
                    'data': data
                    })


@api.route('/fm/radio/detail', methods=['GET'])
def get_fm_radio_detail():
    radio_id = request.args.get('radio_id')
    if not radio_id:
        return jsonify({'code': 500,
                        'errmsg': 'radio_id必选'
                        })

    fm_obj = QingtingFM()
    data = fm_obj.get_radio_detail(radio_id)

    return jsonify({'code': 200,
                    'errmsg': 'OK',
                    'data': data
                    })



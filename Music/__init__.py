from flask import Flask
from config import CONFIG_MAP
from logger import setting_log
from werkzeug.routing import BaseConverter

setting_log(level='INFO')


# 定义正则转换器
class ReConverter(BaseConverter):

    def __init__(self, url_map, regex):
        super(ReConverter, self).__init__(url_map)
        self.regex = regex


def create_app(config_name):
    assert config_name in ('develop', 'product'), 'config_name must be develop or product'
    app = Flask(__name__)
    config_class = CONFIG_MAP.get(config_name)
    app.config.from_object(config_class)


    # CSRFProtect(app)

    app.url_map.converters["re"] = ReConverter

    from . import api_v1
    app.register_blueprint(api_v1.api, url_prefix='/api/v1')

    from . import web_html
    app.register_blueprint(web_html.html, url_prefix='')

    return app

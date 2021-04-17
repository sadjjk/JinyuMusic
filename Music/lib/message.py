import requests


class WeChatMessage:
    PUSHPLUS_MESSAGE_TOKEN = '87a297b65b034ef58eef7676f16747f2'
    PUSHPLUS_URL = 'http://pushplus.hxtrip.com/send'

    @staticmethod
    def send(title, content, template='html'):
        assert template in ('html', 'json'), '发送消息模板类型仅支持html或者json'

        data = {
            'title': title,
            'content': content,
            'template': template,
            'token': WeChatMessage.PUSHPLUS_MESSAGE_TOKEN
        }

        response = requests.post(WeChatMessage.PUSHPLUS_URL,
                                 json=data)

        return response



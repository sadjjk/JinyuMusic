from flask import Blueprint, current_app, make_response

html = Blueprint('web_html', __name__)


@html.route("<re(r'.*'):html_file_name>")
def get_html(html_file_name):
    if not html_file_name:
        html_file_name = 'index.html'

    if html_file_name != 'favicon.ico':
        html_file_name = 'html/' + html_file_name

    resp = make_response(current_app.send_static_file(html_file_name))

    return resp

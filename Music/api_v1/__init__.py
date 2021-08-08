from gevent import monkey
monkey.patch_all()
from flask import Blueprint
from .utils import get_all_subclasses

api = Blueprint('api_v1', __name__)

from . import playlist,toplist,song,platform,fm

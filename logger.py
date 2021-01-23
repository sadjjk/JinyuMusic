import logging
from logging.handlers import RotatingFileHandler
import os



def setting_log(add_file=True, add_console=True, folder='logs', level='DEBUG'):
    '''
    获取日志对象
    :param add_file: boolean 是否添加日志文件
    :param add_console: boolean 是否打印到屏幕上
    :param folder: 日志文件夹 默认 logs
    :param level: 记录日志级别
    :return:
    '''

    logging.basicConfig(level=getattr(logging,level))
    if add_file:

        if not os.path.exists(folder):
            os.mkdir(folder)

        # 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
        file_log_handler = RotatingFileHandler(os.path.join(folder, 'logging.log'),
                                               maxBytes=1024 * 1024 * 100,
                                               backupCount=10)

        # 创建日志记录的格式                 日志等级    输入日志信息的文件名 行数    日志信息
        formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
        # 为刚创建的日志记录器设置日志记录格式
        file_log_handler.setFormatter(formatter)
        # 为全局的日志工具对象（flask app使用的）添加日记录器
        logging.getLogger().addHandler(file_log_handler)

    if add_console:
        console_handler = logging.StreamHandler()
        logging.getLogger().addHandler(console_handler)



import datetime
import logging
import os

import colorlog

from Config import config


class Log:
    """
    系统日志输出类

    日志输出等级：
    CRITICAL = 50
    FATAL = CRITICAL(就是50)
    ERROR = 40
    WARNING = 30
    WARN = WARNING(就是30)
    INFO = 20
    DEBUG = 10
    NOTSET = 0

    使用示例：
    logging.debug("This is a DEBUG message")
    logging.info("This is an INFO message")
    logging.warning("This is a WARNING message")
    logging.error("This is an ERROR message")
    logging.critical("This is a CRITICAL message")
    """

    logger = None

    def __init__(self):
        # 日志输出颜色
        log_colors_config = {
            'DEBUG': 'white',
            'INFO': 'white',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'bold_red',
        }

        Log.logger = logging.getLogger()
        Log.logger.setLevel(config.get_log_level())

        root_path = os.getcwd()
        file_name = datetime.datetime.now().strftime('%Y%m%d_%H%M%S') + ".log"
        log_path = os.path.join(root_path, r"log", file_name)

        # create log folder if it is not exist.
        log_dir = os.path.dirname(log_path)
        if not os.path.exists(log_dir):
            os.mkdir(log_dir)

        if not Log.logger.handlers:  # 作用,防止重新生成处理器
            sh = logging.StreamHandler()  # 创建控制台日志处理器
            fh = logging.FileHandler(filename=log_path, mode='a', encoding="utf-8")  # 创建日志文件处理器
            # 创建格式器
            fmt = logging.Formatter(
                fmt="[%(asctime)s.%(msecs)03d] %(filename)s:%(lineno)d [%(levelname)s]: %(message)s",
                datefmt='%Y-%m-%d  %H:%M:%S')

            sh_fmt = colorlog.ColoredFormatter(
                fmt="%(log_color)s[%(asctime)s.%(msecs)03d]-[%(levelname)s]: %(message)s",
                datefmt='%Y-%m-%d  %H:%M:%S',
                log_colors=log_colors_config)
            # 给处理器添加格式
            sh.setFormatter(fmt=sh_fmt)
            fh.setFormatter(fmt=fmt)
            # 给日志器添加处理器，过滤器一般在工作中用的比较少，如果需要精确过滤，可以使用过滤器
            Log.logger.addHandler(sh)
            Log.logger.addHandler(fh)

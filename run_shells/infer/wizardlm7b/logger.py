import logging


class SingletonType(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(SingletonType, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


# python 3 style
class MyLogger(object, metaclass=SingletonType):

    def __init__(self, filename=None):
        self._logger = logging.getLogger("tts")
        self._logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s \t [%(levelname)s | %(filename)s:%(lineno)s] > %(message)s')

        streamHandler = logging.StreamHandler()
        streamHandler.setFormatter(formatter)
        self._logger.addHandler(streamHandler)

        self._logger.propagate = False  # 防止 log record向根Logger传 打印两次log的问题

        if filename:
            file_handler = logging.FileHandler(filename)
            file_handler.setFormatter(formatter)
            self._logger.addHandler(file_handler)

        print("Generate new instance")

    def get_logger(self):
        return self._logger

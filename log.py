import logging


def add_logger(c):
    c._logger= logging.getLogger('farmcloud')

    c.debug = c._logger.debug
    c.info = c._logger.info
    c.warn = c._logger.warn
    c.error = c._logger.error
    c.critical = c._logger.critical


def init_logger(name='farmcloud', level=logging.DEBUG, logfile=''):
    # logging.basicConfig()

    formatter = logging.Formatter('%(levelname)s:%(message)s')

    handler = logging.FileHandler(logfile) if logfile else \
        logging.StreamHandler()
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

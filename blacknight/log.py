import logging


def add_logger(c):
    c.log = logging.getLogger('blacknight')

    c.debug = c.log.debug
    c.info = c.log.info
    c.warn = c.log.warn
    c.error = c.log.error
    c.critical = c.log.critical

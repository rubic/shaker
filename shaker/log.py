import os
import logging

LOG_LEVELS = {
    'debug': logging.DEBUG,
    'error': logging.ERROR,
    'info': logging.INFO,
    'none': logging.NOTSET,
    'warning': logging.WARNING,
}

def start_logger(logname, filename, log_level):
    consoleLogger = logging.StreamHandler()
    consoleLogger.setLevel(logging.WARNING)
    logging.getLogger(logname).addHandler(consoleLogger)
    formatter = logging.Formatter(
        '%(asctime)-6s: %(name)s - %(levelname)s - %(message)s')

    directory, _ = os.path.split(filename)
    if not os.path.isdir(directory):
        os.makedirs(directory)

    fileLogger = logging.FileHandler(filename=filename)
    fileLogger.setLevel(LOG_LEVELS[log_level])
    fileLogger.setFormatter(formatter)
    logging.getLogger(logname).addHandler(fileLogger)
    logger = logging.getLogger(logname)
    logger.setLevel(LOG_LEVELS[log_level])


def getLogger(logname):
    return logging.getLogger(logname)

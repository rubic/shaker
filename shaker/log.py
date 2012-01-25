import os
import logging

def start_logger(logname, filename):
    consoleLogger = logging.StreamHandler()
    consoleLogger.setLevel(logging.INFO)
    logging.getLogger(logname).addHandler(consoleLogger)
    formatter = logging.Formatter(
        '%(asctime)-6s: %(name)s - %(levelname)s - %(message)s')

    directory, _ = os.path.split(filename)
    if not os.path.isdir(directory):
        os.makedirs(directory)

    fileLogger = logging.FileHandler(filename=filename)
    fileLogger.setLevel(logging.INFO)
    fileLogger.setFormatter(formatter)
    logging.getLogger(logname).addHandler(fileLogger)
    logger = logging.getLogger(logname)
    logger.setLevel(logging.INFO)


def getLogger(logname):
    return logging.getLogger(logname)

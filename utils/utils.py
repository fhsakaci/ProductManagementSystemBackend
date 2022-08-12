import os
import time
import tarfile
import logging
import colorlog
from pathlib import Path
from datetime import datetime


APP_NAME = 'server'
HOME_DIR = None
LOG_FILE_NAME = APP_NAME + '.log'
LOG_FILE_PATH = None
LOGGER = None

ONE_HOUR_IN_SECONDS=60*60



def set_log_file(home_dir, log_file_name):
    global LOG_FILE_PATH
    LOG_FILE_PATH = os.path.join(home_dir, log_file_name)


def set_home_dir(py_file):
    global HOME_DIR
    HOME_DIR = Path(os.path.dirname(os.path.abspath(py_file)))


def save_prev_log(path):
    # save older log file in tar format if any
    if os.path.exists(path):
        date_time = datetime.now().strftime('_%Y-%m-%d_%H:%M')
        tar_path = path + date_time + '.gz'
        tar = tarfile.open(tar_path, "w:gz")
        tar.add(path)
        tar.close()
        os.remove(path)


def remove_older_logs(log_file_path, older_than_in_hours):
    log_dir = Path(log_file_path).parent
    for root, dirs, files in os.walk(log_dir):
        if root != str(log_dir):
            break
        for f in files:
            if f.endswith('.gz'):
                try:
                    if os.path.getmtime(f) < time.time() - (older_than_in_hours * ONE_HOUR_IN_SECONDS):
                        os.remove(f)
                except FileNotFoundError as f:
                    pass


def set_logger(name=APP_NAME, main_file_path=None):
    
    if not main_file_path:
        raise ValueError('Main python source file path should be given (for example, __name__)')
    # set application home directory
    set_home_dir(main_file_path)
    set_log_file(HOME_DIR, LOG_FILE_NAME)
    save_prev_log(LOG_FILE_PATH)
    remove_older_logs(LOG_FILE_PATH, 1)
    formatter = colorlog.ColoredFormatter(
        "[%(asctime)s] %(filename)-18sln %(lineno)3d %(threadName)-10s %(name)s-%(log_color)s%(levelname)8s-%(blue)s%(message)s",
        datefmt=None,
        reset=True,
        log_colors={

            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red',
        }
    )
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # create a file handler and a stream handler
    fh = logging.FileHandler(LOG_FILE_PATH)
    fh.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # create a logging format
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    # add the file handler to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)
    logger.propagate = False

    global LOGGER
    LOGGER = logger
    return logger

    
def get_logger():
    global LOGGER
    return LOGGER

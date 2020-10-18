import logging
from time import strftime
from os.path import isfile

def createConfig(logfile : str, level, process : str):
    mode = None
    if isfile(logfile):
        mode = 'a+'
    else:
        mode = 'w+'
    file = open(logfile, mode)
    try:
        file.write('\n')
        file.write('-' * 75)
        file.write('\n')
    finally:
        file.close()

    logging.basicConfig(filename=logfile, level=level, encoding='utf-8')
    logging.info(f'Initialising RapidLogger With {process} at {strftime("%H:%M:%S")}')

def closeLog(logfile : str, process : str):
    if logfile:
        logging.info(f'Terminating RapidLogger On {process} at {strftime("%H:%M:%S")}')
        file = open(logfile, 'a+')
        try:
            file.write('\n')
            file.write('-' * 75)
            file.write('\n')
        finally:
            file.close()

def log_info(text : str, logfile : str):
    if logfile:
        logging.info(text)

def log_error(text : str, logfile : str):
    if logfile:
        logging.error(text)

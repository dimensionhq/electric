######################################################################
#                               LOGGING                              #
######################################################################

from Classes.PathManager import PathManager
from os.path import isfile
from time import strftime
import logging

path_manager = PathManager()
current_dir = path_manager.get_current_directory()
parent_dir = path_manager.get_current_directory().replace('\\src', '')

# Create Log File At A Certain Directory (logfile)
def createConfig(logfile : str, level, process : str):
    with open(f'{parent_dir}\\electric-log.log', 'w+') as f:
        pass
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
    with open(f'{parent_dir}\\electric-log.log', 'w+') as f:
        f.write('\n')
        f.write('-' * 75)
        f.write('\n')
    
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
    with open(f'{parent_dir}\\electric-log.log', 'a+') as f:
        f.write(f'\nINFO:root:{text}')
    if logfile:
        logging.info(text)

def log_error(text : str, logfile : str):
    with open(f'\n{parent_dir}\\electric-log.log', 'a+') as f:
        f.write(f'INFO:root:{text}')
    if logfile:
        logging.error(text)

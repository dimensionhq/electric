######################################################################
#                               LOGGING                              #
######################################################################

from Classes.PathManager import PathManager
from os.path import isfile, isdir
from time import strftime
from os import mkdir
import logging

appdata_dir = PathManager.get_appdata_directory()

def start_log():
    """
    Register a new command start in the appdata electric logfile
    """    
    mode = 'a+' if isfile(f'{appdata_dir}\\electric-log.log') else 'w+'
    with open(f'{appdata_dir}\\electric-log.log', mode) as f:
        f.write('-' * 75)
        
# Create Log File At A Certain Directory (logfile)
def create_config(logfile : str, level, process : str):
    """
    Initializes a logger and handles logging to a specific file if told to do so

    #### Arguments
        logfile (str): Name of the file to log to
        level ([type]): The level of the logging (defaults to info)
        process (str): The method (installation / uninstallation)
    """
    if not isdir(appdata_dir):
        mkdir(appdata_dir)

    mode = None
    mode = 'a+' if isfile(logfile) else 'w+'
    file = open(logfile, mode)
    try:
        file.write('-' * 75)
        file.write('\n')
    finally:
        file.close()

    logging.basicConfig(filename=logfile, level=logging.DEBUG, encoding='utf-8')
    logging.info(f'Initialising RapidLogger With {process} at {strftime("%H:%M:%S")}')

def close_log(logfile : str, process : str):
    """
    Marks a completed log into the specified logfile and the appdata electric logs

    #### Arguments
        logfile (str): The file to log to
        process (str): The method (installation / uninstallation)
    """    
    with open(f'{appdata_dir}\\electric-log.log', 'a+') as f:
        f.write('-' * 75)
        f.write('\n')

    if logfile:
        logging.info(f'Terminating RapidLogger On {process} at {strftime("%H:%M:%S")}')
        file = open(logfile, 'a+')
        try:
            file.write('-' * 75)
            file.write('\n')
        finally:
            file.close()


def log_info(text : str, logfile : str):
    """
    Logs with a level of `info` to a logfile

    #### Arguments
        text (str): The text to log / write to the file
        logfile (str): The file to write logs to
    """    
    mode = 'a+'

    with open(f'{appdata_dir}\\electric-log.log', mode) as f:
        f.write(f'\nINFO:root:{text}')
    if logfile:
        logging.info(text)


def log_error(text : str, logfile : str):
    """
    Logs with a level of `error` to a logfile

    #### Arguments
        text (str): Text to log / write to the file
        logfile (str): The file to write logs to
    """    
    with open(f'\n{appdata_dir}\\electric-log.log', 'a+') as f:
        f.write(f'INFO:root:{text}')
    if logfile:
        logging.error(text)

from Classes.PathManager import PathManager
from subprocess import Popen, PIPE
import json
import os

settings_dir = PathManager.get_appdata_directory() + R'\settings.json'

def initialize_settings():
    """
    Initializes the settings file and directory if it doesn't exist. Writes default settings to the file.
    """    
    default_electric_settings = {
        "$schema": "https://github.com/electric-package-manager/electric/blob/master/settings-schema.json",
        "progressBarType": "accented",
        "showProgressBar": True,
        "electrifyProgressBar": False
    }

    if not os.path.isdir(PathManager.get_appdata_directory()):
        os.mkdir(PathManager.get_appdata_directory()) 
    with open(settings_dir, 'w+') as f:
        f.write(json.dumps(default_electric_settings, indent=4))

def read_settings() -> dict:
    """
    Reads settings from the settings file in appdata

    Returns:
        dict: The settings in the form of a dictionary
    """    
    with open(settings_dir, 'r') as f:
        dictionary = json.load(f)
    return dictionary

def open_settings():
    """
    Opens the settings file with the default application configured for .json files.
    """    
    Popen(f'start {settings_dir}'.split(), stdout=PIPE, stderr=PIPE, stdin=PIPE, shell=True)

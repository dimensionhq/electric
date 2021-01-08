from Classes.PathManager import PathManager
from subprocess import Popen, PIPE
import json
import os

settings_dir = PathManager.get_appdata_directory() + R'\electric-settings.json'

def initialize_settings():
    default_electric_settings = {
        "$schema": "https://electric-package-manager.herokuapp.com/schemas/settings",
        "progressBarType": "accented",
        "showProgressBar": True,
        "electrifyProgressBar": False
    }

    if not os.path.isdir(PathManager.get_appdata_directory()):
        os.mkdir(PathManager.get_appdata_directory()) 
    with open(settings_dir, 'w+') as f:
        f.write(json.dumps(default_electric_settings, indent=4))

def read_settings() -> dict:
    with open(settings_dir, 'r') as f:
        dictionary = json.load(f)
    return dictionary

def open_settings():
    Popen(f'start {settings_dir}'.split(), stdout=PIPE, stderr=PIPE, stdin=PIPE, shell=True)

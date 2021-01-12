from zip_utils import *
from colorama import Fore
import os

def install(data: dict):
    changes_environment = False
    latest_version = data['latest-version']
    data = data[latest_version]
    loc = __file__.replace('zip-install.py', '')
    shortcuts = data['shortcuts']
    download(data['url'], '.zip', data['extract-dir'])
    unzip_dir = unzip_file(data['extract-dir'] + '.zip', data['extract-dir'])
    software_loc = loc + '\\' + unzip_dir

    try:
        dir = data['chdir']
        software_loc += f'\\{dir}'
    except KeyError:
        pass

    try:
        name = data['bin']
        changes_environment = True
        generate_shim(rf'{software_loc}\{name}', data['bin'])
    except KeyError:
        changes_environment = False

    for shortcut in shortcuts:
        shortcut_name = shortcut['shortcut-name']
        file_name = shortcut['file-name']
        create_start_menu_shortcut(file_name, shortcut_name)

    if changes_environment:
        print(f'{Fore.GREEN}\nRefreshing Environment Variables{Fore.RESET}')
        os.system(r'C:\Users\tejas\Desktop\Electric\Electric-Windows\src\scripts\refreshvars.cmd')

# import json
# with open('zip-test.json', 'r') as f:
#     data = json.load(f)

# install(data)
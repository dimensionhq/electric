from Classes.PortablePacket import PortablePacket
from zip_utils import delete_start_menu_shortcut
import json
import os

home = os.path.expanduser('~')

def uninstall(data: dict):
    packet = PortablePacket(data)
    loc = rf'{home}\electric\\'
    package_directory = loc + packet.extract_dir
    os.system(f'del /f/s/q {package_directory} > nul')
    os.system(f'rmdir /s/q {package_directory}')
    loc = rf'{home}\electric\shims'

    for sh in packet.bin:
        shim_name = sh.split('\\')[-1].replace('.exe', '').replace('.ps1', '').replace('.cmd', '').replace('.bat', '')
        try:
            os.remove(loc + '\\' + shim_name + '.bat')
        except FileNotFoundError:
            pass

    shortcuts = packet.shortcuts
    for shortcut in shortcuts:
        delete_start_menu_shortcut(shortcut['shortcut-name'])

# with open('zip-test.json', 'r') as f:
#     data = json.load(f)

# uninstall(data)
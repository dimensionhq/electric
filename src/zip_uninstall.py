# from zip_utils import delete_start_menu_shortcut
# import json
# import os

# def uninstall(data: dict):
#     loc = __file__.replace('zip-uninstall.py', '')
#     data = data[data['latest-version']]
#     package_directory = loc + data['extract-dir']
#     os.system(f'del /f/s/q {package_directory} > nul')
#     os.system(f'rmdir /s/q {package_directory}')
#     loc = __file__.replace('zip-uninstall.py', '') + r'shims'
#     shim_name = data['bin'].replace('.exe', '').replace('.ps1', '').replace('.cmd', '').replace('.bat', '')
#     os.remove(loc + '\\' + shim_name + '.bat')

#     shortcuts = data['shortcuts']
#     for shortcut in shortcuts:
#         delete_start_menu_shortcut(shortcut['shortcut-name'])


######################################################################
#                              REGISTRY                              #
######################################################################

from query import query_registry_info, find_accurate_matches
from Classes.RegSnapshot import RegSnapshot
import difflib
import winreg


def string_gen(package_name : str):
    package_name = package_name.split('-')
    return ''.join(package_name)


def get_uninstall_key(package_name : str):

    keys = query_registry_info()
    final_array = []
    total = []

    strings = string_gen(package_name)

    for key in keys:
        display_name = key['DisplayName']
        url = None if 'URLInfoAbout' not in key else key['URLInfoAbout']
        uninstall_string = '' if 'UninstallString' not in key else key['UninstallString']
        quiet_uninstall_string = '' if 'QuietUninstallString' not in key else key['QuietUninstallString']
        install_location = '' if 'InstallLocation' not in key else key['InstallLocation']
        final_list = [display_name, url, uninstall_string, quiet_uninstall_string, install_location]
        index = 0
        matches = None
        refined_list = []

        for item in final_list:
            if item is None:
                final_list.pop(index)
            else:
                name = item.lower()
                refined_list.append(name)
            
            index += 1

        for string in strings:
            matches = difflib.get_close_matches(string, refined_list)

            if not matches:
                possibilities = []

                for element in refined_list:
                    for string in strings:
                        if string in element:
                            possibilities.append(key)

                if possibilities:
                    total.append(possibilities)

                continue

            else:
                final_array.append(key)

    strings = string_gen(package_name)

    if final_array:
        if len(final_array) > 1:
            return find_accurate_matches(strings, package_name, final_array)
        return final_array
    
    return_array = []
    for val in total:
        return_array.append(val[0])

    if len(return_array) > 1:
        return find_accurate_matches(strings, package_name, return_array)
    
    return return_array


def get_environment_keys() -> RegSnapshot:
    env_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Environment', 0, winreg.KEY_READ)
    sys_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, R'SYSTEM\CurrentControlSet\Control\Session Manager\Environment', 0, winreg.KEY_READ)
    sys_idx = 0
    while True:
        if winreg.EnumValue(env_key, sys_idx)[0] == 'Path':
            break
        sys_idx += 1
    env_idx = 0
    while True:
        if winreg.EnumValue(sys_key, env_idx)[0] == 'Path':
            break
        env_idx += 1
    snap = RegSnapshot(str(winreg.EnumValue(env_key, sys_idx)[1]), len(str(winreg.EnumValue(env_key, sys_idx)[1]).split(';')), str(winreg.EnumValue(sys_key, env_idx)[1]), len(str(winreg.EnumValue(sys_key, env_idx)[1]).split(';')))
    return snap

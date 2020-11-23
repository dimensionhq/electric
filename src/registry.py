######################################################################
#                              REGISTRY                              #
######################################################################

from timeit import default_timer as timer
from Classes.RegSnapshot import RegSnapshot
import difflib
import winreg
import os


keys = []

def get_uninstall_key(package_name : str):
    def get_registry_info():
        proc_arch = os.environ['PROCESSOR_ARCHITECTURE'].lower()
        proc_arch64 = None if 'PROCESSOR_ARCHITEW6432' not in os.environ.keys() else os.environ['PROCESSOR_ARCHITEW6432'].lower()
        if proc_arch == 'x86' and not proc_arch64:
            arch_keys = {0}
        elif proc_arch == 'x86' or proc_arch == 'amd64':
            arch_keys = {winreg.KEY_WOW64_32KEY, winreg.KEY_WOW64_64KEY}
        else:
            raise OSError("Unhandled arch: %s" % proc_arch)

        for arch_key in arch_keys:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall", 0, winreg.KEY_READ | arch_key)
            for i in range(0, winreg.QueryInfoKey(key)[0]):
                skey_name = winreg.EnumKey(key, i)
                skey = winreg.OpenKey(key, skey_name)
                try:
                    name = winreg.QueryValueEx(skey, 'DisplayName')[0]
                    stro = winreg.QueryValueEx(skey, 'UninstallString')[0]
                    packs = []
                    for regkey in ["URLInfoAbout", "InstallLocation", "Publisher"]:
                        try:
                           packs.append(winreg.QueryValueEx(skey, regkey)[0])
                        except:
                            packs.append(None)

                    url, loc, pub = packs

                    qstro = None
                    if 'MsiExec.exe' in stro:
                        qstro = stro + ' /quiet'
                    try:
                        qstro = winreg.QueryValueEx(skey, 'QuietUninstallString')[0]
                    except OSError as e:
                            pass
                    if qstro is not None:
                        gen_dict = {
                                    "DisplayName": name,
                                    "QuietUninstallString": qstro,
                                    "URLInfoAbout": url,
                                    "InstallLocation": loc,
                                    "Publisher": pub,
                                   }

                        keys.append(gen_dict)
                    else:
                        gen_dict = {
                                    "DisplayName": name,
                                    "UninstallString": stro,
                                    "URLInfoAbout": url,
                                    "InstallLocation": loc,
                                    "Publisher": pub,
                                   }
                        keys.append(gen_dict)
                except OSError as e:
                        pass
                finally:
                    skey.Close()

    final_array = []
    total = []

    def get_uninstall_string(package_name : str):
        nonlocal final_array
        string_gen(package_name)

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
                        
                    else:
                        continue
                else:
                    final_array.append(key)


    strings = []
    def string_gen(package_name : str):
        package_name = package_name.split('-')
        strings.append(''.join(package_name))

    def get_more_accurate_matches(return_array):
        index, confidence = 0, 50
        final_index, final_confidence = (None, None)

        for key in return_array:
            name = key['DisplayName']
            loc = key['InstallLocation']
            uninstall_string = None if 'UninstallString' not in key else key['UninstallString']
            quiet_uninstall_string = None if 'QuietUninstallString' not in key else key['QuietUninstallString']
            url = None if 'URLInfoAbout' not in key else key['URLInfoAbout']

            for string in strings:
                if name:
                    if string.lower() in name.lower():
                        confidence += 10
                if loc:
                    if string.lower() in loc.lower():
                        confidence += 5
                if uninstall_string:
                    if string.lower() in uninstall_string.lower():
                        confidence += 5
                if quiet_uninstall_string:
                    if string.lower() in quiet_uninstall_string.lower():
                        confidence += 5
                if url:
                    if string.lower() in url.lower():
                        confidence += 10

                if final_confidence == confidence:
                    word_list = package_name.split('-')

                    for word in word_list:
                        for key in [name, quiet_uninstall_string, loc, url]:
                            if key:
                                if word in key:
                                    confidence += 5

                        if word:
                            if uninstall_string:
                                if word in uninstall_string:
                                        confidence += 5

                if not final_index and not final_confidence:
                    final_index = index
                    final_confidence = confidence
                if final_confidence < confidence:
                    final_index = index
                    final_confidence = confidence
            index += 1
        return return_array[final_index]


    get_registry_info()
    get_uninstall_string(package_name)
    if final_array:
        if len(final_array) > 1:
            return get_more_accurate_matches(final_array)
        return final_array
    return_array = []
    for something in total:
        return_array.append(something[0])
    if len(return_array) > 1:
        return get_more_accurate_matches(return_array)
    else:
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

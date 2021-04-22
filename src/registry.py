######################################################################
#                              REGISTRY                              #
######################################################################

from Classes.RegSnapshot import RegSnapshot
import difflib
import winreg


keys = []


def send_query(hive, flag):
    aReg = winreg.ConnectRegistry(None, hive)
    aKey = winreg.OpenKey(aReg, r'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall',
                        0, winreg.KEY_READ | flag)

    count_subkey = winreg.QueryInfoKey(aKey)[0]

    software_list = []

    for i in range(count_subkey):
        software = {}
        try:
            asubkey_name = winreg.EnumKey(aKey, i)
            asubkey = winreg.OpenKey(aKey, asubkey_name)

            software['DisplayName'] = winreg.QueryValueEx(asubkey, "DisplayName")[0]
            software['KeyName'] = asubkey_name
            try:
                temp = winreg.QueryValueEx(asubkey, "QuietUninstallString")[0]
                software['QuietUninstallString'] = temp
            except:
                pass
            try:
                software['UninstallString'] = winreg.QueryValueEx(asubkey, "UninstallString")[0]
            except:
                software['UninstallString'] = 'Unknown'
            try:
                software['Version'] = winreg.QueryValueEx(asubkey, "DisplayVersion")[0]
            except EnvironmentError:
                software['Version'] = 'Unknown'
            try:
                software['InstallLocation'] = winreg.QueryValueEx(asubkey, "InstallLocation")[0]
            except EnvironmentError:
                software['InstallLocation'] = 'Unknown'
            try:
                software['Publisher'] = winreg.QueryValueEx(asubkey, "Publisher")[0]
            except EnvironmentError:
                software['Publisher'] = 'Unknown'
            software_list.append(software)
        except EnvironmentError:
            continue
        
    return software_list


def get_uninstall_key(package_name : str, display_name: str):
    """
    Finds the uninstallation key from the registry

    #### Arguments
        package_name (str): The json-name of the package ex: `sublime-text-3`
        
        display_name (str): The display name of the package ex: `Sublime Text 3`
    """    
    

    keys = send_query(winreg.HKEY_LOCAL_MACHINE, winreg.KEY_WOW64_32KEY) + send_query(winreg.HKEY_LOCAL_MACHINE, winreg.KEY_WOW64_64KEY) + send_query(winreg.HKEY_CURRENT_USER, 0)
    
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
            install_location = None if 'InstallLocation' not in key else key['InstallLocation']
            final_list = [display_name, url, uninstall_string, quiet_uninstall_string, install_location]
            matches = None
            refined_list = []

            for index, item in enumerate(final_list):
                    if item:
                            name = item.lower()

                    else:
                            final_list.pop(index)
                    refined_list.append(name)

            temp_list = []
            old = ''
            for val in refined_list:
                if val != old:
                    temp_list.append(val.lower())
                    old = val

            for string in strings:
                if package_name.endswith('*'):
                    for name in temp_list:
                        if package_name.lower().replace('*', '') in name:
                            final_array.append(key)
                else:
                    matches = difflib.get_close_matches(
                        package_name.lower(), temp_list, cutoff=0.65)

                    if matches:
                            final_array.append(key)

                    else:
                            possibilities = []

                            for element in refined_list:
                                for string in strings:
                                    if string in element:
                                        possibilities.append(key)

                            if possibilities:
                                total.append(possibilities)

    strings = []

    def string_gen(package_name : str):
        package_name = package_name.split('-')
        strings.append(' '.join(package_name))
        strings.append(display_name.lower())

    def get_more_accurate_matches(return_array):
        index, confidence = 0, 50
        final_index, final_confidence = (None, None)

        for key in return_array:
            name = key['DisplayName']
            loc = None
            try:
                loc = key['InstallLocation']
            except KeyError:
                pass

            uninstall_string = None if 'UninstallString' not in key else key['UninstallString']
            quiet_uninstall_string = None if 'QuietUninstallString' not in key else key['QuietUninstallString']
            url = None if 'URLInfoAbout' not in key else key['URLInfoAbout']

            for string in strings:
                    if name and string.lower() in name.lower():
                            confidence += 10
                    if loc and string.lower() in loc.lower():
                            confidence += 5
                    if (uninstall_string
                        and string.lower() in uninstall_string.lower()):
                            confidence += 5
                    if (quiet_uninstall_string and
                        string.lower() in quiet_uninstall_string.lower()):
                            confidence += 5
                    if url and string.lower() in url.lower():
                            confidence += 10

                    if final_confidence == confidence:
                            word_list = package_name.split('-')

                            for word in word_list:
                                    for key in [name, quiet_uninstall_string, loc, url]:
                                            if key and word in key:
                                                    confidence += 5

                                    if (word and uninstall_string
                                        and word in uninstall_string):
                                            confidence += 5

                    if not final_index and not final_confidence:
                        final_index = index
                        final_confidence = confidence
                    if final_confidence < confidence:
                        final_index = index
                        final_confidence = confidence
            index += 1
        return return_array[final_index]

    get_uninstall_string(display_name)

    if final_array:
        if len(final_array) > 1:
            return get_more_accurate_matches(final_array)
        return final_array
    return_array = []
    
    for var in total:
        return_array.append(var[0])
    
    if len(return_array) > 1:
        return get_more_accurate_matches(return_array)
    else:
        return return_array


def get_environment_keys() -> RegSnapshot:
        """
    Gets the current PATH environment variable and inserts it into a registry snapshot

    Returns:
        RegSnapshot: The Snapshot for the PATH Env
    """    
        env_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Environment', 0, winreg.KEY_READ)
        sys_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, R'SYSTEM\CurrentControlSet\Control\Session Manager\Environment', 0, winreg.KEY_READ)
        sys_idx = 0
        while True:
            try:
                if winreg.EnumValue(env_key, sys_idx)[0] == 'Path':
                    break
            except OSError:
                break
            sys_idx += 1
        env_idx = 0
        while True:
            try:
                if winreg.EnumValue(sys_key, env_idx)[0].lower() == 'path':
                    break
            except OSError:
                break
            env_idx += 1
        return RegSnapshot(
            str(winreg.EnumValue(env_key, sys_idx)[1]),
            len(str(winreg.EnumValue(env_key, sys_idx)[1]).split(';')),
            str(winreg.EnumValue(sys_key, env_idx)[1]),
            len(str(winreg.EnumValue(sys_key, env_idx)[1]).split(';')),
        )

import winreg
import os

keys = []

def query_registry_info():
    
        arch_keys = {winreg.KEY_WOW64_32KEY, winreg.KEY_WOW64_64KEY}
        
        for arch_key in arch_keys:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall', 0, winreg.KEY_READ | arch_key)
            for i in range(0, winreg.QueryInfoKey(key)[0]):
                skey_name = winreg.EnumKey(key, i)
                skey = winreg.OpenKey(key, skey_name)
                try:
                    name = winreg.QueryValueEx(skey, 'DisplayName')[0]
                    stro = winreg.QueryValueEx(skey, 'UninstallString')[0]
                    packs = []
                    for regkey in ['URLInfoAbout', 'InstallLocation', 'Publisher']:
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
                    except OSError:
                            pass
                    if qstro is not None:
                        gen_dict = {
                                    'DisplayName': name,
                                    'QuietUninstallString': qstro,
                                    'URLInfoAbout': url,
                                    'InstallLocation': loc,
                                    'Publisher': pub,
                                   }

                        keys.append(gen_dict)
                    else:
                        gen_dict = {
                                    'DisplayName': name,
                                    'UninstallString': stro,
                                    'URLInfoAbout': url,
                                    'InstallLocation': loc,
                                    'Publisher': pub,
                                   }
                        keys.append(gen_dict)
                except OSError:
                        pass
                finally:
                    skey.Close()

def find_accurate_matches(strings, package_name, return_array):

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

                        if word and uninstall_string:
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
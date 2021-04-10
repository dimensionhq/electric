from difflib import get_close_matches
import sys
import winreg

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

installed_software = send_query(winreg.HKEY_LOCAL_MACHINE, winreg.KEY_WOW64_32KEY) + send_query(
            winreg.HKEY_LOCAL_MACHINE, winreg.KEY_WOW64_64KEY) + send_query(winreg.HKEY_CURRENT_USER, 0)
        
names = [software['DisplayName'] for software in installed_software]

num = int(input('Enter 1 => Find Display Name For Software\nEnter 2 => Test If Display Name Has A Match\n>'))


if num == 1:
    test = input('Enter the approx display name of the package > ')
    matches = get_close_matches(test, names, cutoff=0.3)

    if len(matches) == 0:
        print('No Matches Found!')
    else:
        for match in matches:
            print('Match Found:', match)

if num == 2:
    try:
        test = input('Enter the display name of the package you want to test for > ')
    except KeyboardInterrupt:
        sys.exit()

    matches = get_close_matches(test, names, cutoff=0.65)

    if len(matches) == 0:
        print('No Matches Found!')
    if len(matches) == 1:
        print(f'Great! 1 Match Found => {matches[0]}')
    elif len(matches) > 1:
        print('Multiple Matches Found. Please Try To Refine Your Display Name')
        for match in matches:
            print(match)

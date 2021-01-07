import winreg

winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, R'*\shell\electric')
winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, R'*\shell\electric\command')

electric_key = winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, R'*\shell\electric', 0, winreg.KEY_ALL_ACCESS)
winreg.SetValueEx(electric_key, '', 0, winreg.REG_SZ, 'Install With Electric')
electric_key.Close()

command_key = winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, R'*\shell\electric\command', 0, winreg.KEY_ALL_ACCESS)
winreg.SetValueEx(command_key, '', 0, winreg.REG_SZ, R'"C:\Program Files (x86)\Electric\bin\electric.exe" install --configuration "%1"')
command_key.Close()
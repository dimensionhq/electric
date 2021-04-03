import winreg

k = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, 'Electric')
winreg.SetValueEx(k, '', 0, winreg.REG_SZ, 'URL:Electric Protocol')
winreg.SetValueEx(k, 'URL Protocol', 0, winreg.REG_SZ, 'URL:Electric Protocol')
winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, r'Electric\DefaultIcon')
winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, r'Electric\Shell')
winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, r'Electric\Shell\Open')
command_key = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, r'Electric\Shell\Open\command')
command = r'C:\Program Files (x86)\Electric\bin\launcher.exe'
winreg.SetValueEx(command_key, '', 0, winreg.REG_SZ, command)

import winreg

winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, r'Electric\Shell\Open\command')
winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, r'Electric\Shell\Open')
winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, r'Electric\Shell')
winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, r'Electric\DefaultIcon')
winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, 'Electric')

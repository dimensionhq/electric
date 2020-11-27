import ctypes, sys
import tempfile
import shutil
import py7zr
import os

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if is_admin():
    archive = py7zr.SevenZipFile(f'{tempfile.gettempdir()}\\Update.7z', 'r')
    archive.extractall(R'C:\Program Files\Electric\update')
    archive.close()
    shutil.rmtree(R'C:\Program Files\Electric\bin')
    os.rename(R'C:\Program Files\Electric\update', R'C:\Program Files\Electric\bin')
else:
    # Re-run the program with admin rights
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)

    
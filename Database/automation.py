from urllib.request import urlretrieve
from installer_types import Installer
from tempfile import gettempdir
import pyperclip as clipboard
from pathlib import Path
import pyautogui as gui
import click
import sys
import os


def create_file():
    with open(f'{gettempdir()}\\automation.txt', 'w+') as file:
        pass

create_file()

args = sys.argv[1:]

package_name = args[0]
win32 = args[1]
win64 = args[2]
darwin = args[3]
debian = args[4]
win32_type = args[5]
win64_type = args[6]
darwin_type = args[7]
debian_type = args[8]
json_name = args[9]

def get_installer_type(path : str) -> str:
    # Check file size

    if '.msi' in path:
        return 'MSI'
    
    if '.7z' in path:
        return '7Zip'
    
    if '.zip' in path:
        return 'ZIP'

    size = Path(path).stat().st_size / 1000000

    if size < 100:
        
        gui.hotkey('win', 'd')
        gui.sleep(0.2)
        gui.hotkey('win')
        gui.sleep(0.5)
        gui.typewrite(f'exeinfope {path}')
        gui.sleep(0.1)
        gui.press('enter')
        gui.sleep(3)
        gui.click(744, 616)
        gui.sleep(0.1)
        gui.hotkey('shift', 'end')
        gui.sleep(0.2)
        gui.hotkey('ctrl', 'c')
        gui.sleep(0.1)
        gui.hotkey('alt', 'fn', 'f4')
        gui.sleep(0.1)
        gui.press('enter')
        os.remove(path)
        return clipboard.paste()

    else:
        gui.hotkey('win', 'd')
        gui.sleep(0.2)
        gui.hotkey('win')
        gui.sleep(0.5)
        gui.typewrite(f'exeinfope {path}')
        gui.press('enter')
        gui.sleep(2)

        gui.hotkey('fn', 'f11')
        gui.sleep(0.4)
        gui.press('enter')
        gui.sleep(0.4)
        gui.press('enter')

        gui.click(744, 616)
        gui.sleep(0.5)
        gui.hotkey('shift', 'end')
        gui.sleep(0.5)
        gui.hotkey('ctrl', 'c')
        gui.sleep(0.4)
        gui.hotkey('alt', 'fn', 'f4')
        gui.sleep(0.4)
        gui.press('enter')
        os.remove(path)
        return clipboard.paste()


def generate_json(win32: str, win64: str, darwin: str, debian: str, package_name: str, installer_type: str, win32_type, win64_type, darwin_type, debian_type):

    type: Installer = None

    if 'InstallAware' in installer_type:
        type = Installer.InstallAware

    if 'Squirrel' in installer_type:
        type = Installer.Squirrel

    if 'InstallShield' in installer_type:
        type = Installer.InstallShield

    if 'Nullsoft' in installer_type:
        type = Installer.NullSoft

    if 'Ghost' in installer_type:
        type = Installer.Ghost

    if 'Inno Setup' in installer_type:
        type = Installer.InnoSetup

    if 'Wise' in installer_type:
        type = Installer.Wise
    
    if installer_type == 'MSI':
        type = Installer.Msi
    

    package_name = package_name.replace('\"', '')

    package = {
        json_name.replace('\"', '') : {
            "package-name": f"{package_name}",
            "win32": f"{win32}",
            "win64": f"{win64}",
            "darwin": f"{darwin}",
            "debian": f"{debian}",
            "win32-type": win32_type,
            "win64-type": win64_type,
            "darwin-type": darwin_type,
            "debian-type": debian_type,
            "install-switches": type.value["install-switches"],
            "uninstall-switches": type.value["uninstall-switches"],
            "custom-location": type.value["dir-spec"]
        }
    }

    return package


def download(win64: str):
    path = f'C:\\Users\\tejas\\Downloads\\Setup{win64_type}'
    urlretrieve(win64, path)
    return path


path = download(win64)
installer_type = get_installer_type(path)
gen_json = generate_json(win32, win64, darwin, debian, package_name,
                         installer_type, win32_type, win64_type, darwin_type, debian_type)

os.remove(f'{gettempdir()}\\automation.txt')

click.echo(gen_json)

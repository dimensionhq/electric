from urllib.request import urlretrieve
from installer_types import Installer
from tempfile import gettempdir
import pyperclip as clipboard
from pathlib import Path
import pyautogui as gui
import click
import sys
import re
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


def get_installer_type(path : str) -> str:
    # Check file size

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
        gui.sleep(0.2)
        gui.press('enter')
        gui.sleep(0.2)
        gui.press('enter')

        gui.click(744, 616)
        gui.sleep(0.2)
        gui.hotkey('shift', 'end')
        gui.sleep(0.2)
        gui.hotkey('ctrl', 'c')
        gui.sleep(0.2)
        gui.hotkey('alt', 'fn', 'f4')
        gui.sleep(0.2)
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

    if 'NullSoft' in installer_type:
        type = Installer.NullSoft

    if 'Ghost' in installer_type:
        type = Installer.Ghost

    if 'Inno Setup' in installer_type:
        type = Installer.InnoSetup

    if 'Wise' in installer_type:
        type = Installer.Wise

    package_name = package_name.replace('\"', '')

    package = {
        "package-name": f"{package_name}",
        "win32": f"{win32}",
        "win64": f"{win64}",
        "darwin": f"{darwin}",
        "debian": f"{debian}"
    }

    return package


def smart_detect_type(win32: str, win64: str, darwin: str, debian: str):

    win32_type = None

    if '.exe' in win32:
        win32_type = '.exe'
    if '.msi' in win32:
        win32_type = '.msi'
    if '.zip' in win32:
        win32_type = '.zip'

    win64_type = None
    if '.exe' in win64:
        win64_type = '.exe'

    if '.msi' in win64:
        win64_type = '.msi'

    if '.zip' in win64:
        win64_type = '.zip'

    darwin_type = None
    if '.dmg' in darwin:
        darwin_type = '.dmg'

    if '.pkg' in darwin:
        darwin_type = '.pkg'

    if '.tar.gz' in darwin:
        darwin_type = '.tar.gz'

    debian_type = None
    if '.deb' in debian:
        debian_type = '.deb'

    if '.tar.gz' in debian:
        debian_type = '.tar.gz'

    if '.tar.bz2' in debian:
        debian_type = '.tar.bz2'

    if '.tar.xz' in debian:
        debian_type = '.tar.xz'

    if win32 != '':
        if not win32_type:
            reQuery = re.compile(r'\?.*$', re.IGNORECASE)
            rePort = re.compile(r':[0-9]+', re.IGNORECASE)
            reExt = re.compile(r'(\.[A-Za-z0-9]+$)', re.IGNORECASE)

            # remove query string
            url = reQuery.sub("", win32)

            # remove port
            url = rePort.sub("", url)

            # extract extension
            matches = reExt.search(url)
            extension = ''
            if matches:
                extension = matches.group(1)

            if matches != '.zip' or matches != '.exe' or matches != '.msi':
                pass
            else:
                win32_type = extension

    if win64 != '':
        if not win64_type:
            reQuery = re.compile(r'\?.*$', re.IGNORECASE)
            rePort = re.compile(r':[0-9]+', re.IGNORECASE)
            reExt = re.compile(r'(\.[A-Za-z0-9]+$)', re.IGNORECASE)

            # remove query string
            url = reQuery.sub("", win64)

            # remove port
            url = rePort.sub("", url)

            # extract extension
            matches = reExt.search(url)
            extension = ''
            if matches:
                extension = matches.group(1)

            if matches != '.zip' or matches != '.exe' or matches != '.msi':
                pass
            else:
                win64_type = extension

    if darwin != '':
        if not darwin_type:
            reQuery = re.compile(r'\?.*$', re.IGNORECASE)
            rePort = re.compile(r':[0-9]+', re.IGNORECASE)
            reExt = re.compile(r'(\.[A-Za-z0-9]+$)', re.IGNORECASE)

            # remove query string
            url = reQuery.sub("", darwin)

            # remove port
            url = rePort.sub("", url)

            # extract extension
            matches = reExt.search(url)
            extension = ''
            if matches:
                extension = matches.group(1)

            if matches != '.zip' or matches != '.dmg' or matches != '.pkg' or matches != '.tar.gz':
                pass
            else:
                darwin_type = extension

    if debian != '':
        if not debian_type:
            reQuery = re.compile(r'\?.*$', re.IGNORECASE)
            rePort = re.compile(r':[0-9]+', re.IGNORECASE)
            reExt = re.compile(r'(\.[A-Za-z0-9]+$)', re.IGNORECASE)

            # remove query string
            url = reQuery.sub("", debian)

            # remove port
            url = rePort.sub("", url)

            # extract extension
            matches = reExt.search(url)
            extension = ''
            if matches:
                extension = matches.group(1)
            if matches != '.zip' or matches != '.exe' or matches != '.msi':
                pass
            else:
                debian_type = extension

    return win32_type, win64_type, darwin_type, debian_type


def download(win32: str, win64: str, darwin: str, debian: str):
    win32_type, win64_type, darwin_type, debian_type = smart_detect_type(
        win32, win64, darwin, debian)
    if win32 != '':
        if not win32_type:
            win32_type = input('Failed To Detect Win32 Type Enter The Type : ')
    if win64 != '':
        if not win64_type:
            win64_type = input('Failed To Detect Win64 Type Enter The Type : ')
    if darwin != '':
        if not darwin_type:
            darwin_type = input(
                'Failed To Detect Darwin Type Enter The Type : ')
    if debian != '':
        if not debian_type:
            debian_type = input(
                'Failed To Detect Debian Type Enter The Type : ')
    path = f'C:\\Users\\tejas\\Downloads\\Setup{win64_type}'
    urlretrieve(win64, path)
    return path, win32_type, win64_type, darwin_type, debian_type


path, win32_type, win64_type, darwin_type, debian_type = download(win32, win64, darwin, debian)
installer_type = get_installer_type(path)
gen_json = generate_json(win32, win64, darwin, debian, package_name,
                         installer_type, win32_type, win64_type, darwin_type, debian_type)

os.remove(f'{gettempdir()}\\automation.txt')

click.echo(gen_json)

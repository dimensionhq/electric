from urllib.request import urlretrieve
import pyperclip as clipboard
from InstallerTypes import *
from subprocess import PIPE
import pyautogui as gui
import subprocess
import json
import re

PATH = 'C:\\Users\\tejas\\Downloads\\Setup.exe'
JSON_DIR = 'Test\\sublime-text-3.json'

dictionary = []

with open(JSON_DIR, 'r') as f:
    dictionary = json.loads(f.read())

win32 = dictionary['sublime-text-3']['win32']
win64 = dictionary['sublime-text-3']['win64']
darwin = dictionary['sublime-text-3']['darwin']
debian = dictionary['sublime-text-3']['debian']
package_name = dictionary['sublime-text-3']['package-name']


def get_installer_type(path: str) -> str:
    gui.hotkey('win', 'd')
    gui.sleep(0.2)
    gui.hotkey('win')
    gui.sleep(0.3)
    gui.typewrite('cmd')
    gui.sleep(0.7)
    gui.press('enter')
    gui.sleep(0.3)
    gui.press('esc')
    gui.sleep(1)
    gui.click(960, 570)
    gui.sleep(0.3)
    gui.typewrite(f'exeinfope {path}')
    gui.sleep(0.1)
    gui.press('enter')
    gui.sleep(0.1)
    gui.hotkey('alt', 'fn', 'f4')
    gui.sleep(1.8)
    gui.click(973, 364)

    coords = gui.locateOnScreen(
        R'C:\Users\tejas\Desktop\Automation\Resources\FileSize.png')

    if coords:
        gui.hotkey('fn', 'f11')
        gui.sleep(0.01)
        gui.press('enter')
        gui.sleep(0.01)
        gui.press('enter')

    gui.sleep(0.01)
    gui.click(746, 614)
    gui.sleep(0.1)
    gui.hotkey('shift', 'end')
    gui.sleep(0.01)
    gui.hotkey('ctrl', 'c')
    gui.sleep(0.01)
    gui.hotkey('alt', 'fn', 'f4')
    gui.sleep(0.01)
    gui.press('enter')

    subprocess.call(f'del {PATH}', stdin=PIPE,
                    stdout=PIPE, stderr=PIPE, shell=True)
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

    package = {
        'Package Name': package_name,
        'win32': win32,
        'win64': win64,
        'darwin': darwin,
        'debian': debian,
        'installer-type': type.value,
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
    print(win32_type, win64_type, darwin_type, debian_type)
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
    print(path, win32_type, win64_type, darwin_type, debian_type)
    return path, win32_type, win64_type, darwin_type, debian_type


path, win32_type, win64_type, darwin_type, debian_type = download(
    win32, win64, darwin, debian)
installer_type = get_installer_type(path)
gen_json = generate_json(win32, win64, darwin, debian, package_name,
                         installer_type, win32_type, win64_type, darwin_type, debian_type)
print(gen_json)

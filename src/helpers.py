from menu_selector import show_menu_selector
from subprocess import PIPE
from getpass import getuser

import subprocess
import requests
import platform
import zipfile
import click
import sys
import os


def get_architecture():
    if platform.machine().endswith('64'):
        return 'x64'
    if platform.machine().endswith('86'):
        return 'x32'


def get_download_url(architecture, json):
    if sys.platform == 'win32':
        if architecture == 'x64':
            return json['win64']
        elif architecture == 'x32':
            return json['win32']
        
    elif sys.platform == 'darwin':
        return json['darwin']
    
    elif sys.platform == 'linux':
        return json['debian']


def parse_json_response(json):
    return json['package-name'], json['source'], json['type'], json['switches']


def get_setup_name(download_type, package_name):
    if plat == 'win32':
        download_path = 'C:\\Users\\{0}\\Downloads\\'.format(get_user())
        architecture = get_architecture()
        package = package_name.split()
        package.insert(0, download_path)
        package.append('Setup')
        package.append(architecture)
        package.append(download_type)
        return ''.join(package)
    
    elif plat == 'darwin':
        download_path = rf'/Users/{getuser()}/Downloads/'
        package = package_name.split()
        package.insert(0, download_path)
        package.append('Setup')
        package.append(download_type)
        return ''.join(package)
    
    elif plat == 'linux':
        download_path = rf'/home/{getuser()}/Downloads/'
        package = package_name.split()
        package.insert(0, download_path)
        package.append('Setup')
        package.append(download_type)
        return ''.join(package)


# noinspection DuplicatedCode
def download(url, download_type: str, package_name):
    setup_name = get_setup_name(download_type, package_name)

    with open(setup_name, "wb") as f:
        response = requests.get(url, stream=True)
        total_length = response.headers.get('content-length')

        if total_length is None:
            f.write(response.content)
        else:
            dl = 0
            full_length = int(total_length)
            
            for data in response.iter_content(chunk_size=4096):
                dl += len(data)
                f.write(data)
                complete = int(50 * dl / total_length)
                fill_c, unfill_c = chr(9608) * complete, chr(9617) * (50 - complete)
                sys.stdout.write(f"\r|{fill_c}{unfill_c}| {round(dl / 1000000, 2)} / {round(full_length / 1000000, 2)} MB")
                sys.stdout.flush()


def install_package(package_name, switches, download_type):
    file_name = get_setup_name(download_type, package_name)
    
    if plat == 'win32':
        if download_type == '.exe':
            command = file_name + ' '
            for switch in switches:
                command = command + ' ' + switch
            subprocess.call(command)
            
        elif download_type == '.msi':
            command = 'msiexec.exe /i' + file_name + ' '
            for switch in switches:
                command = command + ' ' + switch
            subprocess.call(command)
            
        elif download_type == '.zip':
            click.echo(click.style(f'Unzipping File At {file_name}', fg='green'))
            zip_directory = fR'C:\Users\{getuser()}\Downloads\\{package_name}'
            with zipfile.ZipFile(file_name, 'r') as zip_ref:
                zip_ref.extractall(zip_directory)
            executable_list = []
            for name in os.listdir(zip_directory):
                if name.endswith('.exe'):
                    executable_list.append(name)
            executable_list.append('Exit')
            show_menu_selector(executable_list, 'C:\\Users\\{0}\\Downloads\\{1}'.format(get_user(), package_name))

    if plat == 'darwin':
        mount_dmg = f'hdiutil attach -nobrowse {file_name}'


def cleanup(download_type, package_name):
    setup_name = get_setup_name(download_type, package_name)
    command = 'del ' + setup_name
    subprocess.call(command, shell=True)

def run_uninstall(command : str):
    subprocess.call(command, stdout=PIPE, stdin=PIPE, stderr=PIPE)

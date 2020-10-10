import platform
from subprocess import PIPE
from sys import platform as plat
from getpass import getuser
import subprocess
import sys
from click.decorators import command
import requests
import zipfile
import click
import os
from menu_selector import show_menu_selector


def get_architecture() -> str:
    if platform.machine().endswith('64'):
        return 'x64'
    if platform.machine().endswith('86'):
        return 'x32'


def get_download_url(architecture, json) -> str:
    if plat == 'win32':
        if architecture == 'x64':
            return json['win64']
        if architecture == 'x32':
            return json['win32']
    if plat == 'darwin':
        return json['darwin']
    if plat == 'linux':
        return json['debian']


def parse_json_response(json) -> tuple:
    return json['package-name'], json['source'], json['type'], json['switches']


def get_setup_name(download_type, package_name) -> str:
    if plat == 'win32':
        download_path = fR'C:\Users\roopa\Downloads\\'
        architecture = get_architecture()
        package = package_name.split()
        package.insert(0, download_path)
        package.append('Setup')
        package.append(architecture)
        package.append(download_type)
        return ''.join(package)
    if plat == 'darwin':
        download_path = fR'/Users/{getuser()}/Downloads/'
        package = package_name.split()
        package.insert(0, download_path)
        package.append('Setup')
        package.append(download_type)
        return ''.join(package)
    if plat == 'linux':
        download_path = fR'/home/{getuser()}/Downloads/'
        package = package_name.split()
        package.insert(0, download_path)
        package.append('Setup')
        package.append(download_type)
        return ''.join(package)


# noinspection DuplicatedCode
def download(url, download_type : str, package_name):
    setup_name = get_setup_name(download_type, package_name)

    with open(setup_name, "wb") as f:
        response = requests.get(url, stream=True)
        total_length = response.headers.get('content-length')

        if total_length is None:
            f.write(response.content)
        else:
            dl = 0
            total_length = int(total_length)
            for data in response.iter_content(chunk_size=4096):
                dl += len(data)
                f.write(data)
                done = int(50 * dl / total_length)
                sys.stdout.write(f"\r|%s%s| {round(dl / 1000000, 2)} / {round(total_length / 1000000, 2)} MB" % ('█' * done, '░' * (50 - done)))
                sys.stdout.flush()


def install_package(package_name, switches, download_type):
    file_name = get_setup_name(download_type, package_name)
    if plat == 'win32':
        if download_type == '.exe':
            command = file_name + ' '
            for switch in switches:
                command = command + ' ' + switch
            subprocess.call(command)
        if download_type == '.msi':
            command = 'msiexec.exe /i' + file_name + ' '
            for switch in switches:
                command = command + ' ' + switch
            subprocess.call(command)
        if download_type == '.zip':
            click.echo(click.style(f'Unzipping File At {file_name}', fg='green'))
            zip_directory = fR'C:\Users\roopa\Downloads\\{package_name}'
            with zipfile.ZipFile(file_name, 'r') as zip_ref:
                zip_ref.extractall(zip_directory)
            executable_list = []
            for name in os.listdir(zip_directory):
                if name.endswith('.exe'):
                    executable_list.append(name)
            executable_list.append('Exit')
            show_menu_selector(executable_list, fR'C:\Users\roopa\Downloads\\{package_name}')

    if plat == 'darwin':
        mount_dmg = f'hdiutil attach -nobrowse {file_name}'


def cleanup(download_type, package_name):
    setup_name = get_setup_name(download_type, package_name)
    command = 'del ' + setup_name
    subprocess.call(command, shell=True)

def run_uninstall(command : str):
    subprocess.call(command, stdout=PIPE, stdin=PIPE, stderr=PIPE)

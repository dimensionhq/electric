######################################################################
#                           HELPERS / UTILS                          #
######################################################################

from constants import valid_install_exit_codes, valid_uninstall_exit_codes
from subprocess import Popen, PIPE, CalledProcessError, check_call, call
from Classes.PathManager import PathManager
from timeit import default_timer as timer
from colorama import Back, Fore, Style
from urllib.request import urlretrieve
from Classes.Metadata import Metadata
import Classes.PackageManager as mgr
from viruscheck import virus_check
from Classes.Packet import Packet
from googlesearch import search
import pyperclip as clipboard
from datetime import datetime
from decimal import Decimal
from signal import SIGTERM
from switch import Switch
from extension import *
from registry import *
from halo import Halo
from logger import *
from limit import *
import webbrowser
import keyboard
import requests
import tempfile
import registry
import difflib
import zipfile
import hashlib
import ctypes
import shutil
import random
import pickle
import cursor
import click
import json
import info
import sys
import os
import re

index = 0
final_value = None
path = ''

appdata_dir = PathManager.get_appdata_directory()

class HiddenPrints:
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout


def get_recent_logs() -> list:
    with open(Rf'{appdata_dir}\electric-log.log', 'r') as file:
        data = file.read()
    return data.splitlines()


def generate_report(name: str):
    return f'''
{{
NAME :: {name}
VERSION :: Coming Soon!
LOGFILE :: <--attachment-->
}}
    '''


def is_admin():
    try:
        is_admin = (os.getuid() == 0)
    except AttributeError:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
    return is_admin


def get_download_url(packet):
    return packet.win64



def generate_dict(path: str, package_name: str):
    return {
        'directory': path,
        'package_name': package_name,
        'size': os.stat(path).st_size,
    }


def dump_pickle(data: dict, filename: str):
    with open(Rf'{tempfile.gettempdir()}\electric\{filename}.pickle', 'wb') as f:
        pickle.dump(data, f)


def retrieve_data(filename: str):
    if os.path.isfile(Rf'{tempfile.gettempdir()}\electric\{filename}.pickle'):
        with open(Rf'{tempfile.gettempdir()}\electric\{filename}.pickle', 'rb') as f:
            final = pickle.loads(f.read())
            return final


def check_existing_download(package_name: str, download_type) -> bool:
    data = retrieve_data('downloadcache')
    if data:
        if data['package_name'] == package_name:
            try:
                filesize = os.stat(data['directory'] + download_type).st_size
            except FileNotFoundError:

                if download_type not in data['directory']:
                    os.rename(data['directory'], data['directory'] + download_type)
                try:
                    filesize = os.stat(data['directory']).st_size
                except FileNotFoundError:
                    filesize = os.stat(data['directory'] + download_type).st_size
            if filesize < data['size']:
                # Corrupt Installation
                return False
            return data['directory']
    return False


def get_chunk_size(total_size: str):
    size = int(total_size)
    size = size / 1000000
    if size < 7:
        return 4096
    else:
        return 7096

def get_color_escape(r, g, b, background=False):
    return '\033[{};2;{};{};{}m'.format(48 if background else 38, r, g, b)


def check_resume_download(package_name: str, metadata: Metadata):
    data = retrieve_data('unfinishedcache')
    try:
        if os.path.isfile(data['path']) and package_name == data['name']:
            write(f'Resuming Existing Download At => {tempfile.gettempdir()}', 'blue', metadata)
            return os.stat(data['path']).st_size, data['path']
        else:
            return (None, None)
    except:
        return (None, None)


def send_req_bundle():
    REQA = 'https://electric-package-manager.herokuapp.com/bundles/windows'
    time = 0.0
    response = requests.get(REQA, timeout=15)
    time = response.elapsed.total_seconds()
    return response.json(), time


def download(url: str, package_name: str, metadata: Metadata, download_type: str):
    cursor.hide()
    path = check_existing_download(package_name, download_type)
    if not os.path.isdir(Rf'{tempfile.gettempdir()}\electric'):
        os.mkdir(Rf'{tempfile.gettempdir()}\electric')

    if isinstance(path, bool):
        path = Rf'{tempfile.gettempdir()}\electric\Setup{download_type}'
    else:
        write(f'Found Existing Download At => {tempfile.gettempdir()}', 'blue', metadata)
        return path, True

    while os.path.isfile(path):
        path = Rf'{tempfile.gettempdir()}\electric\Setup{random.randint(200, 100000)}'

    size, newpath = check_resume_download(package_name, metadata)
    # TODO: Display Progress Bar If Already Downloaded

    if not size:
        dump_pickle({'path': path, 'url': url, 'name': package_name, 'download-type': download_type}, 'unfinishedcache')

    with open(newpath if newpath else path, 'wb' if not size else 'ab') as f:
        if size:
            response = requests.get(url, stream=True, headers={'Range': 'bytes=%d-' % size})
        else:
            response = requests.get(url, stream=True)
        total_length = response.headers.get('content-length')
        chunk_size = get_chunk_size(total_length)
        if total_length is None:
            f.write(response.content)
        else:
            dl = 0
            full_length = int(total_length)
            # 7096 => 7.48, 8.001
            # 4096 => 6.87, 6.005, 7.59, 7.35
            for data in response.iter_content(chunk_size=chunk_size):
                dl += len(data)
                f.write(data)

                if metadata.no_progress:
                    sys.stdout.write(
                        f'\r{round(dl / 1000000, 1)} / {round(full_length / 1000000, 1)} MB')
                    sys.stdout.flush()

                elif not metadata.no_progress and not metadata.silent:
                    complete = int(25 * dl / full_length)
                    # fill_c =  Fore.LIGHTBLACK_EX + Style.DIM + '█' * complete
                    # fill_c = click.style('█', fg='bright_black') * complete
                    # unfill_c = Fore.BLACK + '█' * (25 - complete)   
                    fill_c =  Fore.GREEN + Style.DIM + '=' * complete
                    unfill_c = Fore.LIGHTBLACK_EX + '-' * (25 - complete)

                    # sys.stdout.write(
                    #     f'\r⚡ {fill_c}{unfill_c} ⚡ {round(dl / full_length * 100, 1)} % ')

                    sys.stdout.write(
                        f'\r{fill_c}{unfill_c} {Fore.RESET + Style.DIM} {round(dl / 1000000, 1)} / {round(full_length / 1000000, 1)} MB {Fore.RESET}')
                    # sys.stdout.write(
                    #     f'\r{fill_c}{unfill_c} ⚡ {round(dl / full_length * 100, 1)} % ⚡ {round(dl / 1000000, 1)} / {round(full_length / 1000000, 1)} MB')
                    
                    sys.stdout.flush()
    os.remove(Rf"{tempfile.gettempdir()}\electric\unfinishedcache.pickle")
    dump_pickle(generate_dict(newpath if newpath else path, package_name), 'downloadcache')
    if not newpath:
        return path, False
    else:
        return newpath, False


def get_error_cause(error: str, display_name: str, method: str, metadata: Metadata) -> str:
    log_info(f'{error} ==> {method}', metadata.logfile)
    if method == 'installation':
        for code in valid_install_exit_codes:
            if f'exit status {code}' in error:
                return ['no-error']

    if method == 'uninstallation':
        for code in valid_uninstall_exit_codes:
            if f'exit status {code}' in error:
                return ['no-error']

    if 'exit status 1603' in error:
        click.echo(click.style('\nAdministrator Elevation Required Or Unknown Error. Exit Code [1603]', fg='red'))
        return get_error_message('1603', 'installation', display_name)

    if 'exit status 1639' in error:
        click.echo(click.style(f'\nElectric Installer Passed In Invalid Parameters For Installation. Exit Code [0002]', fg='red'))
        return get_error_message('0002', 'installation', display_name)

    if 'exit status 1' in error:
        click.echo(click.style(f'\nUnknown Error. Exited With Code [0000]', fg='red'))
        handle_unknown_error(error)
        return get_error_message('0000', 'installation', display_name)

    if '[WinError 740]' in error and 'elevation' in error:
        # Process Needs Elevation To Execute
        click.echo(click.style(f'\nAdministrator Elevation Required. Exit Code [0001]', fg='red'))
        return get_error_message('0001', 'installation', display_name)

    if 'exit status 2' in error or 'exit status 1' in error:
        # User Declined Prompt Asking For Permission
        click.echo(click.style(f'\nAdministrative Privileges Declined. Exit Code [0101]', fg='red'))
        return get_error_message('0101', 'installation', display_name)

    if 'exit status 4' in error:
        # Fatal Error During Installation
        click.echo(click.style(f'\nFatal Error. Exit Code [1111]', fg='red'))
        return get_error_message('1111', 'installation', display_name)

    if '[WinError 87]' in error and 'incorrect' in error:
        click.echo(click.style(f'\nElectric Installer Passed In Invalid Parameters For Installation. Exit Code [0002]', fg='red'))
        return get_error_message('0002', 'installation', display_name)

    if 'exit status 3010' or 'exit status 2359301' in error:
        # Installer Requesting Reboot
        return get_error_message('1010', 'installation', display_name)

    else:
        click.echo(click.style(f'\nUnknown Error. Exited With Code [0000]', fg='red'))
        handle_unknown_error(error)
        return get_error_message('0000', 'installation', display_name)


def run_cmd(command: str, metadata: Metadata, method: str, display_name: str, halo: Halo):
    log_info(f'Running command: {command}', metadata.logfile)
    command = command.replace('\"\"', '\"').replace('  ', ' ')
    # print('Running Command => ', command)
    try:
        check_call(command, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    except (CalledProcessError, OSError, FileNotFoundError) as err:
        if halo:
            halo.stop()
        keyboard.add_hotkey(
        'ctrl+c', lambda: os._exit(0))
        disp_error_msg(get_error_cause(str(err), display_name, method, metadata), metadata)


def install_package(path, packet: Packet, metadata: Metadata) -> str:
    download_type = packet.win64_type
    custom_install_switch = packet.custom_location
    directory = packet.directory
    package_name = packet.json_name
    switches = packet.install_switches

    if download_type == '.exe':
        if '.exe' not in path:
            if not os.path.isfile(path + '.exe'):
                os.rename(path, f'{path}.exe')
            path = path + '.exe'
        command = path + ' '

        if custom_install_switch:
            if directory and directory != '':
                if '/D=' in custom_install_switch:
                    idx = 0
                    for switch in switches:
                        if idx == 0:
                            command = command + switch
                            continue
                        command = command + ' ' + switch
                        idx += 1

                    command += ' ' + custom_install_switch + f'{directory}'
                else:
                    for switch in switches:
                        command += ' ' + switch

                    command += ' ' + custom_install_switch + f'"{directory}"'
                if directory == '':
                    click.echo(click.style(
                        f'Installing {package_name} To Default Location, Custom Installation Directory Not Supported By This Installer!', fg='yellow'))

        if not directory:
            for switch in switches:
                command = command + ' ' + switch

        run_cmd(command, metadata, 'installation', packet.display_name, None)

    elif download_type == '.msi':
        command = 'msiexec.exe /i ' + path + ' '
        for switch in switches:
            command = command + ' ' + switch

        if not is_admin():
            click.echo(click.style(
                '\nAdministrator Elevation Required. Exit Code [0001]', fg='red'))
            disp_error_msg(get_error_message('0001', 'installation', packet.display_name), metadata)
            handle_exit('ERROR', None, metadata)
        run_cmd(command, metadata, 'installation', packet.display_name, None)

    elif download_type == '.zip':
        if not metadata.no_color:
            click.echo(click.style(
                f'Unzipping File At {path}', fg='green'))
        if metadata.no_color:
            click.echo(click.style(
                f'Unzipping File At {path}'))

        zip_directory = fR'{tempfile.gettempdir()}\\{package_name}'
        with zipfile.ZipFile(path, 'r') as zip_ref:
            zip_ref.extractall(zip_directory)
        executable_list = []
        for name in os.listdir(zip_directory):
            if name.endswith('.exe'):
                executable_list.append(name)
        executable_list.append('Exit')

        file_path = fR'{tempfile.gettempdir()}\\{package_name}'

        def trigger():
            click.clear()
            for executable in executable_list:
                if executable == executable_list[index]:
                    print(Back.CYAN + executable + Back.RESET)
                else:
                    print(executable)

        trigger()

        def up():
            global index
            if len(executable_list) != 1:
                index -= 1
                if index >= len(executable_list):
                    index = 0
                    trigger()
                    return
                trigger()

        def down():
            global index
            if len(executable_list) != 1:
                index += 1
                if index >= len(executable_list):
                    index = 0
                    trigger()
                    return
                trigger()

        def enter():
            if executable_list[index] == 'Exit':
                os._exit(0)

            else:
                path = file_path + '\\' + executable_list[index]
                click.echo(click.style(
                    f'Running {executable_list[index]}. Hit Control + C to Quit', fg='magenta'))
                call(path, stdout=PIPE, stdin=PIPE, stderr=PIPE)
                quit()

        keyboard.add_hotkey('up', up)
        keyboard.add_hotkey('down', down)
        keyboard.add_hotkey('enter', enter)
        keyboard.wait()


def get_configuration_data(username: str, description: str, uses_editor: bool, include_editor: bool, editor: str, include_python: bool, include_node: bool):
    base_configuration = [
        '[ Info ]\n',
        '# Go To https://www.electric.sh/electric-configuration-documentation/ For More Information\n',
        f'Publisher => \"{username}\"\n',
        f'Description => \"{description}\"\n'
    ]

    required_packages = []

    if uses_editor and include_editor and editor:
        base_configuration.append('\n[ Editor-Configuration ]\n')
        if editor == 'Visual Studio Code':
            base_configuration.append(f'Editor => \"{editor}\"\n\n[ Editor-Extensions ]\n<vscode:name>\n')
            required_packages.append('visual-studio-code')
        if editor == 'Atom':
            base_configuration.append(
                f'Editor => \"{editor}\"\n\n[ Editor-Extensions ]\n<atom:name>\n')
            required_packages.append('atom')

    if include_python:
        base_configuration.append('\n[ Pip-Packages ]\n<pip:name>\n')
        required_packages.append('python')

    if include_node:
        base_configuration.append('\n[ Node-Packages ]\n<npm:name>\n')
        required_packages.append('nodejs')

    requirements = str(required_packages).replace('[', '').replace(']', '').replace(',', '\n').replace('\'', '').replace('\n ', '\n')
    base_configuration.insert(4, f'\n[ Packages ]\n{requirements}\n')
    return base_configuration

def get_correct_package_names(res: str) -> list:
    package_names = []
    for package in res:
        package_names.append(package)
    return package_names


def get_hash_algorithm(checksum: str):
    # A function to detect the hash algorithm used in checksum
    hashes = {32: 'md5', 40: 'sha1', 64: 'sha256', 128: 'sha512'}
    return hashes[len(checksum)] if len(checksum) in hashes else None


def get_checksum(bytecode: bytes, hash_algorithm: str):
    # A function to get the checksum from bytecode
    hash_type = getattr(hashlib, hash_algorithm, None)

    if hash_type:
        return hash_type(bytecode).hexdigest()

    return None


def send_req_all() -> dict:
    REQA = 'https://electric-package-manager.herokuapp.com/packages/windows'
    time = 0.0
    response = requests.get(REQA, timeout=15)
    time = response.elapsed.total_seconds()
    return response.json(), time


def get_pid(exe_name):
    proc = Popen('tasklist', stdin=PIPE, stdout=PIPE, stderr=PIPE)
    output, _ = proc.communicate()
    output = output.decode('utf-8')
    lines = output.splitlines()
    for line in lines:
        if exe_name in line:
            return line.split()[1]


def find_approx_pid(exe_name, display_name) -> str:
    proc = Popen('tasklist /FI "Status eq RUNNING"', stdin=PIPE, stdout=PIPE, stderr=PIPE)
    output, _ = proc.communicate()
    output = output.decode('utf-8')
    lines = output.splitlines()

    cleaned_up_names = []
    for line in lines:
        try:
            cleaned_up_names.append(line.split()[0].replace('.exe', '').lower())
        except IndexError:
            continue

    matches = difflib.get_close_matches(display_name.lower(), cleaned_up_names, n=1, cutoff=0.65)

    if matches != []:
        for line in lines:
            if matches[0] in line.lower():
                return line.split()[1]

    return 1


def handle_exit(status: str, setup_name: str, metadata: Metadata):
    finish_log()
    if status == 'Downloaded' or status == 'Installing' or status == 'Installed':
        exe_name = setup_name.split('\\')[-1]
        os.kill(int(get_pid(exe_name)), SIGTERM)

        write('SafetyHarness Successfully Created Clean Exit Gateway',
              'green', metadata)
        write('\nRapidExit Using Gateway From SafetyHarness Successfully Exited With Code 0',
              'light_blue', metadata)
        os._exit(0)

    if status == 'Got Download Path':
        write('\nRapidExit Successfully Exited With Code 0', 'green', metadata)
        os._exit(0)

    if status == 'Downloading':
        write('\n\nRapidExit Successfully Exited With Code 0', 'green', metadata)
        os._exit(0)
    else:
        write('\nRapidExit Successfully Exited With Code 0', 'green', metadata)
        os._exit(0)


def kill_running_proc(package_name: str, display_name: str, metadata: Metadata):
    parts = package_name.split('-')
    name = ' '.join([p.capitalize() for p in parts])
    pid = int(find_approx_pid(package_name, display_name))
    if pid == 1:
        return
    if pid and pid != 1:
        if metadata.yes:
            write(f'Terminating {name}.', 'green', metadata)
            os.kill(pid, SIGTERM)
            return
        if metadata.silent:
            os.kill(pid, SIGTERM)
            return
        terminate = click.confirm(
            f'Electric Detected {name} Running In The Background. Would You Like To Terminate It?')
        if terminate:
            write(f'Terminating {name}.', 'green', metadata)
            os.kill(pid, SIGTERM)
        else:
            write('Aborting Installation!', 'red', metadata)
            write_verbose(
                f'Aborting Installation Due To {name} Running In Background', metadata)
            write_debug(
                f'Aborting Installation Due To {name} Running In Background. Process Was Not Terminated.', metadata)
            os._exit(1)


def kill_proc(proc, metadata: Metadata):
    if proc is not None:
        proc.terminate()
        write('SafetyHarness Successfully Created Clean Exit Gateway',
              'green', metadata)
        write('\nRapidExit Using Gateway From SafetyHarness Successfully Exited With Code 0',
              'light_blue', metadata)
        os._exit(0)
    else:
        write('\nRapidExit Successfully Exited With Code 0',
              'green', metadata)
        os._exit(0)


def assert_cpu_compatible() -> int:
    cpu_count = os.cpu_count()
    print(cpu_count)


def find_existing_installation(package_name: str, display_name: str):
    key = registry.get_uninstall_key(package_name, display_name)

    if key:
        return True
    return False


def get_install_flags(install_dir: str, no_cache: bool, sync: bool, metadata: Metadata):
    flags = []
    if metadata.verbose:
        flags.append('--verbose')
    if metadata.debug:
        flags.append('--debug')
    if metadata.no_color:
        flags.append('--no-color')
    if metadata.no_progress:
        flags.append('--no-progress')
    if metadata.yes:
        flags.append('--yes')
    if metadata.silent:
        flags.append('--silent')
    if metadata.logfile:
        flags.append('--logfile')
    if metadata.virus_check:
        flags.append('--virus-check')
    if metadata.reduce_package:
        flags.append('--reduce')
    if metadata.rate_limit:
        flags.append(f'--rate-limit={metadata.rate_limit}')
    if install_dir:
        flags.append(f'--install-dir={install_dir}')
    if sync:
        flags.append('--sync')
    if no_cache:
        flags.append('--no-cache')

    return flags

def refresh_environment_variables() -> bool:
    proc = Popen(Rf'{PathManager.get_current_directory()}\scripts\refreshvars.cmd',
                 stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
    output, err = proc.communicate()
    if 'Finished' in output.decode('utf-8'):
        return True
    else:
        print('An error occurred')
        print(err.decode('utf-8'))
        return False


def check_virus(path: str, metadata: Metadata):
    detected = virus_check(path)
    if detected:
        for value in detected.items():
            if not metadata.silent and not metadata.no_color:
                click.echo(click.style(f'\n{value[0]} => {value[1]}', fg='yellow'))
            elif metadata.no_color and not metadata.silent:
                click.echo(click.style(f'\n{value[0]} => {value[1]}', fg='white'))
            else:
                continue_install = 'y'
        if not metadata.silent:
            continue_install = click.confirm('Would You Like To Continue?')
            if continue_install:
                pass
            else:
                handle_exit('Virus Check', '', metadata)
    else:
        click.echo(click.style('No Viruses Detected!', fg='green'))


def setup_supercache():
    if not os.path.isdir(Rf'{appdata_dir}\supercache.json'):
        os.mkdir(appdata_dir)
    res, time = send_req_all()
    with open(Rf'{appdata_dir}\supercache.json', 'w+') as file:
        del res['_id']
        file.write(json.dumps(res, indent=4))

    return res, time


def update_supercache(res, metadata: Metadata):
    if isfile(f'{tempfile.gettempdir()}\electric'):
        log_info(f'Removing all data in {tempfile.gettempdir()}\electric', metadata.logfile)
        shutil.rmtree(f'{tempfile.gettempdir()}\electric')
        log_info(f'Deleted all data in {tempfile.gettempdir()}\electric successfully.', metadata.logfile)

    if not os.path.isdir(appdata_dir):
        log_info('Setting up supercache because it doesn\'t exist.', metadata.logfile)
        setup_supercache()
        log_info('Successfully set up supercache.', metadata.logfile)

    filepath = Rf'{appdata_dir}\supercache.json'
    file = open(filepath, 'w+')
    log_info(f'Dumping json to {filepath}', metadata.logfile if metadata else None)
    file.write(json.dumps(res, indent=4))
    file.close()
    logpath = Rf'{appdata_dir}\superlog.txt'
    logfile = open(logpath, 'w+')
    now = datetime.now()
    log_info(f'Writing {str(now)} to {logpath}', metadata.logfile if metadata else None)
    logfile.write(str(now))
    logfile.close()
    log_info(f'Successfully wrote date and time to {logpath}', metadata.logfile if metadata else None)


def check_newer_version(new_version) -> bool:
    current_version = int(info.__version__.replace('.', '').replace('a', '').replace('b', ''))
    new_version = int(new_version.replace('.', ''))
    if current_version < new_version:
        return True
    return False


def check_for_updates():
    res = requests.get('http://electric-package-manager.herokuapp.com/version/windows', timeout=10)
    js = res.json()
    version_dict = json.loads(js)

    if version_dict:
        new_version = version_dict['version']
        if check_newer_version(new_version):
            # Implement Version Check
            if click.confirm('A new update for electric is available, would you like to proceed with the update?'):
                click.echo(click.style('Updating Electric..', fg='green'))
                UPDATEA = 'https://electric-package-manager.herokuapp.com/update/windows'

                def is_admin():
                    try:
                        return ctypes.windll.shell32.IsUserAnAdmin()
                    except:
                        return False


                if is_admin():
                    with open(Rf'C:\Program Files (x86)\Electric\Update.7z', 'wb') as f:
                        response = requests.get(UPDATEA, stream=True)
                        total_length = response.headers.get('content-length')

                        if total_length is None:
                            f.write(response.content)
                        else:
                            dl = 0
                            full_length = int(total_length)

                            for data in response.iter_content(chunk_size=7096):
                                dl += len(data)
                                f.write(data)

                                complete = int(20 * dl / full_length)
                                fill_c, unfill_c = '#' * complete, ' ' * (20 - complete)
                                sys.stdout.write(
                                    f'\r[{fill_c}{unfill_c}] ⚡ {round(dl / full_length * 100, 1)} % ⚡ {round(dl / 1000000, 1)} / {round(full_length / 1000000, 1)} MB')
                                sys.stdout.flush()


                    command = R'"C:\Program Files (x86)\Electric\updater\updater.exe"'

                    Popen(command, close_fds=True, shell=True)
                    click.echo(click.style('\nSuccessfully Updated Electric!', fg='green'))
                    sys.exit()
                else:
                    click.echo(click.style('Re-Run Electric As Administrator To Update', fg='red'))


def check_supercache_valid():
    filepath = Rf'{appdata_dir}\superlog.txt'
    if os.path.isfile(filepath):
        with open(filepath, 'r') as f:
            contents = f.read()
        date = datetime.strptime(contents, '%Y-%m-%d %H:%M:%S.%f')
        if (datetime.now() - date).days < 1:
            return True

        if (datetime.now() - date).days > 3:
            check_for_updates()
    return False


def handle_cached_request():
    filepath = Rf'{appdata_dir}\supercache.json'
    if os.path.isfile(filepath):
        file = open(filepath)
        start = timer()
        res = json.load(file)
        file.close()
        end = timer()
        if res:
            return res, (end - start)
        else:
            res, time = setup_supercache()
            return res, time
    else:
        res, time = setup_supercache()
        return res, time


def generate_metadata(no_progress, silent, verbose, debug, no_color, yes, logfile, virus_check, reduce, rate_limit):
    return Metadata(no_progress, no_color, yes, silent, verbose, debug, logfile, virus_check, reduce, rate_limit)


def disp_error_msg(messages: list, metadata: Metadata):
    if 'no-error' in messages:
        return

    reboot = False
    websites = []
    commands = []
    support_ticket = False
    idx = 0
    for msg in messages:
        if idx == 0:
            click.echo(click.style(msg, fg='yellow'))
            idx += 1
            continue
        if 'Reboot' in msg:
            reboot = True
            break
        if 'http' in msg:
            websites.append(msg.strip())
            click.echo(click.style(msg, fg='blue'))
            idx += 1
            continue
        if 'electric install' in msg:
            commands.append(re.findall(r'\`(.*?)`', msg))
        if 'NAME' and 'VERSION' in msg:
            click.echo(click.style(msg, fg='green'))
            support_ticket = True
            break
        else:
            click.echo(msg)

        idx += 1

    if support_ticket:
        click.echo('By sending a support ticket, you agree to the Terms And Conditions (https://www.electric.sh/support/terms-and-conditions)')
        sending_ticket = click.confirm('Would you like to send the support ticket ?')
        if sending_ticket:
            with Halo('', spinner='bounce') as h:
                res = requests.post('http://electric-package-manager.herokuapp.com/windows/support-ticket/', json={'Logs': get_recent_logs()})
                if res.status_code == 200:
                    h.stop()
                    click.echo(click.style('Successfully Sent Support Ticket!', fg='green'))
                else:
                    h.fail('Failed To Send Support Ticket')

    if reboot:
        reboot = click.confirm('Would you like to reboot?')
        if reboot:
            os.system('shutdown /R')

    if commands:
        run = click.confirm('Would You Like To Install Node?')
        if run:
            print('\n')
            os.system(commands[0][0])

    if websites:
        website = click.confirm('Would You Like To Visit Any Of The Above Websites?')
        if website:
            try:
                webpage = int(click.prompt('Which Webpage Would You Like To Visit? ')) - 1
            except:
                handle_exit('ERROR', None, metadata)
            try:
                webbrowser.open(websites[webpage][8:])
            except:
                pass
    handle_exit('ERROR', None, metadata)


def get_error_message(code: str, method: str, display_name: str):
    attr = method.strip('ation')
    with Switch(code) as code:
        if code('0001'):
            return [
                f'\n[0001] => {method.capitalize()} failed because the software you tried to {attr} requires administrator permissions.',
                f'\n\nHow To Fix:\n\nRun Your Command Prompt Or Powershell As Administrator And Retry {method.capitalize()}.\n\nHelp:',
                '\n[1] <=> https://www.howtogeek.com/194041/how-to-open-the-command-prompt-as-administrator-in-windows-8.1/',
                '\n[2] <=> https://www.top-password.com/blog/5-ways-to-run-powershell-as-administrator-in-windows-10/\n\n'
                f'If that doesn\'t work, please file a support ticket at => https://www.electric.sh/support\n'
            ]

        elif code('0002'):
            return [
                f'\n[0002] => {method.capitalize()} failed because the installer provided an incorrect command for {attr}.',
                '\nWe recommend you raise a support ticket with the data generated below:',
                generate_report(display_name),
                '\nHelp:\n',
                'https://www.electric.sh/troubleshoot'
            ]

        elif code('0000'):
            return [
                f'\n[0000] => {method.capitalize()} failed due to an unknown reason.',
                '\nWe recommend you raise a support ticket with the data generated below:',
                generate_report(display_name),
                '\nHelp:',
                f'\n[1] <=> https://www.electric.sh/troubleshoot'
            ]

        elif code('0011'):
            clipboard.copy('electric install nodejs')
            return [
                '\n[0011] => Node(npm) is not installed on your system.',
                '\n\nHow To Fix:\n',
                'Run `electric install nodejs` [ Copied To Clipboard ] To Install Node(npm)'
            ]

        elif code('1603'):
            return [
                f'\n[1603] => {method.capitalize()} might have failed because the software you tried to {attr} might require administrator permissions.',
                f'\n\nHow To Fix:\n\nRun Your Command Prompt Or Powershell As Administrator And Retry {method.capitalize()}.\n\nHelp:',
                '\n[1] <=> https://www.howtogeek.com/194041/how-to-open-the-command-prompt-as-administrator-in-windows-8.1/',
                '\n[2] <=> https://www.top-password.com/blog/5-ways-to-run-powershell-as-administrator-in-windows-10/\n\n',
            ]

        elif code('0010'):
            clipboard.copy('electric install python3')
            return [
                '\n[0010] => Python(pip) is not installed on your system.',
                '\n\nHow To Fix:\n',
                'Run `electric install python3` [ Copied To Clipboard ] To install Python(pip).\n\nHelp:',
                '\n[1] <=> https://www.educative.io/edpresso/how-to-add-python-to-path-variable-in-windows',
                '\n[2] <=> https://stackoverflow.com/questions/23708898/pip-is-not-recognized-as-an-internal-or-external-command'
                ]

        elif code('1010'):
            return [
                f'\n[1010] => Installer Has Requested A Reboot In Order To Complete {method.capitalize()}.\n'
            ]

        elif code('1111'):
            return [
                f'\n[1111] => The {attr.capitalize()}er For This Package Failed Due To A Fatal Error. This is likely not an issue or error with electric.',
                '\n\nWe recommend you raise a support ticket with the data generated below:',
                generate_report(display_name),
                '\nHelp:\n',
                '\n[1] <=> https://www.electric.sh/errors/1111',
                '\n[2] <=> https://www.electric.sh/support',
            ]

        elif code('0101'):
            return [
                f'\n[0101] => The installer / uninstaller was denied of Administrator permissions And failed to initialize successfully.',
                '\n\nHow To Fix:\n',
                'Make sure you accept prompt asking for administrator privileges or alternatively: \n',
                f'Run Your Command Prompt Or Powershell As Administrator And Retry {method.capitalize()}.\n\n\nHelp:',
                '\n[1] <=> https://www.electric.sh/errors/0101',
                '\n[2] <=> https://www.howtogeek.com/194041/how-to-open-the-command-prompt-as-administrator-in-windows-8.1/',
                '\n[3] <=> https://www.top-password.com/blog/5-ways-to-run-powershell-as-administrator-in-windows-10/\n\n'
            ]


def handle_unknown_error(err: str):
    error_msg = click.confirm('Would You Like To See The Error Message?')

    if error_msg:
        print(err + '\n')
        with Halo('Troubleshooting ', text_color='yellow'):
            results = search(query=err, stop=3)
            results = [f'\n\t[{index + 1}] <=> {r}' for index, r in enumerate(results)]

            results = ''.join(results)

            if '.google-cookie' in os.listdir('.'):
                os.remove('.google-cookie')

        print(f'These automatically generated links may help:{results}')


    proc = Popen('tasklist', stdin=PIPE, stdout=PIPE, stderr=PIPE)
    output, err = proc.communicate()
    output = output.decode('utf-8')
    lines = output.splitlines()

    cleaned_up_names = []
    for line in lines:
        try:
            cleaned_up_names.append(line.split()[0].strip('.exe'))
        except IndexError:
            continue

    count = 0
    for name in cleaned_up_names:
        if name == 'powershell' or name == 'cmd':
            count += 1

    return count >= 2


def display_info(json: dict) -> str:
    return f'''
| Name => {json['package-name']}
| Version => Coming Soon!
| Url(Windows) => {json['win64']}
    '''


def install_dependent_packages(packet: Packet, rate_limit: int, install_directory: str, metadata: Metadata):
    write(f'Installing Dependencies For => {packet.display_name}', 'cyan', metadata)
    disp = str(packet.dependencies).replace("[", "").replace("]", "").replace("\'", "")
    write(f'{packet.display_name} has the following dependencies: {disp}', 'yellow', metadata)
    continue_install = click.confirm('Would you like to install the above dependencies ?')
    if continue_install:
        res, _ = handle_cached_request()
        if len(packet.dependencies) > 1 and len(packet.dependencies) <= 5:
            write(f'Using Parallel Installation For Installing Dependencies', 'green', metadata)

            packets = []
            for package in packet.dependencies:

                pkg = res[package]
                custom_dir = None
                if install_directory:
                    custom_dir = install_directory + f'\\{pkg["package-name"]}'
                else:
                    custom_dir = install_directory

                packet = Packet(package, pkg['package-name'], pkg['win64'], pkg['win64-type'], pkg['custom-location'], pkg['install-switches'], pkg['uninstall-switches'], custom_dir, pkg['dependencies'])
                installation = find_existing_installation(
                    package, packet.json_name)
                if installation:
                    write_debug(
                        f'Aborting Installation As {packet.json_name} is already installed.', metadata)
                    write_verbose(
                        f'Found an existing installation of => {packet.json_name}', metadata)
                    write(
                        f'Found an existing installation {packet.json_name}.', 'bright_yellow', metadata)
                    installation_continue = click.confirm(
                        f'Would you like to reinstall {packet.json_name}')
                    if installation_continue or metadata.yes:
                        os.system(f'electric uninstall {packet.json_name}')
                        os.system(f'electric install {packet.json_name}')
                        return
                    else:
                        handle_exit('ERROR', None, metadata)

                write_verbose(
                    f'Package to be installed: {packet.json_name}', metadata)
                log_info(
                    f'Package to be installed: {packet.json_name}', metadata.logfile)

                write_verbose(
                    f'Finding closest match to {packet.json_name}...', metadata)
                log_info(
                    f'Finding closest match to {packet.json_name}...', metadata.logfile)
                packets.append(packet)

                write_verbose('Generating system download path...', metadata)
                log_info('Generating system download path...', metadata.logfile)

            manager = mgr.PackageManager(packets, metadata)
            paths = manager.handle_multi_download()
            log_info('Finished Rapid Download...', metadata.logfile)
            log_info(
                'Using Rapid Install To Complete Setup, Accept Prompts Asking For Admin Permission...', metadata.logfile)
            manager.handle_multi_install(paths)
            return
        else:
            write('Starting Sync Installation...', 'green', metadata)
            for package in packet.dependencies:
                pkg = res[package]
                log_info('Generating Packet For Further Installation.', metadata.logfile)
                packet = Packet(package, pkg['package-name'], pkg['win64'], pkg['win64-type'], pkg['custom-location'], pkg['install-switches'], pkg['uninstall-switches'], install_directory, pkg['dependencies'])
                log_info('Searching for existing installation of package.', metadata.logfile)
                installation = find_existing_installation(package, packet.json_name)

                if installation:
                    write_debug(
                        f'Found existing installation of {packet.json_name}.', metadata)
                    write_verbose(
                        f'Found an existing installation of => {packet.json_name}', metadata)
                    write(
                        f'Found an existing installation {packet.json_name}.', 'bright_yellow', metadata)
                    continue

                if packet.dependencies:
                    install_dependent_packages(packet, rate_limit, install_directory, metadata)

                write_verbose(
                    f'Package to be installed: {packet.json_name}', metadata)
                log_info(f'Package to be installed: {packet.json_name}', metadata.logfile)

                write_verbose('Generating system download path...', metadata)
                log_info('Generating system download path...', metadata.logfile)

                start = timer()
                download_url = get_download_url(packet)
                end = timer()

                val = round(Decimal(end) - Decimal(start), 6)
                write(
                    f'Electrons Transferred In {val}s', 'cyan', metadata)
                log_info(f'Electrons Transferred In {val}s', metadata.logfile)
                write_debug(f'Successfully Parsed Download Path in {val}s', metadata)

                write('Initializing Rapid Download...', 'green', metadata)
                log_info('Initializing Rapid Download...', metadata.logfile)

                # Downloading The File From Source
                write_debug(f'Downloading {packet.display_name} from => {packet.win64}', metadata)
                write_verbose(
                    f"Downloading from '{download_url}'", metadata)
                log_info(f"Downloading from '{download_url}'", metadata.logfile)

                if rate_limit == -1:
                    path, _ = download(download_url, packet.json_name, metadata, packet.win64_type)
                else:
                    log_info(f'Starting rate-limited installation => {rate_limit}', metadata.logfile)
                    bucket = TokenBucket(tokens=10 * rate_limit, fill_rate=rate_limit)

                    limiter = Limiter(
                        bucket=bucket,
                        filename=f'{tempfile.gettempdir()}\Setup{packet.win64_type}',
                    )

                    urlretrieve(
                        url=download_url,
                        filename=f'{tempfile.gettempdir()}\Setup{packet.win64_type}',
                        reporthook=limiter
                    )

                    path = f'{tempfile.gettempdir()}\Setup{packet.win64_type}'

                write('Completed Rapid Download', 'green', metadata)

                log_info('Finished Rapid Download', metadata.logfile)

                if metadata.virus_check:
                    write('Scanning File For Viruses...', 'blue', metadata)
                    check_virus(path, metadata)

                write(
                    'Using Rapid Install, Accept Prompts Asking For Admin Permission...', 'cyan', metadata)
                log_info(
                    'Using Rapid Install To Complete Setup, Accept Prompts Asking For Admin Permission...', metadata.logfile)

                write_debug(
                    f'Installing {packet.json_name} through Setup{packet.win64_type}', metadata)
                log_info(
                    f'Installing {packet.json_name} through Setup{packet.win64_type}', metadata.logfile)
                start_snap = get_environment_keys()

                # Running The Installer silently And Completing Setup
                install_package(path, packet, metadata)

                final_snap = get_environment_keys()
                if final_snap.env_length > start_snap.env_length or final_snap.sys_length > start_snap.sys_length:
                    write('Refreshing Environment Variables...', 'green', metadata)
                    start = timer()
                    log_info('Refreshing Environment Variables At scripts/refreshvars.cmd', metadata.logfile)
                    write_debug('Refreshing Env Variables, Calling Batch Script At scripts/refreshvars.cmd', metadata)
                    write_verbose('Refreshing Environment Variables', metadata)
                    refresh_environment_variables()
                    end = timer()
                    write_debug(f'Successfully Refreshed Environment Variables in {round(end - start)} seconds', metadata)

                write(
                    f'Successfully Installed {packet.display_name}!', 'bright_magenta', metadata)
                log_info(f'Successfully Installed {packet.display_name}!', metadata.logfile)


                if metadata.reduce_package:

                    os.remove(path)
                    try:
                        os.remove(Rf'{tempfile.gettempdir()}\downloadcache.pickle')
                    except:
                        pass

                    log_info('Successfully Cleaned Up Installer From Temporary Directory And DownloadCache', metadata.logfile)
                    write('Successfully Cleaned Up Installer From Temp Directory...',
                        'green', metadata)

                write_verbose('Dependency successfully Installed.', metadata)
                log_info('Dependency successfully Installed.', metadata.logfile)
    else:
        os._exit(1)


def get_autocorrections(package_names: list, corrected_package_names: list, metadata: Metadata) -> list:
    corrected_names = []

    for name in package_names:
        if name in corrected_package_names:
            corrected_names.append(name)
        else:
            corrections = difflib.get_close_matches(name, corrected_package_names)
            if corrections:
                if metadata.silent:
                    click.echo(click.style(
                        'Incorrect / Invalid Package Name Entered. Aborting Installation.', fg='red'))
                    log_info(
                        'Incorrect / Invalid Package Name Entered. Aborting Installation', metadata.logfile)

                    handle_exit('ERROR', None, metadata)

                if metadata.yes:
                    write_all(f'Autocorrecting To {corrections[0]}', 'bright_magenta', metadata)
                    write(
                        f'Successfully Autocorrected To {corrections[0]}', 'green', metadata)
                    log_info(
                        f'Successfully Autocorrected To {corrections[0]}', metadata.logfile)
                    corrected_names.append(corrections[0])

                else:
                    write_all(f'Autocorrecting To {corrections[0]}', 'bright_magenta', metadata)

                    if click.confirm('Would You Like To Continue?'):
                        package_name = corrections[0]
                        corrected_names.append(package_name)
                    else:
                        handle_exit('ERROR', None, metadata)
            else:
                write_all(f'Could Not Find Any Packages Which Match {name}', 'bright_magenta', metadata)
    return corrected_names

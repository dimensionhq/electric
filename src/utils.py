######################################################################
#                           HELPERS / UTILS                          #
######################################################################


from constants import valid_install_exit_codes, valid_uninstall_exit_codes
from subprocess import Popen, PIPE, CalledProcessError, check_call
from Classes.PathManager import PathManager
from timeit import default_timer as timer
from Classes.Metadata import Metadata
from Classes.Packet import Packet
from viruscheck import virus_check
from datetime import datetime
import pyperclip as clipboard
from signal import SIGTERM
from colorama import Back, Fore
from switch import Switch
from extension import *
import webbrowser
import subprocess
import keyboard
import requests
import tempfile
import registry
import difflib
import zipfile
import hashlib
import ctypes
import random
import pickle
import click
import json
import sys
import os
import re


index = 0
final_value = None
path = ''

manager = PathManager()
parent_dir = manager.get_parent_directory()
current_dir = manager.get_current_directory()

def is_admin():
    try:
        is_admin = (os.getuid() == 0)
    except AttributeError:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
    return is_admin

class HiddenPrints:
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout


def get_download_url(packet):
    return packet.win64


def generate_dict(path: str, package_name: str):
    return {
        'directory': path,
        'package_name': package_name,
        'size': os.stat(path).st_size,
    }


def dump_pickle(data: dict):
    with open(Rf'{tempfile.gettempdir()}\downloadcache.pickle', 'wb') as f:
        pickle.dump(data, f)


def retrieve_data():
    if os.path.isfile(Rf'{tempfile.gettempdir()}\downloadcache.pickle'):
        with open(Rf'{tempfile.gettempdir()}\downloadcache.pickle', 'rb') as f:
            final = pickle.loads(f.read())
            return final


def check_existing_download(package_name: str, download_type) -> bool:
    data = retrieve_data()
    if data:
        if data['package_name'] == package_name:
            if os.stat(data['directory'] + download_type).st_size < data['size']:
                # Corrupt Installation
                return False
            return data['directory']
    return False 


def download(url, package_name, metadata: Metadata, download_type):

        path = check_existing_download(package_name, download_type)

        if isinstance(path, bool):
            path = f'{tempfile.gettempdir()}\\Setup{download_type}'
        else:
            write(f'Found Existing Download At => {tempfile.gettempdir()}', 'blue', metadata)
            return path, True

        while os.path.isfile(path):
            path = f'{tempfile.gettempdir()}\\Setup{random.randint(200, 10000)}'

        

        with open(path, "wb") as f:
            response = requests.get(url, stream=True)
            total_length = response.headers.get('content-length')

            if total_length is None:
                f.write(response.content)
            else:
                dl = 0
                full_length = int(total_length)

                for data in response.iter_content(chunk_size=7096):
                    dl += len(data)
                    f.write(data)

                    if metadata.no_progress:
                        sys.stdout.write(
                            f"\r{round(dl / 1000000, 2)} / {round(full_length / 1000000, 2)} MB")
                        sys.stdout.flush()

                    elif not metadata.no_progress and not metadata.silent:
                        complete = int(20 * dl / full_length)
                        fill_c, unfill_c = '#' * complete, ' ' * (20 - complete)
                        sys.stdout.write(
                            f"\r[{fill_c}{unfill_c}] ⚡ {round(dl / full_length * 100, 1)} % ⚡ {round(dl / 1000000, 1)} / {round(full_length / 1000000, 1)} MB")
                        sys.stdout.flush()
        
        dump_pickle(generate_dict(path, package_name))

        return path, False


def get_error_cause(error: str, method: str) -> str:

    if method == 'installation':
        for code in valid_install_exit_codes:
            if f'exit status {code}' in error:
                return ['no-error']
    
    if method == 'uninstallation':
        for code in valid_uninstall_exit_codes:
            if f'exit status {code}' in error:
                return ['no-error']

    if '[WinError 740]' in error and 'elevation' in error:
        # Process Needs Elevation To Execute
        click.echo(click.style(f'\nAdministrator Elevation Requied. Exit Code [0001]', fg='red'))
        return get_error_message('0001', 'installation')
    
    if 'exit status 2' in error or 'exit status 1' in error:
        # User Declined Prompt Asking For Permission
        click.echo(click.style(f'\nAdministrative Privileges Declined. Exit Code [0101]', fg='red'))
        return get_error_message('0101', 'installation')
    
    if 'exit status 4' in error:
        # Fatal Error During Installation
        click.echo(click.style(f'\nFatal Error. Exit Code [1111]', fg='red'))
        return get_error_message('1111', 'installation')
    
    if '[WinError 87]' in error and 'incorrect' in error:
        click.echo(click.style(f'\nElectric Installer Passed In Invalid Parameters For Installation. Exit Code [0002]', fg='red'))
        return get_error_message('0002', 'installation')

    if 'exit status 3010' or 'exit status 2359301' in error:
        # Installer Requesting Reboot
        return get_error_message('1010', 'installation')
    
    else:
        click.echo(click.style(f'\nUnknown Error. Exited With Code [0000]', fg='red'))
        handle_unknown_error(error)
        return get_error_message('0000', 'installation')


def run_cmd(command: str,  metadata: Metadata, method: str):
    command = command.replace('\"\"', '\"')
    try:
        check_call(command, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    except (CalledProcessError, OSError, FileNotFoundError) as err:
        keyboard.add_hotkey(
        'ctrl+c', lambda: os._exit(0))
        disp_error_msg(get_error_cause(str(err), method), metadata)


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
                    command += ' ' + custom_install_switch + f'{directory}'
                else:
                    command += ' ' + custom_install_switch + \
                        f'"{directory}"'
                if directory == '':
                    click.echo(click.style(
                        f'Installing {package_name} To Default Location, Custom Installation Directory Not Supported By This Installer!', fg='yellow'))

        for switch in switches:
            command = command + ' ' + switch

        run_cmd(command, metadata, 'installation')

    elif download_type == '.msi':
        command = 'msiexec.exe /i ' + path + ' '
        for switch in switches:
            command = command + ' ' + switch

        if not is_admin():
            click.echo(click.style(
                '\nAdministrator Elevation Required. Exit Code [0001]', fg='red'))
            disp_error_msg(get_error_message('0001', 'installation'))
            handle_exit('ERROR', None, metadata)
        run_cmd(command, metadata, 'installation')

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
                path = file_path + "\\" + executable_list[index]
                click.echo(click.style(
                    f'Running {executable_list[index]}. Hit Control + C to Quit', fg='magenta'))
                subprocess.call(path, stdout=PIPE, stdin=PIPE, stderr=PIPE)
                quit()

        keyboard.add_hotkey('up', up)
        keyboard.add_hotkey('down', down)
        keyboard.add_hotkey('enter', enter)
        keyboard.wait()


def get_correct_package_names(res: str) -> list:
    package_names = []
    for package in res:
        package_names.append(package)
    return package_names


def get_hash_algorithm(checksum: str):
    # A function to detect the hash algorithm used in checksum
    hashes = {32: "md5", 40: "sha1", 64: "sha256", 128: "sha512"}
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
    res = json.loads(response.text.strip())
    time = response.elapsed.total_seconds()
    return res, time


def get_pid(exe_name):
    proc = subprocess.Popen('tasklist', stdin=PIPE, stdout=PIPE, stderr=PIPE)
    output, _ = proc.communicate()
    output = output.decode('utf-8')
    lines = output.splitlines()
    for line in lines:
        if exe_name in line:
            return line.split()[1]


def find_approx_pid(exe_name) -> str:
    proc = subprocess.Popen('tasklist', stdin=PIPE, stdout=PIPE, stderr=PIPE)
    output, err = proc.communicate()
    output = output.decode('utf-8')
    lines = output.splitlines()

    cleaned_up_names = []
    for line in lines:
        try:
            cleaned_up_names.append(line.split()[0].strip('.exe'))
        except IndexError:
            continue

    matches = difflib.get_close_matches(exe_name, cleaned_up_names)

    if matches != []:
        for line in lines:
            if matches[0] in line:
                return line.split()[1]

    return 1


def handle_exit(status: str, setup_name: str, metadata: Metadata):

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

    else:
        write('\nRapidExit Successfully Exited With Code 0', 'green', metadata)
        os._exit(0)


def kill_running_proc(package_name: str, metadata: Metadata):
    parts = package_name.split('-')
    name = ' '.join([p.capitalize() for p in parts])
    pid = int(find_approx_pid(package_name))
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
        terminate = click.prompt(
            f'Electric Detected {name} Running In The Background. Would You Like To Terminate It? [y/n]')
        if terminate == 'y':
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
    key = registry.get_uninstall_key(package_name)

    if key:
        return True
    else:
        key = registry.get_uninstall_key(display_name.lower())

        if key:
            return True

        else:
            key = registry.get_uninstall_key(display_name)

    if key:
        return True

    return False


def refresh_environment_variables() -> bool:
    proc = Popen(Rf'{current_dir}\scripts\refreshvars.cmd',
                 stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
    output, err = proc.communicate()
    if 'Finished' in output.decode('utf-8'):
        return True
    else:
        print('An error occurred')
        print(err.decode('utf-8'))


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
            continue_install = click.prompt('Would You Like To Continue? [y/n]')
        if continue_install == 'y':
            pass
        else:
            handle_exit('Virus Check', '', metadata)
    else:
        click.echo(click.style('No Viruses Detected!', fg='green'))


def setup_supercache():
    res, time = send_req_all()
    res = json.loads(res)
    with open(Rf'{parent_dir}supercache.json', 'w+') as file:
        del res['_id']
        file.write(json.dumps(res, indent=4))

    return res, time


def update_supercache(res):
    filepath = Rf'{parent_dir}supercache.json'
    file = open(filepath, 'w+')
    file.write(json.dumps(res, indent=4))
    file.close()
    logpath = Rf'{parent_dir}\superlog.txt'
    logfile = open(logpath, 'w+')
    now = datetime.now()
    logfile.write(str(now))
    logfile.close()


def check_supercache_valid():
    filepath = Rf'{parent_dir}superlog.txt'
    if os.path.isfile(filepath):
        with open(filepath, 'r') as f:
            contents = f.read()
        date = datetime.strptime(contents, '%Y-%m-%d %H:%M:%S.%f')
        if (datetime.now() - date).days < 1:
            return True
    return False


def handle_cached_request():
    filepath = Rf'{parent_dir}supercache.json'
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


def generate_metadata(no_progress, silent, verbose, debug, no_color, yes, logfile, virus_check, reduce):
    return Metadata(no_progress, no_color, yes, silent, verbose, debug, logfile, virus_check, reduce)


def disp_error_msg(messages: list, metadata: Metadata):
    if 'no-error' in messages:
        return

    reboot = False
    websites = []
    commands = []
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
        else:
            click.echo(msg)
        
        idx += 1

    if reboot:
        reboot = click.confirm('Would you like to reboot? [y/n]')
        if reboot:
            os.system('shutdown /R')

    if commands:
        run = click.prompt('Would You Like To Install Node? [y/n]')
        if run == 'y':
            print('\n')
            os.system(commands[0][0])

    if websites:
        website = click.prompt('Would You Like To Visit Any Of The Above Websites? [y/n]')
        if website == 'y':
            try:
                webpage = int(click.prompt('Which Webpage Would You Like To Visit? ')) - 1
            except:
                handle_exit('ERROR', None, metadata)
            try:
                webbrowser.open(websites[webpage][8:])
            except:
                pass
    handle_exit('ERROR', None, metadata)


def get_error_message(code: str, method: str):
    attr = method.replace('ation', '')
    with Switch(code) as code:
        if code('0001'):
            return [
                f'\n[0001] => {method.capitalize()} failed because the software you tried to {attr} requires administrator permissions.',
                f'\n\nHow To Fix:\n\nRun Your Command Prompt Or Powershell As Administrator And Retry {method.capitalize()}.\n\nHelp:',
                '\n[1] <=> https://www.howtogeek.com/194041/how-to-open-the-command-prompt-as-administrator-in-windows-8.1/',
                '\n[2] <=> https://www.top-password.com/blog/5-ways-to-run-powershell-as-administrator-in-windows-10/\n\n']

        if code('0002'):
            return [
                f'\n[0002] => {method.capitalize()} failed because the installer provided an incorrect command for {attr}.', 
                '\nFile a support ticket at https://www.electric.sh/support', 
                '\n\nHelp:\n', 
                'https://www.electric.sh/troubleshoot'
                ]

        if code('0000'):
            return [
                f'\n[0000] => {method.capitalize()} failed due to an unknown reason.',
                '\nFile a support ticket at https://www.electric.com/support',
                '\n\nHelp:',
                '\nhttps://www.electric.sh/troubleshoot'
                ]

        if code('0011'):
            clipboard.copy('electric install node')
            return [
                '\n[0011] => Node(npm) is not installed on your system.', 
                '\n\nHow To Fix:\n', 
                'Run `electric install node` [ Copied To Clipboard ] To Install Node(npm)'
                ]

        if code('0010'):
            clipboard.copy('electric install python3')
            return [
                '\n[0010] => Python(pip) is not installed on your system.',
                '\n\nHow To Fix:\n',
                'Run `electric install python3` [ Copied To Clipboard ] To install Python(pip).\n\nHelp:',
                '\n[1] <=> https://www.educative.io/edpresso/how-to-add-python-to-path-variable-in-windows',
                '\n[2] <=> https://stackoverflow.com/questions/23708898/pip-is-not-recognized-as-an-internal-or-external-command'
                ]
        
        if code('1010'):
            return [
                f'\n[1010] => Installer Has Requested A Reboot In Order To Complete {method.capitalize()}.\n'
            ]
        
        if code('1111'):
            return [
                f'\n[1111] => The {attr.capitalize()}er For This Package Failed Due To A Fatal Error. This is likely not an issue or error with electric.', 
                '\n\nWe recommend you raise a support ticket with the data generated below:',
                generate_report(),
                '\n\nHelp:\n',
                '\n[1] <=> https://www.electric.sh/errors/1111',
                '\n[2] <=> https://www.electric.sh/support',
            ]
        
        if code('0101'):
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
    error_msg = click.prompt('Would You Like To See The Error Message? [y/n]')
    if error_msg == 'y':
        print(err)


    proc = subprocess.Popen('tasklist', stdin=PIPE, stdout=PIPE, stderr=PIPE)
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

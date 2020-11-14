from subprocess import Popen, PIPE, STDOUT, CalledProcessError
from timeit import default_timer as timer
from Classes.Metadata import Metadata
from Classes.Packet import Packet
from viruscheck import virus_check
from datetime import datetime
from switch import Switch
from signal import SIGTERM
from extension import *
import subprocess
import keyboard
import platform
import requests
import tempfile
import registry
import difflib
import zipfile
import hashlib
import ctypes
import click
import time
import json
import sys
import os


index = 0
final_value = None
path = ''


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


def get_architecture():
    if platform.machine().endswith('64'):
        return 'x64'
    if platform.machine().endswith('86'):
        return 'x32'


def get_download_url(packet):
    if sys.platform == 'win32':
        return packet.win64

    elif sys.platform == 'darwin':
        return pkg['darwin']

    elif sys.platform == 'linux':
        return pkg['debian']


def download(url, noprogress, silent, download_type):
    path = f'{tempfile.gettempdir()}\\Setup{download_type}'
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

                if noprogress:
                    sys.stdout.write(
                        f"\r{round(dl / 1000000, 2)} / {round(full_length / 1000000, 2)} MB")
                    sys.stdout.flush()

                if silent:
                    pass

                elif not noprogress and not silent:
                    complete = int(20 * dl / full_length)
                    fill_c, unfill_c = '#' * complete, ' ' * (20 - complete)
                    sys.stdout.write(
                        f"\r[{fill_c}{unfill_c}] ⚡ {round(dl / full_length * 100, 1)} % ⚡ {round(dl / 1000000, 1)} / {round(full_length / 1000000, 1)} MB")
                    sys.stdout.flush()
    return path


def install_package(path, package_name, switches, download_type, no_color, directory, custom_install_switch) -> str:
    if sys.platform == 'win32':
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

            try:
                subprocess.call(command, stdin=PIPE, stdout=PIPE, stderr=PIPE)
            except (OSError, FileNotFoundError) as err:
                try:
                    proc = Popen(command.split(), stdout=PIPE,
                                 stdin=PIPE, stderr=PIPE)
                except (OSError, FileNotFoundError) as err:
                    if '[WinError 740]' in str(err) and 'elevation' in str(err):
                        if not is_admin():
                            click.echo(click.style(
                                'Administrator Elevation Required. Exit Code [0001]', fg='bright_yellow'))
                            print(get_error_message('0001', 'installation'))
                            os._exit(0)

                    if 'FileNotFoundError' in str(err) or 'WinError 2' in str(err):

                        click.echo(click.style(
                            'Installation Failed!', fg='red'))
                        print(get_error_message('0002', 'installation'))
                        os._exit(0)

                    else:
                        print(get_error_message('0000', 'installation'))
                        handle_unknown_error(str(err))
                        os._exit(0)

                if '[WinError 740]' in str(err) and 'elevation' in str(err):
                    if not is_admin():
                        click.echo(click.style(
                            'Administrator Elevation Required. Exit Code [0001]', fg='bright_yellow'))
                        print(get_error_message('0001', 'installation'))
                        os._exit(0)

                if 'FileNotFoundError' in str(err) or 'WinError 2' in str(err):

                    click.echo(click.style('Installation Failed!', fg='red'))
                    print(get_error_message('0002', 'installation'))
                    os._exit(0)

                else:
                    print(get_error_message('0000', 'installation'))
                    handle_unknown_error(str(err))
                    os._exit(0)

        elif download_type == '.msi':
            command = 'msiexec.exe /i ' + path + ' '
            for switch in switches:
                command = command + ' ' + switch
            try:
                proc = Popen(command, stdin=PIPE, stdout=PIPE, stderr=PIPE)
            except (OSError, FileNotFoundError) as err:
                try:
                    proc = Popen(command.split(), stdout=PIPE,
                                 stdin=PIPE, stderr=PIPE, shell=True)
                except (OSError, FileNotFoundError) as err:
                    if '[WinError 740]' in str(err) and 'elevation' in str(err):
                        if not is_admin():
                            click.echo(click.style(
                                'Administrator Elevation Required. Exit Code [0001]', fg='bright_yellow'))
                            print(get_error_message('0001', 'installation'))
                            os._exit(0)

                    if 'FileNotFoundError' in str(err) or 'WinError 2' in str(err):

                        click.echo(click.style(
                            'Installation Failed!', fg='red'))
                        print(get_error_message('0002', 'installation'))
                        os._exit(0)

                    else:
                        print(get_error_message('0000', 'installation'))
                        handle_unknown_error(str(err))
                        os._exit(0)

                if '[WinError 740]' in str(err) and 'elevation' in str(err):
                    if not is_admin():
                        click.echo(click.style(
                            'Administrator Elevation Required. Exit Code [0001]', fg='bright_yellow'))
                        print(get_error_message('0001', 'installation'))
                        os._exit(0)

                if 'FileNotFoundError' in str(err) or 'WinError 2' in str(err):

                    click.echo(click.style('Installation Failed!', fg='red'))
                    print(get_error_message('0002', 'installation'))
                    os._exit(0)

                else:
                    print(get_error_message('0000', 'installation'))
                    handle_unknown_error(str(err))
                    os._exit(0)

        elif download_type == '.zip':
            if not no_color:
                click.echo(click.style(
                    f'Unzipping File At {path}', fg='green'))
            if no_color:
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
                    return

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

    # TODO: Implement the macOS side.
    if sys.platform == 'darwin':
        mount_dmg = f'hdiutil attach -nobrowse {file_name}'


def uninstall_package(command: str, packet: Packet, metadata: Metadata) -> str:
    try:
        subprocess.check_output(
            command, stderr=PIPE, stdin=PIPE)

    except (CalledProcessError, OSError, FileNotFoundError) as err:
        try:
            output = subprocess.check_output(
                command, stderr=PIPE, stdin=PIPE, shell=True)
        except (CalledProcessError, OSError, FileNotFoundError) as err:
            if '[WinError 740]' in str(err) and 'elevation' in str(err):
                if not is_admin():
                    write(
                        f'Installation Failed With Code [0001]', 'red', metadata)
                    print(get_error_message('0001', 'uninstallation'))
                    handle_exit('ERROR', 'None', metadata)
            else:
                if not is_admin():
                    write(
                        f'Installation Failed With Code [0001]', 'red', metadata)
                    print(get_error_message('0001', 'uninstallation'))
                    handle_exit('ERROR', 'None', metadata)
                else:
                    write(
                        'Installation Failed Due To An Unknown Error [0000]', 'red', metadata)
                    handle_unknown_error(str(err))
                    print(get_error_message('0000', 'uninstallation'))
                    os._exit(0)


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
    REQA = 'https://electric-package-manager.herokuapp.com/packages/'
    time = 0.0
    response = requests.get(REQA, timeout=15)
    res = json.loads(response.text.strip())
    time = response.elapsed.total_seconds()
    return res, time


def get_pid(exe_name):
    proc = subprocess.Popen('tasklist', stdin=PIPE, stdout=PIPE, stderr=PIPE)
    output, err = proc.communicate()
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
    split_package_name = exe_name.split('-')

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
    with HiddenPrints():
        time.sleep(1)

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


def kill_running_proc(package_name: str, quiet: bool, verbose: bool, debug: bool, yes: bool, no_color: bool):
    parts = package_name.split('-')
    name = ' '.join([p.capitalize() for p in parts])
    pid = int(find_approx_pid(package_name))
    if pid == 1:
        return
    if pid and pid != 1:
        if yes:
            write(f'Terminating {name}.', 'green', no_color, quiet)
            os.kill(pid, SIGTERM)
            return
        if quiet:
            os.kill(pid, SIGTERM)
            return
        terminate = click.prompt(
            f'Electric Detected {name} Running In The Background. Would You Like To Terminate It? [y/n]')
        if terminate == 'y':
            write(f'Terminating {name}.', 'green', no_color, quiet)
            os.kill(pid, SIGTERM)
        else:
            write('Aborting Installation!', 'red', no_color, quiet)
            write_verbose(
                f'Aborting Installation Due To {name} Running In Background', verbose, no_color, quiet)
            write_debug(
                f'Aborting Installation Due To {name} Running In Background. Process Was Not Terminated.', debug, no_color, quiet)
            os._exit(1)


def kill_proc(proc, no_color, silent):
    if proc is not None:
        proc.terminate()
        write('SafetyHarness Successfully Created Clean Exit Gateway',
              'green', no_color, silent)
        write('\nRapidExit Using Gateway From SafetyHarness Successfully Exited With Code 0',
              'light_blue', no_color, silent)
        os._exit(0)
    else:
        write('\nRapidExit Successfully Exited With Code 0',
              'green', no_color, silent)
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
    proc = Popen(R'C:\Users\tejas\Desktop\electric\src\scripts\refreshvars.cmd',
                 stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
    output, err = proc.communicate()
    if 'Finished' in output.decode('utf-8'):
        return True
    else:
        print('An error occurred')
        print(err.decode('utf-8'))


def check_virus(path: str, no_color: bool, silent: bool):
    detected = virus_check(path)
    if detected:
        for value in detected.items():
            click.echo(click.style(f'{value[0]} => {value[1]}', fg='yellow'))
        continue_install = click.prompt('Would You Like To Continue? [y/n]')
        if continue_install == 'y':
            pass
        else:
            handle_exit('Virus Check', '', no_color, silent)
    else:
        click.echo(click.style('No Viruses Detected!', fg='green'))


def setup_supercache():
    res, time = send_req_all()
    res = json.loads(res)
    with open('C:\\Users\\tejas\\Desktop\\electric\\supercache.json', 'w+') as file:
        del res['_id']
        file.write(json.dumps(res, indent=4))

    return res, time


def update_supercache(res):
    filepath = f'C:\\Users\\tejas\\Desktop\\electric\\supercache.json'
    file = open(filepath, 'w+')
    file.write(json.dumps(res, indent=4))
    file.close()
    logpath = f'C:\\Users\\tejas\\Desktop\\electric\\superlog.txt'
    logfile = open(logpath, 'w+')
    now = datetime.now()
    logfile.write(str(now))
    logfile.close()


def check_supercache_valid():
    filepath = R'C:\\Users\tejas\Desktop\electric\superlog.txt'
    if os.path.isfile(filepath):
        with open(filepath, 'r') as f:
            contents = f.read()
        date = datetime.strptime(contents, '%Y-%m-%d %H:%M:%S.%f')
        if (datetime.now() - date).days < 1:
            return True
    return False


def handle_cached_request():
    filepath = R'C:\\Users\tejas\Desktop\electric\supercache.json'
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


def get_error_message(code: str, method: str):
    attr = method.replace('ation', '')
    with Switch(code) as code:
        if code('0001'):
            return f'\n[0001] => {method.capitalize()} failed because the software you tried to {attr} requires administrator permissions.\n\nHow To Fix:\nRun Your Command Prompt Or Powershell As Administrator And Retry {method.capitalize()}.'
        if code('0002'):
            return f'\n[0002] => {method.capitalize()} failed because the installer provided an incorrect command for {attr}.\nFile a support ticket at https://www.electric.com/support'
        if code('0000'):
            return f'\n[0000] => {method.capitalize()} failed due to an unknown reason, to get support, file a support ticket at https://www.electric.com/support'


def handle_unknown_error(err: str):
    error_msg = click.prompt('Would You Like To See The Error Message? [y/n]')
    if error_msg == 'y':
        print(err)

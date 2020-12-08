######################################################################
#                              EXTERNAL                              #
######################################################################


from Classes.Metadata import Metadata
from subprocess import PIPE, Popen
from extension import *
from colorama import *
from utils import *
import mslex
import sys


def handle_python_package(package_name: str, mode: str, metadata: Metadata):
    command = ''

    valid = Popen(mslex.split('pip --version'), stdin=PIPE, stdout=PIPE, stderr=PIPE)
    _, err = valid.communicate()

    if err:
        click.echo(click.style('Python Is Not Installed. Exit Code [0011]', fg='red'))
        disp_error_msg(get_error_message('0011', 'install'))
        handle_exit('ERROR', None, metadata)
    if mode == 'install':
        command = 'python -m pip install --upgrade --no-input'

        command += f' {package_name}'
        
        proc = Popen(mslex.split(command), stdin=PIPE,
                        stdout=PIPE, stderr=PIPE)

        py_version = sys.version.split()
        for line in proc.stdout:
            line = line.decode('utf-8')
            if f'Collecting {package_name}' in line:
                write(f'Python v{py_version[0]} :: Collecting {package_name}', 'green', metadata)
            if 'Downloading' in line and package_name in line:
                write(
                    f'Python v{py_version[0]} :: Downloading {package_name}', 'green', metadata)

            if 'Installing collected packages' in line and package_name in line:
                write(
                    f'Python v{py_version[0]} :: Installing {package_name}', 'green', metadata)

            if f'Requirement already satisfied: {package_name} ' in line and package_name in line:
                write(
                    f'Python v{py_version[0]} :: {package_name} Is Already Installed And On The Latest Version ==> {line.split()[-1]}', 'yellow', metadata)

            if 'Successfully installed' in line and package_name in line:
                ver = line.split('-')[1]
                write(
                    f'Python v{py_version[0]} :: Successfully Installed {package_name} {ver}', 'green', metadata)

            if 'You should consider upgrading via' in line:
                wants = click.confirm(
                    'Would you like to upgrade your pip version?')
                if wants:
                    write('Updating Pip Version', 'green', metadata)
                    Popen(mslex.split('python -m pip install --upgrade pip'))

    elif mode == 'uninstall':
        command = 'python -m pip uninstall --no-input --yes'

        command += f' {package_name}'

        proc = Popen(mslex.split(command), stdin=PIPE,
                        stdout=PIPE, stderr=PIPE)

        py_version = sys.version.split()

        for line in proc.stdout:
            line = line.decode('utf-8')
            if 'Uninstalling' in line and package_name in line:
                write(
                    f'Python v{py_version[0]} :: Uninstalling {package_name}', 'green', metadata)

            if 'Successfully uninstalled' in line and package_name in line:
                ver = line.split('-')[1]
                write(
                    f'Python v{py_version[0]} :: Successfully Uninstalled {package_name} {ver}', 'green', metadata)

        _, err = proc.communicate()

        if err:
            err = err.decode('utf-8')
            if f'WARNING: Skipping {package_name}' in err:
                write(
                    f'Python v{py_version[0]} :: Could Not Find Any Installations Of {package_name}', 'yellow', metadata)


def handle_node_package(package_name: str, mode: str, metadata: Metadata):
    version_proc = Popen(mslex.split('npm --version'), stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
    version, err = version_proc.communicate()
    version = version.decode().strip()

    if err:
        click.echo(click.style('npm Or node Is Not Installed. Exit Code [0011]', fg='bright_yellow'))
        disp_error_msg(get_error_message('0011', 'install'))
        handle_exit('ERROR', None, metadata)


    if mode == 'install':
        proc = Popen(mslex.split(f'npm i {package_name} -g'), stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
        write(f'npm v{version} :: Collecting {package_name}', 'green', metadata)
        package_version = None
        for line in proc.stdout:
            line = line.decode()
            
            if 'node install.js' in line:
                write(f'npm v{version} :: Running `node install.js` for {package_name}', 'green', metadata)
            if package_name in line and '@' in line and 'install' in line or ' postinstall' in line:
                package_version = line.split()[1]
                write(f'npm v{version} :: {package_version} Installing To <=> "{line.split()[3]}"', 'green', metadata)

            if 'Success' in line and package_name in line or 'added' in line:
                write(f'npm v{version} :: Successfully Installed {package_version}', 'green', metadata)
            if 'updated' in line:
                if package_version:
                    write(f'npm v{version} :: Sucessfully Updated {package_version}', 'green', metadata)
                else:
                    write(f'npm v{version} :: Sucessfully Updated {package_name}', 'green', metadata)


    else:
        proc = Popen(mslex.split(f'npm uninstall -g {package_name}'), stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
        for line in proc.stdout:
            line = line.decode()
            if 'up to date' in line:
                write(f'npm v{version} :: Could Not Find Any Existing Installations Of {package_name}', 'yellow', metadata)
            if 'removed' in line:
                number = line.split(' ')[1].strip()
                time = line.split(' ')[4].strip()
                write(f'npm v{version} :: Sucessfully Uninstalled {package_name} And {number} Other Dependencies in {time}', 'green', metadata)


def handle_vscode_extension(package_name: str, mode: str, metadata: Metadata):
    try:
        version_proc = Popen(mslex.split('code --version'), stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
    except FileNotFoundError:
        click.echo(click.style('Visual Studio Code Or vscode Is Not Installed. Exit Code [0111]', fg='bright_yellow'))
        disp_error_msg(get_error_message('0111', 'install'))
        handle_exit('ERROR', None, metadata)

    version, err = version_proc.communicate()
    version = version.decode().strip().split('\n')[0]

    if err:
        click.echo(click.style('Visual Studio Code Or vscode Is Not Installed. Exit Code [0111]', fg='bright_yellow'))
        disp_error_msg(get_error_message('0111', 'install'))
        handle_exit('ERROR', None, metadata)

    if mode == 'install':
        command = f'code --install-extension {package_name} --force'
        proc = Popen(mslex.split(command), stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
        for line in proc.stdout:
            line = line.decode()
            
            if 'Installing extensions' in line:
                write(f'Code v{version} :: Installing {Fore.MAGENTA}{package_name}{Fore.RESET}', 'green', metadata)

            if 'is already installed' in line:
                write(f'{Fore.GREEN}Code v{version} :: {Fore.MAGENTA}{package_name}{Fore.YELLOW} is already installed!', 'white', metadata)
            
            if 'was successfully installed' in line:
                write(f'{Fore.GREEN}Code v{version} :: Successfully Installed {Fore.MAGENTA}{package_name}{Fore.RESET}', 'green', metadata)
    if mode == 'uninstall':
        command = f'code --uninstall-extension {package_name} --force'
        proc = Popen(mslex.split(command), stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
        for line in proc.stdout:
            line = line.decode()
            
            if 'Uninstalling' in line:
                write(f'Code v{version} :: Uninstalling {Fore.MAGENTA}{package_name}{Fore.RESET}', 'green', metadata)

            if 'is not installed' in line:
                write(f'{Fore.GREEN}Code v{version} :: {Fore.MAGENTA}{package_name}{Fore.YELLOW} is not installed!', 'white', metadata)
            
            if 'was successfully uninstalled' in line:
                write(f'{Fore.GREEN}Code v{version} :: Successfully Uninstalled {Fore.MAGENTA}{package_name}{Fore.RESET}', 'green', metadata)

from Classes.Metadata import Metadata
from subprocess import Popen, PIPE, run
from sys import platform
from extension import *
import shlex
import sys


def handle_python_package(package_name, mode, flags: list, metadata: Metadata):

    command = ''

    if platform == 'linux':

        if mode == 'install':
            command = f'python -m pip3 install --upgrade --no-input --yes'
            for flag in flags:
                command += f' {flag}'

            command += f' {package_name}'

            proc = Popen(shlex.split(command), stdin=PIPE,
                         stdout=PIPE, stderr=PIPE)
            output, err = proc.communicate()
            # print(output.decode('utf-8'))

        elif mode == 'uninstall':
            command = f'python -m pip3 uninstall --no-input --yes'
            for flag in flags:
                command += f' {flag}'

            command += f' {package_name}'

            proc = Popen(shlex.split(command), stdin=PIPE,
                         stdout=PIPE, stderr=PIPE)
            output, err = proc.communicate()
            # print(output.decode('utf-8'))

    elif platform == 'win32':

        if mode == 'install':

            command = f'python -m pip install --upgrade --no-input'
            for flag in flags:
                command += f' {flag}'

            command += f' {package_name}'

            proc = Popen(shlex.split(command), stdin=PIPE,
                         stdout=PIPE, stderr=PIPE)

            py_version = sys.version.split()
            for line in proc.stdout:
                line = line.decode('utf-8')

                if 'Downloading' in line and package_name in line:
                    write(
                        f'Python v{py_version[0]} :: Downloading {package_name}', 'green', metadata)

                if 'Installing collected packages' in line and package_name in line:
                    write(
                        f'Python v{py_version[0]} :: Installing {package_name}', 'green', metadata)

                if 'Requirement already up-to-date:' in line and package_name in line:
                    write(
                        f'Python v{py_version[0]} :: {package_name} Is Already Installed And On The Latest Version ==> {line.split()[6]}', 'yellow', metadata)

                if 'Successfully installed' in line and package_name in line:
                    ver = line.split('-')[1]
                    write(
                        f'Python v{py_version[0]} :: Successfully Installed {package_name} {ver}', 'green', metadata)

                if 'You should consider upgrading via' in line:
                    wants = click.prompt(
                        'Would you like to upgrade your pip version? [y/n]')
                    if wants:
                        write('Updating Pip Version', 'green', metadata)
                        Popen(shlex.split('python -m pip install --upgrade pip'))

        elif mode == 'uninstall':
            command = f'python -m pip uninstall --no-input --yes'
            for flag in flags:
                command += f' {flag}'

            command += f' {package_name}'

            proc = Popen(shlex.split(command), stdin=PIPE,
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

    elif platform == 'darwin':

        if mode == 'install':
            command = f'python -m pip3 install --upgrade --no-input --yes'
            for flag in flags:
                command += f' {flag}'

            command += f' {package_name}'

            proc = Popen(shlex.split(command), stdin=PIPE,
                         stdout=PIPE, stderr=PIPE)
            output, err = proc.communicate()

        elif mode == 'uninstall':
            command = f'python -m pip3 uninstall --no-input --yes'
            for flag in flags:
                command += f' {flag}'

            command += f' {package_name}'

            proc = Popen(shlex.split(command), stdin=PIPE,
                         stdout=PIPE, stderr=PIPE)


def handle_node_package(package_name, mode):
    proc = run('node --version', stdin=PIPE, stdout=PIPE, stderr=PIPE)

    if 'not recognized' in proc.stdout.decode() or 'not recognized' in proc.stderr.decode():
        return 'not installed'
    
    if mode == 'install':
        run(f'npm i {package_name} -g')

    else:
        run(f'npm uninstall {package_name}')
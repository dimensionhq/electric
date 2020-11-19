######################################################################
#                              EXTERNAL                              #
######################################################################


from Classes.Metadata import Metadata
from subprocess import PIPE, Popen
from extension import *
from utils import *
import shlex
import sys


def handle_python_package(package_name: str, mode: str, metadata: Metadata):
    command = ''
    platform = sys.platform

    if platform == 'linux':

        if mode == 'install':
            command = 'python -m pip3 install --upgrade --no-input --yes'

            command += f' {package_name}'

            proc = Popen(shlex.split(command), stdin=PIPE,
                         stdout=PIPE, stderr=PIPE)
            _, err = proc.communicate()
            # print(output.decode('utf-8'))

        elif mode == 'uninstall':
            command = 'python -m pip3 uninstall --no-input --yes'

            command += f' {package_name}'

            proc = Popen(shlex.split(command), stdin=PIPE,
                         stdout=PIPE, stderr=PIPE)
            _, err = proc.communicate()
            # print(output.decode('utf-8'))

    elif platform == 'win32':
        valid = Popen('pip --version', stdin=PIPE, stdout=PIPE, stderr=PIPE)
        _, err = valid.communicate()
        if err:
            click.echo(click.style('npm Or node Is Not Installed. Exit Code [0011]', fg='red'))
            disp_error_msg(get_error_message('0011', 'install'))
            handle_exit('ERROR', None, metadata)
        if mode == 'install':
            command = 'python -m pip install --upgrade --no-input'

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
            command = 'python -m pip uninstall --no-input --yes'

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
            command = 'python -m pip3 install --upgrade --no-input --yes'

            command += f' {package_name}'

            proc = Popen(shlex.split(command), stdin=PIPE,
                         stdout=PIPE, stderr=PIPE)
            _, err = proc.communicate()

        elif mode == 'uninstall':
            command = 'python -m pip3 uninstall --no-input --yes'


            command += f' {package_name}'

            proc = Popen(shlex.split(command), stdin=PIPE,
                         stdout=PIPE, stderr=PIPE)


def handle_node_package(package_name: str, mode: str, metadata: Metadata):
    version_proc = Popen('npm --version'.split(), stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
    version, err = version_proc.communicate()
    version = version.decode().strip()

    if err:
        click.echo(click.style('npm Or node Is Not Installed. Exit Code [0011]', fg='bright_yellow'))
        disp_error_msg(get_error_message('0011', 'install'))
        handle_exit('ERROR', None, metadata)


    if mode == 'install':
        proc = Popen(f'npm i {package_name} -g'.split(), stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
        write(f'npm v{version} :: Collecting {package_name}', 'green', metadata)
        package_version = None
        for line in proc.stdout:
            line = line.decode()
            if package_name in line and '@' in line and 'install' in line or 'postinstall' in line:
                package_version = line.split()[1]
                write(f'npm v{version} :: {package_version} Installing To <=> "{line.split()[3]}"', 'green', metadata)
            if 'Success' in line and package_name in line:
                write(f'npm v{version} :: Successfully Installed {package_version}', 'green', metadata)
            if 'updated' in line:
                if package_version:
                    write(f'npm v{version} :: Sucessfully Updated {package_version}', 'green', metadata)
                else:
                    write(f'npm v{version} :: Sucessfully Updated {package_name}', 'green', metadata)


    else:
        proc = Popen(f'npm uninstall {package_name}'.split(), stdin=PIPE, stdout=PIPE, stderr=PIPE)
        _, err = proc.communicate()

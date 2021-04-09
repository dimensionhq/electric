from utils import confirm, find_existing_installation, copy_to_clipboard, time, is_admin, get_install_flags
from tempfile import gettempdir
from sys import platform
from subprocess import Popen, PIPE
from Classes.PathManager import PathManager
from Classes.Metadata import Metadata
from colorama import Fore
import colorama
import requests
import click
import os
import sys
import json as js

tags = [
    '<pip>',
    '<pip:name>',
    '<pip:name,version>',
    '<python>',
    '<python:name>',
    '<python:name,version>',
    '<npm>',
    '<npm:name>',
    '<npm:name,version>',
    '<node:name>',
    '<node>',
    '<node:name,version',
    '<vscode>',
    '<vscode:name>',
    '<vscode:name,version>',
    '<vscode-insiders>',
    '<vscode-insiders:name>',
    '<vscode-insiders:name,version>',
    '<atom>',
    '<atom:name>',
    '<atom:name,version>',
    '<apm>',
    '<apm:name>',
    '<apm:name,version>',
    '<sublime>',
    '<sublime:name>',
    '<electric>',
    '<electric:name>',
    '<electric:name,version>'
]


class Config:

    def __init__(self, dictionary):
        self.dictionary = dictionary
        self.publisher = dictionary['Info'][0]['Publisher']
        self.description = dictionary['Info'][1]['Description']
        try:
            self.os = dictionary['Info'][2]['OS']
        except IndexError:
            self.os = None
        self.headers = dictionary.keys()

    def check_prerequisites(self):
        dictionary = self.dictionary
        headers = dictionary.keys()

        if 'Info' in headers:

            click.echo(click.style(f'Publisher => {self.publisher}'))
            click.echo(click.style(
                f'Description => {self.description}', fg='bright_yellow'))

            if (
                platform == 'win32'
                and self.os != 'Windows'
                and self.os
                and not confirm(
                    f'WARNING: This Config Has A Target OS Of {self.os}. Would you like to continue?'
                )
            ):
                sys.exit()

        packages = self.dictionary['Packages'] if 'Packages' in self.headers else None

        if 'Pip-Packages' in headers:
            try:
                Popen('pip', stdin=PIPE, stdout=PIPE, stderr=PIPE)
            except FileNotFoundError:
                if all('python' not in package for package in packages):
                    click.echo(click.style(
                        'Pip Not Found, Aborting Config Installation!', fg='red'))
                    sys.exit()

        if 'Node-Packages' in headers:
            try:
                Popen('npm', stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
            except FileNotFoundError:
                if all('nodejs' not in package for package in packages):
                    click.echo(click.style(
                        'Node Not Found, Aborting Config Installation!', fg='red'))
                    sys.exit()

        editor_type = self.dictionary['Editor-Configuration'][0]['Editor'] if 'Editor-Configuration' in self.headers else None
        if editor_type:
            if not find_existing_installation(
                editor_type, 'Visual Studio Code'
            ) and all('vscode' not in package for package in packages):
                click.echo(click.style(
                    'Visual Studio Code Not Found, Aborting Config Installation!', fg='red'))
            else:
                if editor_type == 'Visual Studio Code':
                    try:
                        Popen('code --help', stdin=PIPE,
                              stdout=PIPE, stderr=PIPE, shell=True)
                    except FileNotFoundError:
                        click.echo(click.style(
                            'Visual Studio Code Found But Shell Extension Not Found, Aborting Config Installation!', fg='red'))

        click.echo(click.style('All Tests Passed!', 'bright_green'))

    @staticmethod
    def get_repr_packages(packages: list, version: bool):

        try:
            packages = list(set(packages))
        except:
            pass

        for package in packages:
            if '(empty)' in package:
                packages.remove('(empty)')

        if version:
            return (
                str(packages)
                .replace('\'', '')
                .replace('[', '')
                .replace(']', '')
                .replace(',', '')
                .replace('{', '')
                .replace('}', '\n')
                .replace(':', ' =>')
                .strip()
            )

        else:
            return str(packages).replace('\'', '').replace(
                '[', '').replace(']', '').replace(',', '').strip().replace(' ', '\n')

    @staticmethod
    def check_pypi_name(pypi_package_name):
        """
        Check if a package name exists on pypi.

        It will return True if the package name, or any equivalent variation as defined by PEP 503 normalisation
        rules (https://www.python.org/dev/peps/pep-0503/#normalized-names) is registered in the PyPI registry.

        >>> check_pypi_name('pip')
        True
        >>> check_pypi_name('Pip')
        True

        It will return False if the package name, or any equivalent variation as defined by PEP 503 normalisation
        rules (https://www.python.org/dev/peps/pep-0503/#normalized-names) is not registered in the PyPI registry.
        """
        extension_url = 'https://pypi.org/project'
        res = requests.get(f'{extension_url}/{pypi_package_name}/')
        return res.status_code == 200

    @staticmethod
    def check_vscode_name(extension_name):
        """
        Check if an extension exists on vscode.
        """
        extension_url = 'https://marketplace.visualstudio.com/items?itemName='
        res = requests.get(f'{extension_url}{extension_name}')
        return res.status_code == 200

    @staticmethod
    def check_atom_name(extension_name):
        extension_url = 'https://atom.io/packages/'
        res = requests.get(f'{extension_url}{extension_name}')
        return res.status_code == 200

    @staticmethod
    def check_sublime_name(extension_name):
        extension_url = 'https://packagecontrol.io/packages/'
        res = requests.get(f'{extension_url}{extension_name}')
        return res.status_code == 200

    @staticmethod
    def check_node_name(extension_name):
        extension_url = 'https://www.npmjs.com/package/'
        res = requests.get(f'{extension_url}{extension_name}')
        return res.status_code == 200

    # FUTURE Yarn Support
    @staticmethod
    def check_yarn_name(extension_name):
        extension_url = 'https://yarnpkg.com/package/'
        res = requests.get(f'{extension_url}{extension_name}')
        return res.status_code == 200

    @staticmethod
    def generate_configuration(filepath: str, signed=True):
        import hashlib
        d = {}
        try:
            with open(f'{filepath}', 'r') as f:
                chunks = f.read().split("[")

                for chunk in chunks:
                    chunk = chunk.replace("=>", ":").split('\n')
                    header = chunk[0].replace("[", '').replace(']', '').strip()
                    d[header] = []

                    for line in chunk[1:]:
                        if line and '#' not in line and line not in tags:
                            try:
                                k, v = line.split(":")
                                k, v = k.strip(), v.strip()
                                if v == '':
                                    with open(f'{filepath}', 'r') as f:
                                        lines = f.readlines()
                                    ln_number = 0
                                    idx = 0
                                    for val in lines:
                                        if val.strip() == line.replace(':', '=>').strip():
                                            ln_number = idx
                                        idx += 1
                                    click.echo(click.style(
                                        f'Error On Line {ln_number + 1} At {filepath}', fg='red'))
                                    message = line.replace(':', '')
                                    click.echo(click.style(
                                        f'ValueNotFoundError : No Value Provided For Key :: {colorama.Fore.LIGHTCYAN_EX}{message}', fg='bright_yellow'))
                                    sys.exit()

                            except ValueError:
                                if header in ['Packages', 'Pip-Packages', 'Editor-Extensions', 'Node-Packages']:
                                    k, v = line, "latest"
                                else:
                                    with open(f'{filepath}', 'r') as f:
                                        lines = f.readlines()

                                    ln_number = 0
                                    idx = 0
                                    for val in lines:
                                        if val.strip() == line.replace(':', '=>').strip():
                                            ln_number = idx
                                        idx += 1

                                    click.echo(click.style(
                                        f'Error On Line {ln_number + 1} At {filepath}', fg='red'))
                                    message = line.replace(':', '')
                                    click.echo(click.style(
                                        f'ValueNotFoundError : Expecting A Value Pair With `=>` Operator For Key :: {colorama.Fore.LIGHTCYAN_EX}{message}', fg='bright_yellow'))
                                    sys.exit()

                            d[header].append({k: v.replace('"', '')})

                if 'Packages' in d:
                    with open(f'{filepath}', 'r') as f:

                        lines = f.readlines()

                    for line in lines:
                        if '<electric:name>' in line or '<electric>' in line:
                            idx = lines.index(line)
                            proc = Popen('electric list --installed'.split(),
                                         stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
                            output, _ = proc.communicate()
                            output = output.decode().splitlines()
                            electric_packages = []
                            electric_packages = output

                            lines[idx] = Config.get_repr_packages(
                                electric_packages, False) + '\n'
                            d['Packages'] = lines[idx].split('\n')

                            with open(f'{filepath}', 'w') as f:
                                f.writelines(lines)

                        if '<electric:name,version>' in line:
                            idx = lines.index(line)
                            proc = Popen('electric list --installed --versions'.split(),
                                         stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
                            output, _ = proc.communicate()
                            output = output.decode().splitlines()
                            electric_packages = []
                            electric_packages = [
                                {line.split('@')[0]: line.split('@')[1]} for line in output]
                            lines[idx] = Config.get_repr_packages(
                                electric_packages, True).replace('\n ', '\n') + '\n'
                            d['Packages'] = [line.split(
                                '@')[0] for line in output]

                            with open(f'{filepath}', 'w') as f:
                                f.writelines(lines)

                if 'Editor-Extensions' in d:
                    with open(f'{filepath}', 'r') as f:

                        lines = f.readlines()

                    for line in lines:

                        if '<sublime:name>' in line or '<sublime>' in line:
                            insert_index = lines.index(line)
                            if find_existing_installation('sublime-text-3', 'Sublime Text 3'):
                                location = PathManager.get_appdata_directory().replace('\electric', '') + \
                                    '\Sublime Text 3'
                                if os.path.isdir(location) and os.path.isfile(fr'{location}\Packages\User\Package Control.sublime-settings'):
                                    with open(fr'{location}\Packages\User\Package Control.sublime-settings', 'r') as f:
                                        sublime_lines = f.readlines()
                                        idx = 0
                                        for line in sublime_lines:
                                            if '"Package Control",' in line.strip():
                                                idx = sublime_lines.index(line)

                                        if ']' in sublime_lines[idx + 1].strip():
                                            sublime_lines[idx] = "        \"Package Control\"\n"

                                    with open(fr'{location}\Packages\User\Package Control.sublime-settings', 'w') as f:
                                        f.writelines(sublime_lines)

                                    with open(fr'{location}\Packages\User\Package Control.sublime-settings', 'r') as f:
                                        json = js.load(f)
                                        current_packages = str(json['installed_packages']).replace('[', '').replace(
                                            ']', '').replace('\n ', '\n').replace('\'', '').replace(', ', '\n') + '\n'
                                        lines[insert_index] = current_packages
                                        d['Editor-Extensions'] = lines[insert_index].split(
                                            '\n')

                                    with open(f'{filepath}', 'w') as f:
                                        f.writelines(lines)

                        if '<vscode:name>' in line or '<vscode>' in line:
                            idx = lines.index(line)
                            proc = Popen('code --list-extensions'.split(),
                                         stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
                            output, _ = proc.communicate()
                            output = output.decode().splitlines()
                            vscode_packages = []
                            vscode_packages = output

                            lines[idx] = Config.get_repr_packages(
                                vscode_packages, False) + '\n'
                            d['Editor-Extensions'] = lines[idx].split('\n')

                            with open(f'{filepath}', 'w') as f:
                                f.writelines(lines)

                        if '<vscode:name,version>' in line:
                            idx = lines.index(line)
                            proc = Popen('code --list-extensions --show-versions'.split(),
                                         stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
                            output, _ = proc.communicate()
                            output = output.decode().splitlines()
                            vscode_packages = []
                            vscode_packages = [
                                {line.split('@')[0]: line.split('@')[1]} for line in output]
                            lines[idx] = Config.get_repr_packages(
                                vscode_packages, True).replace('\n ', '\n') + '\n'
                            d['Editor-Extensions'] = [line.split('@')[0]
                                                      for line in output]

                            with open(f'{filepath}', 'w') as f:
                                f.writelines(lines)

                        if '<vscode-insiders:name>' in line or '<vscode-insiders>' in line:
                            idx = lines.index(line)
                            proc = Popen('code-insiders --list-extensions'.split(),
                                         stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
                            output, _ = proc.communicate()
                            output = output.decode().splitlines()
                            vscode_packages = []
                            vscode_packages = output

                            lines[idx] = Config.get_repr_packages(
                                vscode_packages, False) + '\n'
                            d['Editor-Extensions'] = lines[idx].split('\n')

                            with open(f'{filepath}', 'w') as f:
                                f.writelines(lines)

                        if '<vscode-insiders:name,version>' in line:
                            idx = lines.index(line)
                            proc = Popen('code-insiders --list-extensions --show-versions'.split(
                            ), stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
                            output, _ = proc.communicate()
                            output = output.decode().splitlines()
                            vscode_packages = []
                            vscode_packages = [
                                {line.split('@')[0]: line.split('@')[1]} for line in output]
                            lines[idx] = Config.get_repr_packages(
                                vscode_packages, True).replace('\n ', '\n') + '\n'
                            d['Editor-Extensions'] = [line.split('@')[0]
                                                      for line in output]

                            with open(f'{filepath}', 'w') as f:
                                f.writelines(lines)

                        if '<atom>' in line or '<atom:name>' in line or '<apm>' in line or '<apm:name>' in line:
                            idx = lines.index(line)
                            proc = Popen(
                                'apm list --installed'.split(), stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
                            output, _ = proc.communicate()
                            output = output.decode().splitlines()[1:]
                            atom_packages = []
                            for val in output:
                                if val:
                                    atom_packages.append(val.replace('├──', '').replace(
                                        '└── ', '').strip().lower()[:-6])

                            lines[idx] = Config.get_repr_packages(
                                atom_packages, False) + '\n'
                            d['Editor-Extensions'] = lines[idx].split('\n')

                            with open(f'{filepath}', 'w') as f:
                                f.writelines(lines)

                        if '<atom:name,version>' in line or '<apm:name,version>' in line:
                            idx = lines.index(line)
                            proc = Popen(
                                'apm list --installed'.split(), stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
                            output, _ = proc.communicate()
                            output = output.decode().splitlines()[1:]
                            atom_packages = []
                            refined_output = []
                            for val in output:
                                if val:
                                    refined_output.append(val.replace(
                                        '├──', '').replace('└── ', '').strip())

                            atom_packages.append(
                                [{line.split('@')[0].lower(): line.split('@')[1].lower()} for line in refined_output])
                            atom_packages = atom_packages[0]
                            lines[idx] = Config.get_repr_packages(
                                atom_packages, True).replace('\n ', '\n') + '\n'
                            d['Editor-Extensions'] = [line.split('@')[0]
                                                      for line in output]

                            with open(f'{filepath}', 'w') as f:
                                f.writelines(lines)

                if 'Pip-Packages' in d:
                    with open(f'{filepath}', 'r') as f:
                        lines = f.readlines()

                    for line in lines:
                        if '<pip:name>' in line or '<pip>' in line or '<python>' in line or '<python:name>' in line:
                            idx = lines.index(line)
                            proc = Popen('pip list'.split(),
                                         stdin=PIPE, stdout=PIPE, stderr=PIPE)
                            output, _ = proc.communicate()
                            output = output.decode().splitlines()[2:]
                            pip_packages = []
                            pip_packages.append(
                                [line.lower().split()[0] for line in output])
                            pip_packages = pip_packages[0]

                            lines[idx] = Config.get_repr_packages(
                                pip_packages, False) + '\n'
                            d['Pip-Packages'] = lines[idx].split('\n')

                            with open(f'{filepath}', 'w') as f:
                                f.writelines(lines)

                        if '<pip:name,version>' in line or '<python:name,version>' in line:
                            idx = lines.index(line)
                            proc = Popen('pip list'.split(),
                                         stdin=PIPE, stdout=PIPE, stderr=PIPE)
                            output, _ = proc.communicate()
                            output = output.decode().splitlines()[2:]
                            pip_packages = []

                            pip_packages.append(
                                [{line.lower().split()[0]: line.lower().split()[1]} for line in output])
                            pip_packages = pip_packages[0]
                            d['Pip-Packages'] = [line.lower().split()[0]
                                                 for line in output]
                            lines[idx] = Config.get_repr_packages(
                                pip_packages, True).replace('\n ', '\n') + '\n'

                            with open(f'{filepath}', 'w') as f:
                                f.writelines(lines)

                if 'Node-Packages' in d:
                    with open(f'{filepath}', 'r') as f:
                        lines = f.readlines()

                    for line in lines:
                        if '<npm:name>' in line or '<npm>' in line or '<node:name>' in line or '<node>' in line:
                            idx = lines.index(line)
                            proc = Popen('npm list --global --depth=0'.split(),
                                         stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
                            output, _ = proc.communicate()
                            output = output.decode().splitlines()[1:]
                            refined_output = []
                            for val in output:
                                if val:
                                    refined_output.append(val.replace(
                                        '+--', '').replace('`--', '').strip())

                            npm_packages = []
                            npm_packages.append(
                                [line.split('@')[0] for line in refined_output])
                            npm_packages = npm_packages[0]
                            new_packages = []
                            for package in npm_packages:
                                package = package.replace(
                                    'UNMET PEER DEPENDENCY ', '')
                                new_packages.append(package)

                            lines[idx] = Config.get_repr_packages(
                                new_packages, False) + '\n'
                            d['Node-Packages'] = lines[idx].split('\n')

                            with open(f'{filepath}', 'w') as f:
                                f.writelines(lines)

                        if '<npm:name,version>' in line or '<node:name,version>' in line:
                            idx = lines.index(line)
                            proc = Popen('npm list --global --depth=0'.split(),
                                         stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
                            output, _ = proc.communicate()
                            if not 'empty' in output.decode():
                                output = output.decode().splitlines()[1:]
                                refined_output = []
                                for val in output:
                                    if val:
                                        refined_output.append(val.replace(
                                            '+--', '').replace('`--', '').strip())
                                npm_packages = []

                                npm_packages.append(
                                    [{line.split('@')[0]: line.split('@')[1]} for line in refined_output])
                                npm_packages = npm_packages[0]

                                lines[idx] = Config.get_repr_packages(
                                    npm_packages, True).replace('\n ', '\n') + '\n'
                                d['Node-Packages'] = [line.split('@')[0]
                                                      for line in refined_output]

                                with open(f'{filepath}', 'w') as f:
                                    f.writelines(lines)

                if signed:
                    with open(f'{filepath}', 'r') as f:
                        lines = f.readlines()

                    l = [line.strip() for line in lines]
                    if not '# --------------------Checksum Start-------------------------- #' in l or not '# --------------------Checksum End--------------------------- #' in l:
                        click.echo(click.style(
                            f'File Checksum Not Found! Run `electric sign {filepath}` ( Copied To Clipboard ) to sign your .electric configuration.', fg='red'))
                        copy_to_clipboard(f'electric sign {filepath}')
                        sys.exit()

                    if lines[-1] != '# --------------------Checksum End--------------------------- #':
                        click.echo(click.style(
                            'DataAfterChecksumError : Comments, Code And New lines Are Not Allowed After The Checksum End Header.', 'red'))
                        sys.exit()

                    if '# --------------------Checksum Start-------------------------- #' in l and '# --------------------Checksum End--------------------------- #' in l:
                        idx = 0
                        for item in l:
                            if item == '# --------------------Checksum Start-------------------------- #':
                                idx = list.index(l, item)

                        md5 = l[idx + 1].replace('#', '').strip()
                        sha256 = l[idx + 2].replace('#', '').strip()

                        # Generate Temporary Configuration File
                        with open(rf'{gettempdir()}\electric\configuration.electric', 'w+') as f:
                            f.writelines(lines[:-5])

                        md5_checksum = hashlib.md5(open(
                            rf'{gettempdir()}\electric\configuration.electric', 'rb').read()).hexdigest()
                        sha256_hash_checksum = hashlib.sha256()
                        with open(rf'{gettempdir()}\electric\configuration.electric', 'rb') as f:
                            # Read and update hash string value in blocks of 4K
                            for byte_block in iter(lambda: f.read(4096), b''):
                                sha256_hash_checksum.update(byte_block)

                        sha256_checksum = sha256_hash_checksum.hexdigest()
                        if md5 == md5_checksum and sha256 == sha256_checksum:
                            click.echo(click.style(
                                'Hashes Match!', 'bright_green'))
                        else:
                            click.echo(click.style(
                                'Hashes Don\'t Match!', 'red'))
                            os.remove(
                                rf'{gettempdir()}\electric\configuration.electric')
                            exit(1)
                        os.remove(
                            rf'{gettempdir()}\electric\configuration.electric')
        except FileNotFoundError:
            click.echo(click.style(
                f'Could Not Find {Fore.LIGHTCYAN_EX}{filepath}{Fore.RESET}.', fg='red'), err=True)
            time.sleep(2)
            sys.exit()
        d.pop('')

        return Config(d)

    def verify(self):  # sourcery no-metrics
        config = self.dictionary

        python_packages = config['Pip-Packages'] if 'Pip-Packages' in self.headers else None
        node_packages = config['Node-Packages'] if 'Node-Packages' in self.headers else None
        editor_extensions = config['Editor-Extensions'] if 'Editor-Extensions' in self.headers else None
        packages = config['Packages'] if 'Packages' in self.headers else None
        editor_type = config['Editor-Configuration'][0]['Editor'] if 'Editor-Configuration' in self.headers else None

        if packages:
            click.echo(click.style(
                '↓ Validating Electric Packages        ↓', 'cyan'))


            for package in packages:
                if isinstance(package, dict):
                    if package:
                        
                        proc = Popen(
                            rf'electric show {list(package.keys())[0]}', stdin=PIPE, stdout=PIPE, stderr=PIPE)
                        output, err = proc.communicate()
                        err = 'UnicodeEncodeError' in err.decode()
                        
                        if 'Could Not Find Any Packages' in output.decode() or 'Not Found.' in output.decode() or err:
                            click.echo(click.style(
                                f'`{list(package.keys())[0]}` does not exist or has been removed.', 'red'))
                            sys.exit()

                else:
                    if package:
                        proc = Popen(
                            rf'electric show {package}', stdin=PIPE, stdout=PIPE, stderr=PIPE)
                        output, err = proc.communicate()
                        err = 'UnicodeEncodeError' not in err.decode()
                        if 'Could Not Find Any Packages' in output.decode() or err:
                            click.echo(click.style(
                                f'`{package}` does not exist or has been removed.', 'red'))
                            sys.exit()

        if node_packages:
            click.echo(click.style(
                '↓ Validating Node or Npm Modules      ↓', 'cyan'))
            for package_name in node_packages:
                if isinstance(package_name, dict):
                    if package_name:
                        if not Config.check_node_name(list(package_name.keys())[0]):
                            click.echo(click.style(
                                f'The ( npm | node ) module => `{list(package_name.keys())[0]}` does not exist or has been removed.', 'red'))
                            sys.exit()
                else:
                    if package_name:
                        if not Config.check_node_name(package_name):
                            click.echo(click.style(
                                f'The ( npm | node ) module => `{package_name}` does not exist or has been removed.', 'red'))
                            sys.exit()

        click.echo(click.style(
            '↓ Validating Python or Pip Modules    ↓', 'cyan'))

        if python_packages:
            for package in python_packages:
                if isinstance(package, dict):
                    if package:
                        if not Config.check_pypi_name(list(package.keys())[0]):
                            click.echo(click.style(
                                f'The ( npm | node ) module => `{list(package.keys()[0])}` does not exist or has been removed.', 'red'))
                            sys.exit()
                else:
                    if package:
                        if not Config.check_pypi_name(package):
                            click.echo(click.style(
                                f'The ( python | pip ) module => `{package}` does not exist or has been removed.', 'red'))
                            sys.exit()

        if editor_type:
            if not editor_type in ['Visual Studio Code', 'Visual Studio Code Insiders', 'Atom', 'Sublime Text 3']:
                click.echo(click.style(
                    f'{editor_type} is not supported by electric yet!', 'red'))
            else:
                if editor_extensions:
                    click.echo(click.style(
                        '↓ Validating Editor Extensions        ↓', 'cyan'))
                    if editor_type == 'Visual Studio Code' or editor_type == 'Visual Studio Code Insiders':
                        for package_name in editor_extensions:
                            if isinstance(package_name, dict):
                                if package_name:
                                    if not Config.check_vscode_name(list(package_name.keys())[0]):
                                        click.echo(click.style(
                                            f'Invalid Extension Name => {list(package_name.keys())[0]}', 'red'))
                                        sys.exit()
                            else:
                                if package_name:
                                    if not Config.check_vscode_name(package_name):
                                        click.echo(click.style(
                                            f'Invalid Extension Name => {package_name}', 'red'))
                                        sys.exit()

                    if editor_type == 'Sublime Text 3':
                        for package_name in editor_extensions:
                            if isinstance(package_name, dict):
                                if package_name:
                                    if not Config.check_sublime_name(list(package_name.keys())[0]):
                                        click.echo(click.style(
                                            f'Invalid Extension Name => {list(package_name.keys())[0]}', 'red'))
                                        sys.exit()
                            else:
                                if package_name:
                                    if not Config.check_sublime_name(package_name):
                                        click.echo(click.style(
                                            f'Invalid Extension Name => {package_name}', 'red'))

                    if editor_type == 'Atom':
                        for package_name in editor_extensions:
                            if isinstance(package_name, dict):
                                if package_name:
                                    if not Config.check_atom_name(list(package_name.keys())[0]):
                                        click.echo(click.style(
                                            f'Invalid Extension Name => {list(package_name.keys())[0]}', 'red'))
                                        sys.exit()
                            else:
                                if package_name:
                                    if not Config.check_atom_name(package_name):
                                        click.echo(click.style(
                                            f'Invalid Extension Name => {package_name}', 'red'))

    def install(self, include_versions: bool, install_directory: str, sync: bool, metadata: Metadata):
        if is_admin():
            flags = get_install_flags(install_directory, metadata)
            config = self.dictionary
            python_packages = config['Pip-Packages'] if 'Pip-Packages' in self.headers else None
            node_packages = config['Node-Packages'] if 'Node-Packages' in self.headers else None
            editor_extensions = config['Editor-Extensions'] if 'Editor-Extensions' in self.headers else None
            packages = config['Packages'] if 'Packages' in self.headers else None
            editor_type = config['Editor-Configuration'][0]['Editor'] if 'Editor-Configuration' in self.headers else None

            command = ''
            pip_command = ''
            idx = 1
            if not include_versions:
                for package in packages:
                    if idx == len(packages):
                        command += list(package.keys())[0]
                        idx += 1
                        continue
                    command += list(package.keys())[0] + ','
                    idx += 1

                for flag in flags:
                    command += ' ' + flag

                for pkg in command.split(','):
                    os.system(f'electric install {pkg}')
            else:
                for package in packages:
                    if list(package.values())[0] is None:
                        os.system(f'electric install {list(package.keys())[0]}')
                    else:
                        os.system(f'electric install {list(package.keys())[0]} --version {list(package.values())[0]}')
            
            package_versions = []
            package_names = []
            for package in python_packages:
                if idx == len(packages):
                    package_versions.append(package[list(package.keys())[0]])
                    package_names.append(list(package.keys())[0])
                    pip_command += list(package.keys())[0]
                    idx += 1
                    continue

                package_versions.append(package[list(package.keys())[0]])
                package_names.append(list(package.keys())[0])
                pip_command += list(package.keys())[0] + ','
                idx += 1

            os.system('refreshenv')

            idx = 0

            if include_versions and package_versions:
                for package_name in package_names:
                    os.system(
                        f'electric install --python {package_name} --version {versions[idx]}')
                    idx += 1                                                                                                                                                                                                                     
            else:
                if include_versions:
                    print("No Versions Specified With This Configuration!")
                    sys.exit()

                for package_name in package_names:
                    os.system(f'electric install --python {package_name}')
                    idx += 1

            if editor_type == 'Visual Studio Code' or editor_type == 'Visual Studio Code Insiders' and editor_extensions != []:
                editor_extensions = config['Editor-Extensions'] if 'Editor-Extensions' in self.headers else None
                package_versions = []
                print(editor_extensions)

                for extension in editor_extensions:
                    extension = list(extension.keys())[0]
                    version = list(extension.values())[0]
                    command = f'electric install --vscode {extension}'

                    if version and include_versions:
                        command = f'electric install --vscode {extension} --version {version}'

                    try:
                        os.system(command)
                    except:
                        if not confirm('Would you like to continue configuration installation?'):
                            sys.exit()

            if editor_type == 'Sublime Text 3' and editor_extensions:
                editor_extensions = config['Editor-Extensions'] if 'Editor-Extensions' in self.headers else None
                for extension in editor_extensions:
                    extension = list(extension.keys())[0]

                    if extension != 'Package Control':
                        command = f'electric install --sublime \"{extension}\"'

                    try:
                        os.system(command)
                    except:
                        if not confirm('Would you like to continue configuration installation?'):
                            sys.exit()

            if editor_type == 'Atom' and editor_extensions:
                editor_extensions = config['Editor-Extensions'] if 'Editor-Extensions' in self.headers else None
                for extension in editor_extensions:
                    extension = list(extension.keys())[0]
                    command = f'electric install --atom {extension}'
                    try:
                        os.system(command)
                    except:
                        if not confirm('Would you like to continue configuration installation?'):
                            sys.exit()

            if node_packages:
                for node_package in node_packages:
                    node_package = list(node_package)[0]
                    try:
                        os.system(
                            f'electric install --node {node_package}')
                    except:
                        if not confirm('Would you like to continue configuration installation?'):
                            sys.exit()

        else:
            click.echo(click.style(
                'Config installation must be ran as administrator!', fg='red'), err=True)

    def uninstall(self):
        if is_admin():
            config = self.dictionary
            python_packages = config['Pip-Packages'] if 'Pip-Packages' in self.headers else None
            node_packages = config['Node-Packages'] if 'Node-Packages' in self.headers else None
            editor_extensions = config['Editor-Extensions'] if 'Editor-Extensions' in self.headers else None
            packages = config['Packages'] if 'Packages' in self.headers else None
            editor_type = config['Editor-Configuration'][0]['Editor'] if 'Editor-Configuration' in self.headers else None
            if packages:
                for package in packages:
                    try:
                        os.system(
                            f'electric uninstall {list(package.keys())[0]}')
                    except:
                        if not confirm('Would you like to continue configuration installation?'):
                            sys.exit()

            if python_packages:
                for python_package in python_packages:
                    command = f'electric uninstall --python {list(python_package.keys())[0]}'
                    try:
                        os.system(command)
                    except:
                        if not confirm('Would you like to continue configuration installation?'):
                            sys.exit()

            if editor_type == 'Visual Studio Code' and editor_extensions:
                editor_extensions = config['Editor-Extensions'] if 'Editor-Extensions' in self.headers else None
                for extension in editor_extensions:
                    extension = list(extension.keys())[0]
                    command = f'electric uninstall --vscode {extension}'
                    try:
                        os.system(command)
                    except:
                        if not confirm('Would you like to continue configuration installation?'):
                            sys.exit()

            if editor_type == 'Atom' and editor_extensions:
                editor_extensions = config['Editor-Extensions'] if 'Editor-Extensions' in self.headers else None
                for extension in editor_extensions:
                    extension = list(extension.keys())[0]
                    command = f'atom uninstall --atom {extension}'
                    try:
                        os.system(command)
                    except:
                        if not confirm('Would you like to continue configuration'):
                            sys.exit()

            if node_packages:
                for node_package in node_packages:
                    node_package = list(node_package)[0]
                    try:
                        os.system(f'electric uninstall --node {node_package}')
                    except:
                        if not confirm('Would you like to continue configuration installation?'):
                            sys.exit()
        else:
            click.echo(click.style(
                'Config installation must be ran as administrator!', fg='red'), err=True)

# TODO: For Installing VISUAL STUDIO EXTENSIONS
# DOWNLOAD THE VSIX FILE FROM https://marketplace.visualstudio.com/_apis/public/gallery/publishers/JaredParMSFT/vsextensions/VsVim/2.8.0.0/vspackage (example => can be scraped)
# Install using vsixinstaller /q path_to_vsix

# TODO: Add Support for intellij idea plugins
# https://intellij-support.jetbrains.com/hc/en-us/community/posts/206178329-How-to-install-idea-plugins-from-the-command-line-
# https://intellij-support.jetbrains.com/hc/en-us/articles/206544519

# TODO: Add support for eclipse plugins

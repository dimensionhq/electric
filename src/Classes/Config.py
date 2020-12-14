from tempfile import gettempdir
from sys import platform
from subprocess import *
from external import *
from utils import *
import pyperclip
import colorama
import socket
import click
import ssl


refreshenv = PathManager.get_current_directory() + r'\scripts\refreshvars.bat'

tags = [
    '<pip>',
    '<pip:name>',
    '<pip:name,version>'
    '<npm>',
    '<npm:name>',
    '<npm:name,version>',
    '<vscode>',
    '<vscode:name>',
    '<vscode:name,version>'
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
            click.echo(click.style(f'Description => {self.description}', fg='yellow'))    
        
            if platform == 'win32' and not self.os == 'Windows':
                if self.os:
                    if not click.confirm(f'WARNING: This Config Has A Target OS Of {self.os}. Would you like to continue?'):
                        exit()

        packages = self.dictionary['Packages'] if 'Packages' in self.headers else None

        if 'Pip-Packages' in headers:
            try:
                Popen('pip', stdin=PIPE, stdout=PIPE, stderr=PIPE)
            except FileNotFoundError:
                if not any(['python' in package for package in packages]):
                    click.echo(click.style('Pip Not Found, Aborting Config Installation!', fg='red'))
                    exit()

        if 'Node-Packages' in headers:
            try:
                Popen('npm', stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
            except FileNotFoundError:
                if not any(['nodejs' in package for package in packages]):
                    click.echo(click.style('Node Not Found, Aborting Config Installation!', fg='red'))
                    exit()

        editor_type = self.dictionary['Editor-Configuration'][0]['Editor'] if 'Editor-Configuration' in self.headers else None
        if editor_type:
            if not find_existing_installation(editor_type, 'Visual Studio Code') and not any(['vscode' in package for package in packages]):
                click.echo(click.style('Visual Studio Code Not Found, Aborting Config Installation!', fg='red'))
            else:
                if editor_type == 'Visual Studio Code':
                    try:
                        Popen('code --help', stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
                    except FileNotFoundError:
                        click.echo(click.style('Visual Studio Code Found But Shell Extension Not Found, Aborting Config Installation!', fg='red'))

        click.echo(click.style('All Tests Passed!', 'green'))


    @staticmethod
    def get_repr_packages(packages: list, version: bool):
        if version:
            packages = str(packages).replace('\'', '').replace('[', '').replace(']', '').replace(',', '').replace('{', '').replace('}', '\n').replace(':', ' =>').strip()
            return packages
        else:
            packages = str(packages).replace('\'', '').replace('[', '').replace(']', '').replace(',', '').strip().replace(' ', '\n')
            return packages

   
    @staticmethod
    def check_pypi_name(pypi_package_name, pypi_registry_host=None):
        """
        Check if a package name exists on pypi.

        TODO: Document the Registry URL construction.
            It may not be obvious how pypi_package_name and pypi_registry_host are used
            I'm appending the simple HTTP API parts of the registry standard specification.

        It will return True if the package name, or any equivalent variation as defined by PEP 503 normalisation
        rules (https://www.python.org/dev/peps/pep-0503/#normalized-names) is registered in the PyPI registry.

        >>> check_pypi_name('pip')
        True
        >>> check_pypi_name('Pip')
        True

        It will return False if the package name, or any equivalent variation as defined by PEP 503 normalisation
        rules (https://www.python.org/dev/peps/pep-0503/#normalized-names) is not registered in the PyPI registry.

        >>> check_pypi_name('testy_mc-test_case-has.a.cousin_who_should_never_write_a_package')
        False

        :param pypi_package_name:
        :param pypi_registry_host:
        :return:
        """
        if pypi_registry_host is None:
            pypi_registry_host = 'pypi.org'

        # Just a helpful reminder why this bytearray size was chosen.
        #                            HTTP/1.1 200 OK
        #                            HTTP/1.1 404 Not Found

        receive_buffer = bytearray(b'------------')
        context = ssl.create_default_context()
        ssl_http_socket = context.wrap_socket(socket.socket(socket.AF_INET), server_hostname=pypi_registry_host)
        ssl_http_socket.connect((pypi_registry_host, 443))
        ssl_http_socket.send(b''.join([
            b"HEAD /simple/", pypi_package_name.encode('ascii'), b"/ HTTP/1.0", b"\r\n",
            b"Host: ", pypi_registry_host.encode('ascii'), b"\r\n",
            b"\r\n\r\n"
        ]))
        ssl_http_socket.recv_into(receive_buffer)

        # Early return when possible.
        if b'HTTP/1.1 200' in receive_buffer:
            ssl_http_socket.shutdown(1)
            ssl_http_socket.close()
            return True
        elif b'HTTP/1.1 404' in receive_buffer:
            ssl_http_socket.shutdown(1)
            ssl_http_socket.close()
            return False

        remaining_bytes = ssl_http_socket.recv(2048)
        redirect_path_location_start = remaining_bytes.find(b'Location:') + 10
        redirect_path_location_end = remaining_bytes.find(b'\r\n', redirect_path_location_start)
        # Append the trailing slash to avoid a needless extra redirect.
        redirect_path = remaining_bytes[redirect_path_location_start:redirect_path_location_end] + b'/'

        ssl_http_socket.shutdown(1)
        ssl_http_socket.close()

        # Reset the bytearray to empty
        # receive_buffer = bytearray(b'------------')

        ssl_http_socket = context.wrap_socket(socket.socket(socket.AF_INET), server_hostname=pypi_registry_host)
        ssl_http_socket.connect((pypi_registry_host, 443))

        ssl_http_socket.send(b''.join([
            b"HEAD ", redirect_path, b" HTTP/1.0", b"\r\n",
            b"Host: ", pypi_registry_host.encode('ascii'), b"\r\n",
            b"\r\n\r\n"]))
        ssl_http_socket.recv_into(receive_buffer)

        if b'HTTP/1.1 200' in receive_buffer:
            return True
        elif b'HTTP/1.1 404' in receive_buffer:
            return False
        else:
            NotImplementedError('A definitive answer was not found by primary or secondary lookups.')


    @staticmethod
    def generate_configuration(filepath: str, signed=True):
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
                                    click.echo(click.style(f'Error On Line {ln_number + 1} At {filepath}', fg='red'))
                                    message = line.replace(':', '')
                                    click.echo(click.style(f'ValueNotFoundError : No Value Provided For Key :: {colorama.Fore.CYAN}{message}', fg='yellow'))
                                    exit()
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

                                    click.echo(click.style(f'Error On Line {ln_number + 1} At {filepath}', fg='red'))
                                    message = line.replace(':', '')
                                    click.echo(click.style(f'ValueNotFoundError : Expecting A Value Pair With `=>` Operator For Key :: {colorama.Fore.CYAN}{message}', fg='yellow'))
                                    exit()

                            d[header].append({ k : v.replace('"', '') })
                
                if 'Editor-Extensions' in d:
                    with open(f'{filepath}', 'r') as f:
                        
                        lines = f.readlines()

                    for line in lines:
                        if '<vscode:name>' in line or '<vscode>' in line:
                            idx = lines.index(line)
                            proc = Popen('code --list-extensions'.split(), stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
                            output, _ = proc.communicate()
                            output = output.decode().splitlines()
                            vscode_packages = []
                            vscode_packages = output           
                            
                            lines[idx] = Config.get_repr_packages(vscode_packages, False) + '\n'
                            
                            with open(f'{filepath}', 'w') as f:
                                f.writelines(lines)
                        if '<vscode:name,version>' in line:
                            idx = lines.index(line)
                            proc = Popen('code --list-extensions --show-versions'.split(), stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
                            output, _ = proc.communicate()
                            output = output.decode().splitlines()
                            vscode_packages = []
                            vscode_packages = [{line.split('@')[0] : line.split('@')[1]} for line in output]
                            lines[idx] = Config.get_repr_packages(vscode_packages, True).replace('\n ', '\n') + '\n'
                             
                            with open(f'{filepath}', 'w') as f:
                                f.writelines(lines)
                                                
                if 'Pip-Packages' in d:
                    with open(f'{filepath}', 'r') as f:
                        
                        lines = f.readlines()
                    
                    for line in lines:
                        if '<pip:name>' in line or '<pip>' in line:
                            idx = lines.index(line)
                            proc = Popen('pip list'.split(), stdin=PIPE, stdout=PIPE, stderr=PIPE)
                            output, _ = proc.communicate()
                            output = output.decode().splitlines()[2:]
                            pip_packages = []
                            pip_packages.append([line.split()[0] for line in output])            
                            pip_packages = pip_packages[0]
                            
                            lines[idx] = Config.get_repr_packages(pip_packages, False) + '\n'

                            with open(f'{filepath}', 'w') as f:                                
                                f.writelines(lines)

                        if '<pip:name,version>' in line:
                            idx = lines.index(line)
                            proc = Popen('pip list'.split(), stdin=PIPE, stdout=PIPE, stderr=PIPE)
                            output, _ = proc.communicate()
                            output = output.decode().splitlines()[2:]
                            pip_packages = []
                            
                            pip_packages.append([{line.split()[0] : line.split()[1]} for line in output])
                            pip_packages = pip_packages[0]
                            
                            lines[idx] = Config.get_repr_packages(pip_packages, True).replace('\n ', '\n') + '\n'
                            with open(f'{filepath}', 'w') as f:                                
                                f.writelines(lines)
                            
                if 'Node-Packages' in d:
                    with open(f'{filepath}', 'r') as f:
                        lines = f.readlines()
   
                    for line in lines:
                        if '<npm:name>' in line or '<npm>' in line:
                            idx = lines.index(line)
                            proc = Popen('npm list --global --depth=0'.split(), stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
                            output, _ = proc.communicate()
                            output = output.decode().splitlines()[1:]
                            refined_output = []
                            for val in output:
                                if val:
                                    refined_output.append(val.replace('+--', '').replace('`--', '').strip())
                            npm_packages = []
                            npm_packages.append([line.split('@')[0] for line in refined_output])            
                            npm_packages = npm_packages[0]
                            
                            lines[idx] = Config.get_repr_packages(npm_packages, False) + '\n'
                            with open(f'{filepath}', 'w') as f:
                                f.writelines(lines)

                        if '<npm:name,version>' in line:
                            
                            idx = lines.index(line)
                            proc = Popen('npm list --global --depth=0'.split(), stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
                            output, _ = proc.communicate()
                            output = output.decode().splitlines()[1:]
                            refined_output = []
                            for val in output:
                                if val:
                                    refined_output.append(val.replace('+--', '').replace('`--', '').strip())
                            npm_packages = []
                            
                            npm_packages.append([{line.split('@')[0] : line.split('@')[1]} for line in refined_output])
                            npm_packages = npm_packages[0]
                            
                            lines[idx] = Config.get_repr_packages(npm_packages, True).replace('\n ', '\n') + '\n'
                            with open(f'{filepath}', 'w') as f:
                                f.writelines(lines)

                if signed:
                    with open(f'{filepath}', 'r') as f:
                        lines = f.readlines()

                    l = [line.strip() for line in lines]
                    if not '# --------------------Checksum Start-------------------------- #' in l or not '# --------------------Checksum End--------------------------- #' in l:
                        click.echo(click.style(f'File Checksum Not Found! Run `electric sign {filepath}` ( Copied To Clipboard ) to sign your .electric configuration.', fg='red'))
                        pyperclip.copy(f'electric sign {filepath}')
                        exit()
                    
                    if lines[-1] != '# --------------------Checksum End--------------------------- #':
                        click.echo(click.style('DataAfterChecksumError : Comments, Code And New lines Are Not Allowed After The Checksum End Header.', 'red'))
                        exit()
                    
                    if '# --------------------Checksum Start-------------------------- #' in l and '# --------------------Checksum End--------------------------- #' in l:
                        idx = 0
                        for item in l:
                            if item == '# --------------------Checksum Start-------------------------- #':
                                idx = list.index(l, item)
                        print(l[idx])
                        exit()
                        md5 = l[idx + 2].replace('#', '').strip()
                        sha256 = l[idx + 3].replace('#', '').strip()
                        # Generate Temporary Configuration File
                        with open(rf'{gettempdir()}\electric\configuration.electric', 'w+') as f:
                            f.writelines(lines[:-7])
            
                        md5_checksum = hashlib.md5(open(rf'{gettempdir()}\electric\configuration.electric', 'rb').read()).hexdigest()
                        sha256_hash_checksum = hashlib.sha256()
                        with open(rf'{gettempdir()}\electric\configuration.electric', 'rb') as f:
                            # Read and update hash string value in blocks of 4K
                            for byte_block in iter(lambda: f.read(4096),b''):
                                sha256_hash_checksum.update(byte_block)
                        
                        sha256_checksum = sha256_hash_checksum.hexdigest()
                        if md5 == md5_checksum and sha256 == sha256_checksum:
                            click.echo(click.style('Hashes Match!', 'green'))
                        else:
                            click.echo(click.style('Hashes Don\'t Match! Aborting Installation!', 'red'))
                            os.remove(rf'{gettempdir()}\electric\configuration.electric')
                            exit(1)
                        os.remove(rf'{gettempdir()}\electric\configuration.electric')
        except FileNotFoundError:
            click.echo(click.style(f'Could Not Find {Fore.BLUE}{filepath}{Fore.RESET}.', fg='red'), err=True)
            exit()
        d.pop('')
        return Config(d)


    def verify(self):
        config = self.dictionary
        python_packages = config['Pip-Packages'] if 'Pip-Packages' in self.headers else None
        node_packages = config['Node-Packages'] if 'Node-Packages' in self.headers else None
        editor_extensions = config['Editor-Extensions'] if 'Editor-Extensions' in self.headers else None
        packages = config['Packages'] if 'Packages' in self.headers else None
        editor_type = config['Editor-Configuration'][0]['Editor'] if 'Editor-Configuration' in self.headers else None
        click.echo(click.style('↓ Validating Electric Packages        ↓', 'cyan'))
        for package in packages:
            proc = Popen(f'electric show {list(package.keys())[0]}', stdin=PIPE, stdout=PIPE, stderr=PIPE)
            output, err = proc.communicate()
            if 'Could Not Find Any Packages' in output.decode():
                click.echo(click.style(f'`{list(package.keys())[0]}` does not exist or has been removed.', 'red'))
                exit()

        click.echo(click.style('↓ Validating Node or Npm Modules      ↓', 'cyan'))

        for package in node_packages:
            proc = Popen(f'npm show {list(package.keys())[0]}', stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
            output, err = proc.communicate()
            if f'\'{list(package.keys())[0]}\' is not in the npm registry.' in err.decode():
                click.echo(click.style(f'The ( npm | node ) module => `{list(package.keys())[0]}` does not exist or has been removed.', 'red'))
                exit()
        
        click.echo(click.style('↓ Validating Python or Pip Modules    ↓', 'cyan'))
        
        for package in python_packages:
            if not Config.check_pypi_name(list(package.keys())[0].lower()):
                click.echo(click.style(f'The ( python | pip ) module => `{list(package.keys())[0]}` does not exist or has been removed.', 'red'))
                exit()

        if not editor_type == 'Visual Studio Code':
            click.echo(click.style(f'The editor => {editor_type} is not supported by electric yet!', 'red'))
        else:
            if editor_extensions:
                for package in editor_extensions:
                    if not '.' in list(package.keys())[0]:
                        click.echo(click.style(f'Invalid Extension Name => {list(package.keys())[0]}', 'red'))


    def install(self, install_directory: str, no_cache: str, sync: bool, metadata: Metadata):
        if is_admin():
            flags = get_install_flags(install_directory, no_cache, sync, metadata)
            config = self.dictionary
            python_packages = config['Pip-Packages'] if 'Pip-Packages' in self.headers else None
            node_packages = config['Node-Packages'] if 'Node-Packages' in self.headers else None
            editor_extensions = config['Editor-Extensions'] if 'Editor-Extensions' in self.headers else None
            packages = config['Packages'] if 'Packages' in self.headers else None
            editor_type = config['Editor-Configuration'][0]['Editor'] if 'Editor-Configuration' in self.headers else None

            command = ''
            pip_command = ''
            idx = 1

            for package in packages:
                if idx == len(packages):
                    command += list(package.keys())[0]
                    idx += 1 
                    continue
                command += list(package.keys())[0] + ','
                idx += 1
            for flag in flags:
                command += ' ' + flag
            
            os.system(f'electric install {command}')

            for package in python_packages:
                if idx == len(packages):
                    pip_command += list(package.keys())[0]
                    idx += 1 
                    continue
                pip_command += list(package.keys())[0] + ','
                idx += 1

            os.system(f'{refreshenv} & electric install --python {pip_command}')


            if editor_type == 'Visual Studio Code' and editor_extensions:
                editor_extensions = config['Editor-Extensions'] if 'Editor-Extensions' in self.headers else None
                for extension in editor_extensions:
                    extension = list(extension.keys())[0]
                    command = f'electric install --vscode {extension}'
                    try:
                        os.system(command)
                    except:
                        if not click.confirm('Would you like to continue configuration installation?'):
                            exit()
            
            if editor_type == 'Sublime Text 3' and editor_extensions:                
                editor_extensions = config['Editor-Extensions'] if 'Editor-Extensions' in self.headers else None
                for extension in editor_extensions:
                    extension = list(extension.keys())[0]
                    command = f'electric install --sublime {extension}'
                    try:
                        os.system(command)
                    except:
                        if not click.confirm('Would you like to continue configuration installation?'):
                            exit()

            if editor_type == 'Atom' and editor_extensions:                
                editor_extensions = config['Editor-Extensions'] if 'Editor-Extensions' in self.headers else None
                for extension in editor_extensions:
                    extension = list(extension.keys())[0]
                    command = f'electric install --atom {extension}'
                    try:
                        os.system(command)
                    except:
                        if not click.confirm('Would you like to continue configuration installation?'):
                            exit()

            if node_packages:
                for node_package in node_packages:
                    node_package = list(node_package)[0]
                    try:
                        os.system(f'{refreshenv} & electric install --node {node_package}')
                    except:
                        if not click.confirm('Would you like to continue configuration installation?'):
                            exit()

        else:
            click.echo(click.style('Config installation must be ran as administrator!', fg='red'), err=True)


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
                        os.system(f'electric uninstall {list(package.keys())[0]}')
                    except:
                        if not click.confirm('Would you like to continue configuration installation?'):
                            exit()
            
            if python_packages:
                for python_package in python_packages:
                    command = f'electric uninstall --python {list(python_package.keys())[0]}'
                    try:
                        os.system(command)
                    except:
                        if not click.confirm('Would you like to continue configuration installation?'):
                            exit()
            
            if editor_type == 'Visual Studio Code' and editor_extensions:
                editor_extensions = config['Editor-Extensions'] if 'Editor-Extensions' in self.headers else None
                for extension in editor_extensions:
                    extension = list(extension.keys())[0]
                    command = f'electric uninstall --vscode {extension}'
                    try:
                        os.system(command)
                    except:
                        if not click.confirm('Would you like to continue configuration installation?'):
                            exit()
            if node_packages:
                for node_package in node_packages:
                    node_package = list(node_package)[0]
                    try:
                        os.system(f'electric uninstall --node {node_package}')
                    except:
                        if not click.confirm('Would you like to continue configuration installation?'):
                            exit()
        else:
            click.echo(click.style('Config installation must be ran as administrator!', fg='red'), err=True)

######################################################################
#                      Copyright 2021 XtremeDevX                     #
#                 SPDX-License-Identifier: Apache-2.0                #
######################################################################

# TODO: Add Conflict-With Field For Json To Differentiate Between Microsoft Visual Studio Code and Microsoft Visual Studio Code Insiders
from halo import Halo
import os
import sys
import time as tm
import click
import halo
from keyboard import add_hotkey, remove_hotkey
from colorama import Fore
from multiprocessing import freeze_support
from extension import write, write_debug, write_verbose
from Classes.Packet import Packet
from Classes.Setting import Setting
from Classes.ThreadedInstaller import ThreadedInstaller
from cli import SuperChargeCLI
from info import __version__
from logger import *
from registry import get_environment_keys, get_uninstall_key, send_query
from utils import *

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help', '-?'])

@click.group(cls=SuperChargeCLI)
@click.version_option(__version__)
@click.pass_context
def cli(_):
    # Make electric portable / tools directory if it doesn't exist
    if not os.path.isdir(os.path.expanduser('~') + r'\electric'):
        os.mkdir(os.path.expanduser('~') + r'\electric')

    # Create the appdata directory for electric if it doesn't exist
    if not (os.path.isdir(rf'{PathManager.get_appdata_directory()}')):
        os.mkdir(rf'{PathManager.get_appdata_directory()}')

    # Check if superlog.txt exists in USERAPPDATA
    if not os.path.isfile(rf'{PathManager.get_appdata_directory()}\superlog.txt'):
        from datetime import date
        # Create the superlog.txt and write the current timestamp
        with open(rf'{PathManager.get_appdata_directory()}\superlog.txt', 'w+') as f:
            f.write(
                f'{date.today().year} {date.today().month} {date.today().day}')

    # Check if settings.json exists in USERAPPDATA
    if not os.path.isfile(rf'{PathManager.get_appdata_directory()}\settings.json'):
        click.echo(click.style(
            f'Creating settings.json at {Fore.LIGHTCYAN_EX}{PathManager.get_appdata_directory()}{Fore.RESET}', fg='bright_green'))
        from settings import initialize_settings
        # Create the settings.json file and write default settings into it
        initialize_settings()

    # Check if packages.json exists in USERAPPDATA
    if not os.path.isfile(rf'{PathManager.get_appdata_directory()}\packages.json'):
        # Otherwise create and write to packages.json
        update_package_list()

    # Create USERAPPDATA/Current if it doesn't exist
    if not os.path.isdir(PathManager.get_appdata_directory() + r'\Current'):
        os.mkdir(PathManager.get_appdata_directory() + r'\Current')

    # Update electric if needed (see the function for further clarification)
    update_electric()


@cli.command(aliases=['i'], context_settings=CONTEXT_SETTINGS)
@click.argument('package_name', required=False, default='test')
@click.option('--version', '-v', type=str, help='Install a certain version of a package')
@click.option('--nightly', '--pre-release', is_flag=True, help='Install a nightly or pre-release build of a package')
@click.option('--portable', '--non-admin', '-p', is_flag=True, help='Install a portable version of a package')
@click.option('--verbose', '-vb', is_flag=True, help='Enable verbose mode for installation')
@click.option('--debug', '-d', is_flag=True, help='Enable debug mode for installation')
@click.option('--no-progress', '-np', is_flag=True, default=False, help='Disable progress bar for installation')
@click.option('--update', '-up', is_flag=True, default=False, help='Update electric before installation')
@click.option('--no-color', '-nc', is_flag=True, help='Disable colored output for installation')
@click.option('--log-output', '-l', 'logfile', help='Log output to the specified file')
@click.option('--install-dir', '-dir', 'install_directory', help='Specify an installation directory for a package')
@click.option('--virus-check', '-vc', is_flag=True, help='Check for virus before installation')
@click.option('-y', '--yes', is_flag=True, help='Accept all prompts during installation')
@click.option('--silent', '-s', is_flag=True, help='Completely silent installation without any output to console')
@click.option('--vscode', '-vs', is_flag=True, help='Specify a Visual Studio Code extension to install')
@click.option('--sublime', '-sb', is_flag=True, help='Specify a Sublime Text 3 extension to install')
@click.option('--atom', '-ato', is_flag=True, help='Specify an Atom extension to install')
@click.option('--python', '-py', is_flag=True, help='Specify a Python package to install')
@click.option('--node', '-npm', is_flag=True, help='Specify a Npm package to install')
@click.option('--sync', '-sc', is_flag=True, help='Force downloads and installations one after another')
@click.option('--reduce', '-rd', is_flag=True, help='Cleanup all traces of package after installation')
@click.option('--rate-limit', '-rl', type=int, default=-1)
@click.option('--force', '-f', is_flag=True, help='Force install a package, ignoring any existing installations of a package.')
@click.option('--configuration', '-cf', is_flag=True, help='Specify a config file to install')
@click.option('--plugin', '-pl', is_flag=True, help='Specify a plugin to install')
@click.option('--manifest', '-m', 'manifest', help='Read from a manifest file instead of querying from the community repository')
@click.pass_context
def install(
    ctx,
    package_name: str,
    verbose: bool,
    debug: bool,
    no_progress: bool,
    no_color: bool,
    logfile: str,
    yes: bool,
    silent: bool,
    python: bool,
    update: bool,
    install_directory: str,
    virus_check: bool,
    sync: bool,
    reduce: bool,
    rate_limit: int,
    node: bool,
    vscode: bool,
    atom: bool,
    sublime: bool,
    force: bool,
    configuration: bool,
    version: str,
    nightly: bool,
    portable: bool,
    plugin: bool,
    manifest: str,
):
    """
    Install a package or a list of packages.
    """
    start_log()
    if not manifest and package_name == 'test':
        print(f'{Fore.LIGHTRED_EX}A Package Name Must Be Supplied\nUsage: electric install <package-name>\n\nExamples:\nelectric install {Fore.LIGHTGREEN_EX}sublime-text-3{Fore.RESET}\n{Fore.LIGHTRED_EX}electric install {Fore.LIGHTGREEN_EX}sublime-text-3,notepad++{Fore.RESET}')
        sys.exit()

    
    if configuration:
        ctx.invoke(
            config,
            config_path=package_name,
            remove=False,
            verbose=verbose,
            debug=debug,
            no_progress=no_progress,
            logfile=logfile,
            install_directory=install_directory,
            virus_check=virus_check,
            yes=yes,
            silent=silent,
            sync=sync,
            reduce=reduce,
            rate_limit=rate_limit
        )
        sys.exit()

    if logfile:
        logfile = logfile.replace('=', '')
        logfile = logfile.replace('.txt', '.log')
        from logging import INFO
        create_config(logfile, INFO, 'Install')

    log_info('Generating metadata...', logfile)

    metadata = generate_metadata(
        no_progress, silent, verbose, debug, no_color, yes, logfile, virus_check, reduce, rate_limit, Setting.new(), sync)
    
    if update:
        write('Updating Electric', 'bright_green', metadata)
        update_package_list()

    if plugin:
        handle_plugin_installation(package_name, metadata)
        sys.exit()
       
    
    log_info('Successfully generated metadata.', metadata.logfile)

    handle_external_installation(
        python, node, vscode, sublime, atom, version, package_name, metadata)

    log_info('Setting up custom `ctrl+c` shortcut.', metadata.logfile)

    # Split the supplied package_name by ,
    # For example : 'sublime-text-3,atom' becomes ['sublime-text-3', 'atom']
    packages = package_name.strip(' ').split(',')

    if len(packages) > 1 and manifest:
        write('Cannot Install Multiple Packages From A Single Manifest. Make sure you install only 1 package at a time while specifying --manifest', 'bright_red', metadata)
        sys.exit()

    if not manifest:
        # Autocorrect all package names provided
        corrected_package_names = list(set(get_autocorrections(
            packages, get_correct_package_names(), metadata)))
    else:
        corrected_package_names = ['']

    # Write install headers to debug
    write_install_headers(metadata)

    # Handle multi-threaded installation (see function for further clarification)

    handle_multithreaded_installation(
        corrected_package_names, install_directory, metadata, force)

    # normal non-multi-threaded installation
    for package in corrected_package_names:
        configs = {
            'path': None,
            'reduce': None,
            'virus_check': None,
        }

        log_info('Handling Network Request...', metadata.logfile)
        status = 'Networking'
        write_verbose('Sending GET Request To /packages/', metadata)
        write_debug('Sending GET Request To /packages', metadata)
        log_info('Sending GET Request To /packages', metadata.logfile)
        log_info('Updating SuperCache', metadata.logfile)
        # request the json response of the package
        from json.decoder import JSONDecodeError

        if not manifest:
            res = send_req_package(package)
        else:
            try:
                f = open(manifest, 'r')
                try:
                    res = json.load(f)
                except JSONDecodeError as e:
                    print(
                        f'Invalid Manifest JSON Syntax : {Fore.LIGHTRED_EX}{e}{Fore.RESET}')
                    sys.exit()
                package = res['package-name']

            except FileNotFoundError:
                write(f'{manifest} Does Not Exist!', 'bright_red', metadata)
                write_verbose(f'{manifest} File Path Not Found!', metadata)
                write_debug(
                    f'{manifest} FileNotFoundError, Specified Manifest Cannot Be Found!', metadata)
                log_info(
                    f'{manifest} FileNotFoundError, Specified Manifest Cannot Be Found!', metadata.logfile)
                sys.exit(1)

        if not metadata.silent:
            if not metadata.no_color:
                print('SuperCached [', Fore.LIGHTCYAN_EX +
                      f'{res["display-name"]}' + Fore.RESET + ' ]')
            else:
                print(f'SuperCached [ {res["display-name"]} ]')

        log_info('Successfully Updated SuperCache', metadata.logfile)

        pkg = res
        log_info('Generating Packet For Further Installation.', metadata.logfile)

        version = get_package_version(
            pkg, res, version, portable, nightly, metadata)

        pkg = pkg[version]

        handle_portable_installation(version == 'portable', pkg, res, metadata)

        if 'install-override-command' in list(pkg.keys()):
            for operation in pkg['install-override-command']:
                if 'admin' in list(operation.keys()):
                    if operation['admin'] == True:
                        if not is_admin():
                            write('Installation Must Be Run As Administrator',
                                  'bright_red', metadata)
                            os._exit(1)

                if operation['type'] == 'python':
                    code = ''''''
                    for line in operation['code']:
                        code += line + '\n'
                    exec(code)

                elif operation['type'] == 'powershell' or operation['type'] == 'ps1':
                    with open(rf'{tempfile.gettempdir()}\electric\temp.ps1', 'w+') as f:
                        for line in operation['code']:
                            f.write(line + '\n')
                    os.system(
                        rf'powershell.exe -noprofile -File {tempfile.gettempdir()}\electric\temp.ps1')

                elif operation['type'] == 'batch' or operation['type'] == 'cmd':
                    with open(rf'{tempfile.gettempdir()}\electric\temp.bat', 'w+') as f:
                        for line in operation['code']:
                            f.write(line + '\n')
                    os.system(rf'{tempfile.gettempdir()}\electric\temp.bat')
            sys.exit()

        install_exit_codes = []
        uninstall_exit_codes = []
        if 'valid-install-exit-codes' in list(pkg.keys()):
            install_exit_codes = pkg['valid-install-exit-codes']

        if 'valid-uninstall-exit-codes' in list(pkg.keys()):
            uninstall_exit_codes = pkg['valid-uninstall-exit-codes']

        packet = Packet(
            pkg,
            package,
            res['display-name'],
            pkg['url'],
            pkg['file-type'],
            pkg['custom-location'],
            pkg['install-switches'],
            pkg['uninstall-switches'],
            install_directory,
            pkg['dependencies'],
            install_exit_codes,
            uninstall_exit_codes,
            version,
            pkg['run-test'] if 'run-test' in list(pkg.keys()) else False,
            pkg['set-env'] if 'set-env' in list(pkg.keys()) else None,
            pkg['default-install-dir'].replace('<appdata>', os.environ['APPDATA'].replace(
                '\\Roaming', '')) if 'default-install-dir' in list(pkg.keys()) else None,
            pkg['uninstall'] if 'uninstall' in list(pkg.keys()) else [],
            pkg['add-path'] if 'add-path' in list(pkg.keys()) else None,
            pkg['checksum'] if 'checksum' in list(pkg.keys()) else None,
            pkg['bin'] if 'bin' in list(pkg.keys()) else None,
            pkg['pre-update'] if 'pre-update' in list(pkg.keys()) else None,
        )

        write_verbose(
            f'Rapidquery Successfully Received {packet.json_name}.json', metadata)
        write_debug(
            f'Rapidquery Successfully Received {packet.json_name}.json', metadata)
        log_info(
            f'Rapidquery Successfully Received {packet.json_name}.json', metadata.logfile)

        handle_existing_installation(package, packet, force, metadata)

        if 'add-path' in list(pkg.keys()):
            if not is_admin():
                write('Installation Must Be Run As Administrator',
                      'bright_red', metadata)
                os._exit(1)

        if packet.dependencies:
            ThreadedInstaller.install_dependent_packages(
                packet, rate_limit, install_directory, metadata)

        write_verbose(
            f'Package to be installed: {packet.json_name}', metadata)
        log_info(
            f'Package to be installed: {packet.json_name}', metadata.logfile)

        write_verbose(
            f'Finding closest match to {packet.json_name}...', metadata)
        log_info(
            f'Finding closest match to {packet.json_name}...', metadata.logfile)

        write_verbose('Generating system download path...', metadata)
        log_info('Generating system download path...', metadata.logfile)

        download_url = packet.win64

        log_info(f'Recieved download path : {download_url}', metadata.logfile)
        log_info('Initializing Rapid Download...', metadata.logfile)

        # Downloading The File From Source
        write_debug(
            f'Downloading {packet.display_name} from => {packet.win64}', metadata)
        write_verbose(
            f"Downloading from '{download_url}'", metadata)
        log_info(f"Downloading from '{download_url}'", metadata.logfile)

        configs['path'] = download_installer(packet, download_url, metadata)

        log_info('Finished Rapid Download', metadata.logfile)

        log_info(
            f'Installing {packet.display_name} through Setup{packet.win64_type}', metadata.logfile)
        write_verbose('Creating registry start snapshot', metadata)
        log_info('Creating start snapshot of registry...', metadata.logfile)

        start_snap = get_environment_keys()

        write_verbose('Checking for pre install code', metadata)
        log_info('Checking for pre install code', metadata.logfile)

        if 'pre-install' in list(pkg.keys()):
            if isinstance(pkg['pre-install'], list):
                write_verbose('Executing Pre-Installation Code', metadata)
                log_info('Executing Pre-Installation Code', metadata.logfile)

                for proc in pkg['pre-install']:
                    if 'admin' in list(proc.keys()):
                        if proc['admin'] == True:
                            if not is_admin():
                                write(
                                    'Installation Must Be Run As Administrator', 'bright_red', metadata)
                                os._exit(1)

                    if proc['type'] == 'powershell':
                        with open(rf'{tempfile.gettempdir()}\electric\temp.ps1', 'w+') as f:
                            for line in proc['code']:
                                line = line.replace('<installer>', configs['path']).replace('<package-name>', packet.json_name).replace('<display-name>', packet.display_name).replace(
                                    '<version>', version).replace('<directory>', packet.directory if packet.directory != None else '').replace('<temp>', tempfile.gettempdir())
                                line += '\n'
                                f.write(line)

                        os.system(
                            rf'powershell.exe -File {tempfile.gettempdir()}\electric\temp.ps1')

                    if proc['type'] == 'cmd':
                        with open(rf'{tempfile.gettempdir()}\electric\temp.bat', 'w+') as f:
                            for line in proc['code']:
                                line = line.replace('<installer>', configs['path']).replace('<package-name>', packet.json_name).replace('<display-name>', packet.display_name).replace(
                                    '<version>', version).replace('<directory>', packet.directory).replace('<temp>', tempfile.gettempdir())
                                line += '\n'
                                f.write(line)

                        os.system(
                            rf'{tempfile.gettempdir()}\electric\temp.bat')

                    if proc['type'] == 'python':
                        ldict = {}
                        code = ''''''
                        for line in proc['code']:
                            add = line.replace('<installer>', configs['path']).replace('<temp>', tempfile.gettempdir()).replace('<package-name>', packet.json_name).replace(
                                '<display-name>', packet.display_name).replace('<directory>', packet.directory if packet.directory else '').replace('<version>', version) + '\n'

                            if f'{packet.win64_type}{packet.win64_type}' in add:
                                add = add.replace(
                                    f'{packet.win64_type}{packet.win64_type}', f'{packet.win64_type}')

                            code += add

                        exec(code, globals(), ldict)
                        for k in configs:
                            if k in ldict:
                                configs[k] = ldict[k]
                    if 'override' in list(proc.keys()):
                        if proc['override'] == True and len(corrected_package_names) == 1:
                            sys.exit()
                        elif len(corrected_package_names) > 1 and proc['override'] == True:
                            continue

        setup_name = configs['path']

        if not 'pre-install' in list(pkg.keys()) or packet.win64_type not in configs['path']:
            setup_name = configs['path'].split('\\')[-1] + packet.win64_type

        status = 'Installing'

        add_hotkey(
            'ctrl+c', lambda: handle_exit(status, setup_name, metadata))

        if f'{packet.win64_type}{packet.win64_type}' in configs['path']:
            configs['path'] = configs['path'].replace(
                f'{packet.win64_type}{packet.win64_type}', f'{packet.win64_type}')
        

        if packet.checksum and metadata.settings.checksum:
            verify_checksum(configs['path'], packet.checksum, metadata, newline = rate_limit != -1)

        if virus_check or metadata.settings.virus_check:
            log_info('Running requested virus scanning', metadata.logfile)
            if not metadata.silent:
                with Halo(text='Scanning File For Viruses ', text_color='cyan' if not metadata.no_color else 'white', color='green' if not metadata.no_color else 'white') as h:
                    check_virus(configs['path'], metadata, h)

        write_debug(
            f'Installing {packet.display_name} through Setup{packet.win64_type}', metadata)

        write(f'Installing {packet.display_name}',
              'bright_cyan', metadata)
        log_info(
            'Using Rapid Install To Complete Setup, Accept Prompts Asking For Admin Permission...', metadata.logfile)

        if not get_pid(setup_name):
            # Running The Installer silently And Completing Setup
            write_verbose(
                f'Running {packet.display_name} Installer at {configs["path"]}', metadata)
            log_info(
                f'Running {packet.display_name} Installer at {configs["path"]}', metadata.logfile)
            install_package(configs['path'], packet, metadata)
        else:
            disp_error_msg(get_error_message(
                '1618', 'install', packet.display_name, version, metadata, packet.json_name), metadata)

        log_info('Deregistering ctrl+c abort shortcut', metadata.logfile)
        write_verbose('Deregistering ctrl+c abort shortcut', metadata)
        remove_hotkey('ctrl+c')
        write_verbose('Checking for post install code', metadata)
        log_info('Checking for post install code', metadata.logfile)

        if 'post-install' in list(pkg.keys()):
            if isinstance(pkg['post-install'], list):
                for proc in pkg['post-install']:
                    if 'admin' in list(proc.keys()):
                        if proc['admin'] == True:
                            if not is_admin():
                                write(
                                    'Installation Must Be Run As Administrator', 'bright_red', metadata)
                                os._exit(1)
                    if proc['type'] == 'powershell':
                        with open(rf'{tempfile.gettempdir()}\electric\temp.ps1', 'w+') as f:
                            for line in proc['code']:
                                f.write(line.replace('<installer>', configs['path']).replace('<package-name>', packet.json_name).replace(
                                    '<display-name>', packet.display_name).replace('<version>', version).replace('<temp>', tempfile.gettempdir()) + '\n')

                        os.system(
                            rf'powershell.exe -File {tempfile.gettempdir()}\electric\temp.ps1')

                    if proc['type'] == 'cmd':
                        with open(rf'{tempfile.gettempdir()}\electric\temp.bat', 'w+') as f:
                            for line in proc['code']:
                                f.write(line.replace('<installer>', configs['path']).replace('<package-name>', packet.json_name).replace(
                                    '<display-name>', packet.display_name).replace('<version>', version).replace('<temp>', tempfile.gettempdir()) + '\n')

                        os.system(
                            rf'{tempfile.gettempdir()}\electric\temp.bat')

                    if proc['type'] == 'python':
                        ldict = {}
                        code = ''''''
                        for line in proc['code']:
                            code += line.replace('<installer>', configs['path']).replace('<temp>', tempfile.gettempdir()).replace(
                                '<package-name>', packet.json_name).replace('<display-name>', packet.display_name).replace('<version>', version) + '\n'
                        exec(code, globals())

        status = 'Installed'
        write_verbose('Creating registry end snapshot', metadata)
        log_info('Creating final snapshot of registry', metadata.logfile)
        changes_environment = False

        if packet.shim:
            changes_environment = True
            
            for shim in packet.shim:
                replace_install_dir = ''

                if packet.directory:
                    replace_install_dir = packet.directory

                elif packet.default_install_dir:
                    replace_install_dir = packet.default_install_dir

                shim = shim.replace('<install-directory>', replace_install_dir)
                shim_name = shim.split("\\")[-1].split('.')[0]
                write(f'Generating Shim For {shim_name}', 'cyan', metadata)

            generate_shim(shim, shim_name, shim.split('.')[-1])

        final_snap = get_environment_keys()

        if packet.add_path:
            replace_install_dir = ''

            if packet.directory:
                replace_install_dir = packet.directory

            elif packet.default_install_dir:
                replace_install_dir = packet.default_install_dir

            write(
                f'Appending "{packet.add_path.replace("<install-directory>", replace_install_dir)}" To PATH', 'bright_green', metadata)
            write_verbose(
                f'Appending "{packet.add_path.replace("<install-directory>", replace_install_dir)}" To PATH', metadata)
            log_info(
                f'Appending "{packet.add_path.replace("<install-directory>", replace_install_dir)}" To PATH', metadata.logfile)
            append_to_path(packet.add_path.replace(
                '<install-directory>', replace_install_dir))

        if packet.set_env:
            if isinstance(packet.set_env, list):
                for obj in packet.set_env:
                    name = obj['name']
                    replace_install_dir = ''

                    if packet.directory:
                        replace_install_dir = packet.directory

                    elif packet.default_install_dir:
                        replace_install_dir = packet.default_install_dir

                    write(
                        f'Setting Environment Variable {name}', 'bright_green', metadata)
                    write_verbose(
                        f'Setting Environment Variable {name} to {obj["value"].replace("<install-directory>", replace_install_dir)}', metadata)
                    log_info(
                        f'Setting Environment Variable {name} to {obj["value"].replace("<install-directory>", replace_install_dir)}', metadata.logfile)

                    set_environment_variable(
                        name, obj['value'].replace('<install-directory>', replace_install_dir))

            else:
                name = packet.set_env['name']
                replace_install_dir = ''

                if packet.directory:
                    replace_install_dir = packet.directory

                elif packet.default_install_dir:
                    replace_install_dir = packet.default_install_dir

                write(
                    f'Setting Environment Variable {name}', 'bright_green', metadata)
                write_verbose(
                    f'Setting Environment Variable {name} to {packet.set_env["value"].replace("<install-directory>", replace_install_dir)}', metadata)
                log_info(
                    f'Setting Environment Variable {name} to {packet.set_env["value"].replace("<install-directory>", replace_install_dir)}', metadata.logfile)

                set_environment_variable(
                    name, packet.set_env['value'].replace('<install-directory>', replace_install_dir))

        if final_snap.env_length > start_snap.env_length or final_snap.sys_length > start_snap.sys_length or changes_environment:

            write('The PATH environment variable has changed. Run `refreshenv` to refresh your environment variables.',
                  'bright_green', metadata)


        if metadata.reduce_package:
            write_verbose(
                f'Deleting installer files at {tempfile.gettempdir()}', metadata)
            log_info(
                f'Deleting installer files at {tempfile.gettempdir()}', metadata.logfile)
            write_debug(
                f'Deleting installer files at {tempfile.gettempdir()}. Path : ({configs["path"]}{packet.win64_type})', metadata)
            try:
                os.remove(f'{configs["path"]}')
                os.remove(
                    Rf'{tempfile.gettempdir()}\electric\downloadcache.pickle')
                os.remove(
                    Rf'{tempfile.gettempdir()}\electric\unfinishedcache.pickle')
            except FileNotFoundError:
                pass

            log_info(
                'Successfully Cleaned Up Installer From Temporary Directory And DownloadCache', metadata.logfile)
            write('Successfully Cleaned Up Installer From Temp Directory',
                  'bright_green', metadata)


        if not packet.run_test:
            write_verbose(f'Running tests for {packet.display_name}', metadata)

            write_debug(
                f'No Pre-Defined Tests found for {packet.display_name}', metadata)
            log_info(
                f'No Pre-Defined Tests found for {packet.display_name}', metadata.logfile)

            write(
                f'Running Tests For {packet.display_name}', 'bright_white', metadata)

            write_debug(
                f'All Pre-Defined checks for {packet.display_name} passed. Registering successful package installation', metadata)
            write_verbose(
                f'All Pre-Defined checks for {packet.display_name} passed', metadata)
            log_info(
                f'All Pre-Defined checks for {packet.display_name} passed', metadata.logfile)
            if not metadata.no_color:
                write(f'[{Fore.LIGHTGREEN_EX} OK {Fore.RESET}] Pre-Defined Checks',
                      'bright_white', metadata)
            else:
                write(f'[ OK ] Pre-Defined Checks', 'bright_white', metadata)
            register_package_success(packet, install_directory, metadata)

            write(
                f'Successfully Installed {packet.display_name}', 'bright_magenta', metadata)

            log_info(
                f'Successfully Installed {packet.display_name}', metadata.logfile)
        else:
            write_verbose(f'Running tests for {packet.display_name}', metadata)
            write_debug(
                f'Pre-Defined Checks found for {packet.display_name}', metadata)
            log_info(
                f'Running pre-defined checks found for {packet.display_name}', metadata.logfile)
            write(
                f'Running Tests For {packet.display_name}', 'bright_white', metadata)
            if find_existing_installation(packet.json_name, packet.display_name):
                if not metadata.no_color:
                    write(
                        f'[ {Fore.LIGHTGREEN_EX}OK{Fore.RESET} ]  Registry Check', 'bright_white', metadata)
                else:
                    write(f'[ OK ] Registry Check', 'bright_white', metadata)

                write_debug(
                    'Passed Registry Check. Registering Package Success', metadata)
                register_package_success(packet, install_directory, metadata)
                write(
                    f'Successfully Installed {packet.display_name}', 'bright_magenta', metadata)
                log_info(
                    f'Successfully Installed {packet.display_name}', metadata.logfile)
            else:
                write(
                    f'[ {Fore.LIGHTRED_EX}ERROR{Fore.RESET} ] Registry Check', 'bright_white', metadata)
                write('Retrying Registry Check In 5 seconds',
                      'bright_yellow', metadata)
                tm.sleep(5)
                if find_existing_installation(packet.json_name, packet.display_name):
                    write(
                        f'[ {Fore.LIGHTGREEN_EX}OK{Fore.RESET} ]  Registry Check', 'bright_white', metadata)
                    register_package_success(
                        packet, install_directory, metadata)
                    write(
                        f'Successfully Installed {packet.display_name}', 'bright_magenta', metadata)
                    log_info(
                        f'Successfully Installed {packet.display_name}', metadata.logfile)
                else:
                    write(
                        f'[ {Fore.LIGHTRED_EX}ERROR{Fore.RESET} ] Registry Check', 'bright_white', metadata)
                    write(
                        f'Failed To Install {packet.display_name}', 'bright_red', metadata)
                sys.exit()

        
        version = ''
        display_support(metadata)
        write_verbose(
            'Installation and setup completed with exit code 0', metadata)
        write_verbose('Terminating verbose logger', metadata)
        log_info('Installation and setup completed.', metadata.logfile)
        write_debug(
            f'Terminated debugger at {strftime("%H:%M:%S")} on install::completion', metadata)
        log_info(
            f'Terminated debugger at {strftime("%H:%M:%S")} on install::completion', metadata.logfile)
        close_log(metadata.logfile, 'Install')


@cli.command(aliases=['upgrade', 'update'], context_settings=CONTEXT_SETTINGS)
@click.argument('package_name', required=True)
@click.option('--no-progress', '-np', is_flag=True, default=False, help='Disable progress bar for bundle installation')
@click.option('--no-color', '-nc', is_flag=True, help='Disable colored output for bundle installation')
@click.option('--verbose', '-vb', is_flag=True, help='Enable verbose mode for installation')
@click.option('--log-output', '-l', 'logfile', help='Log output to the specified file')
@click.option('--debug', '-d', is_flag=True, help='Enable debug mode for installation')
@click.option('--silent', '-s', is_flag=True, help='Completely silent uninstallation without any output to console')
@click.option('--virus-check', '-vc', is_flag=True, help='Check for virus before bundle installation')
@click.option('--rate-limit', '-rl', type=int, default=-1)
@click.option('-y', '--yes', is_flag=True, help='Accept all prompts during uninstallation')
@click.option('--reduce', '-rd', is_flag=True, help='Cleanup all traces of package after bundle installation')
@click.option('--local', '-ll', is_flag=True, help='')
@click.option('--portable', '-p', is_flag=True, help='')
@click.pass_context
def up(
    ctx,
    package_name: str,
    verbose: bool,
    debug: bool,
    no_color: bool,
    logfile: str,
    yes: bool,
    silent: bool,
    no_progress: bool,
    rate_limit: int,
    reduce: bool,
    virus_check: bool,
    local: bool,
    portable: bool,
):
    """
    Updates an existing package
    """
    from zip_update import update_portable
    
    update_package_list()
    if package_name == 'electric' or package_name == 'self':
        sys.exit()

    if package_name == 'all':
        installed_packages = [f.replace('.json', '') for f in os.listdir(
            PathManager.get_appdata_directory() + r'\Current')]
        for package in installed_packages:
            # print(package.split('@')[0])
            ctx.invoke(
                up,
                package_name=package.split('@')[0],
                verbose=verbose,
                debug=debug,
                no_color=no_color,
                logfile=logfile,
                yes=yes,
                silent=silent,
                no_progress=no_progress,
                rate_limit=rate_limit,
                reduce=reduce,
                virus_check=virus_check,
                local=local if local else False
            )
        sys.exit()

    metadata = generate_metadata(
        None, None, None, None, None, None, None, None, None, None, Setting.new(), None)

    log_info('Setting up custom `ctrl+c` shortcut.', metadata.logfile)
    status = 'Initializing'
    setup_name = ''
    add_hotkey(
        'ctrl+c', lambda: handle_exit(status, setup_name, metadata))

    packages = package_name.strip(' ').split(',')

    corrected_package_names = get_autocorrections(
        packages, get_correct_package_names(), metadata)
    corrected_package_names = list(set(corrected_package_names))

    write_install_headers(metadata)

    for package in corrected_package_names:
        spinner = halo.Halo(color='grey', text='Finding Packages')
        spinner.start()
        log_info('Handling Network Request...', metadata.logfile)
        status = 'Networking'
        write_verbose('Sending GET Request To /packages/', metadata)
        write_debug('Sending GET Request To /packages', metadata)
        log_info('Sending GET Request To /packages', metadata.logfile)
        log_info('Updating SuperCache', metadata.logfile)
        res = send_req_package(package)
        log_info('Successfully Updated SuperCache', metadata.logfile)
        spinner.stop()
        pkg = res
        if portable:
            pkg = pkg['portable']
            keys = list(pkg[pkg['latest-version']].keys())
            data = {
                'display-name': res['display-name'],
                'package-name': res['package-name'],
                'latest-version': res['latest-version'],
                'url': pkg[pkg['latest-version']]['url'],
                'file-type': pkg[pkg['latest-version']]['file-type'] if 'file-type' in keys else None,
                'extract-dir': pkg[pkg['latest-version']]['extract-dir'],
                'chdir': pkg[pkg['latest-version']]['chdir'] if 'chdir' in keys else [],
                'bin': pkg[pkg['latest-version']]['bin'] if 'bin' in keys else [],
                'shortcuts': pkg[pkg['latest-version']]['shortcuts'] if 'shortcuts' in keys else [],
                'pre-install': pkg[pkg['latest-version']]['pre-install'] if 'pre-install' in keys else [],
                'post-install': pkg[pkg['latest-version']]['post-install'] if 'post-install' in keys else [],
                'install-notes': pkg[pkg['latest-version']]['install-notes'] if 'install-notes' in keys else None,
                'uninstall-notes': pkg[pkg['latest-version']]['uninstall-notes'] if 'uninstall-notes' in keys else None,
                'set-env': pkg[pkg['latest-version']]['set-env'] if 'set-env' in keys else None,
                'persist': pkg[pkg['latest-version']]['persist'] if 'persist' in keys else None,
                'checksum': pkg[pkg['latest-version']]['checksum'] if 'checksum' in keys else None,
                'dependencies': pkg[pkg['latest-version']]['dependencies'] if 'dependencies' in keys else None,
            }
            packet = PortablePacket(data)
            update_portable(ctx, packet, metadata)


        pkg = res
        pkg = pkg[pkg['latest-version']]

        packet = Packet(
            pkg,
            package,
            res['display-name'],
            pkg['url'],
            pkg['file-type'],
            pkg['custom-location'],
            pkg['install-switches'],
            pkg['uninstall-switches'],
            None,
            pkg['dependencies'],
            None,
            [],
            res['latest-version'],
            pkg['run-check'] if 'run-check' in list(res.keys()) else True,
            pkg['set-env'] if 'set-env' in list(pkg.keys()) else None,
            pkg['default-install-dir'].replace('<appdata>', os.environ['APPDATA'].replace(
                '\\Roaming', '')) if 'default-install-dir' in list(pkg.keys()) else None,
            pkg['uninstall'] if 'uninstall' in list(pkg.keys()) else [],
            pkg['add-path'] if 'add-path' in list(pkg.keys()) else None,
            pkg['checksum'] if 'checksum' in list(pkg.keys()) else None,
            pkg['bin'] if 'bin' in list(pkg.keys()) else None,
            pkg['pre-update'] if 'pre-update' in list(pkg.keys()) else None,
        )

        
        log_info('Generating Packet For Further Installation.', metadata.logfile)
        installed_packages_dict = [{f.split('@')[0]: f.split('@')[1]} for f in os.listdir(
            PathManager.get_appdata_directory() + r'\Current')]
        installed_packages = []
        
        for f in os.listdir(PathManager.get_appdata_directory() + r'\Current'):
            installed_packages.append(f.split('@')[0])

        idx = 0
        if package in installed_packages:
            if check_newer_version(package, packet, installed_packages_dict):
                install_dir = PathManager.get_appdata_directory() + r'\Current'
                dictionary = installed_packages_dict[idx]
                package_name = list(dictionary.keys())[0]

                version = ''

                for package in installed_packages_dict:
                    if list(package.keys())[0] == package_name:
                        version = package[list(package.keys())[
                            0]].replace('.json', '')

                with open(rf'{install_dir}\{package_name}@{version}.json', 'r') as f:
                    data = json.load(f)

                installed_version = data['version']
                if not yes:
                    if not local:
                        continue_update = confirm(
                            f'{package_name} would be updated from version {installed_version} to {packet.version}')
                    else:
                        write(
                            rf'There is a newer version of {packet.display_name} Availiable ({installed_version}) => ({packet.version})', 'bright_yellow', metadata)
                        sys.exit()
                else:
                    continue_update = True


                if packet.pre_update:
                    if isinstance(packet.pre_update, list):
                        write_verbose('Executing Pre-Update Code', metadata)
                        log_info('Executing Pre-Update Code', metadata.logfile)

                        for proc in packet.pre_update:
                            if 'admin' in list(proc.keys()):
                                if proc['admin'] == True:
                                    if not is_admin():
                                        write(
                                            'Installation Must Be Run As Administrator', 'bright_red', metadata)
                                        os._exit(1)

                            if proc['type'] == 'powershell':
                                with open(rf'{tempfile.gettempdir()}\electric\temp.ps1', 'w+') as f:
                                    for line in proc['code']:
                                        line = line.replace('<package-name>', packet.json_name).replace('<display-name>', packet.display_name).replace(
                                            '<version>', version).replace('<directory>', packet.directory if packet.directory != None else '').replace('<temp>', tempfile.gettempdir())
                                        line += '\n'
                                        f.write(line)

                                os.system(
                                    rf'powershell.exe -File {tempfile.gettempdir()}\electric\temp.ps1')

                            if proc['type'] == 'cmd':
                                with open(rf'{tempfile.gettempdir()}\electric\temp.bat', 'w+') as f:
                                    for line in proc['code']:
                                        line = line.replace('<package-name>', packet.json_name).replace('<display-name>', packet.display_name).replace(
                                            '<version>', version).replace('<directory>', packet.directory).replace('<temp>', tempfile.gettempdir())
                                        line += '\n'
                                        f.write(line)

                                os.system(
                                    rf'{tempfile.gettempdir()}\electric\temp.bat')

                            if proc['type'] == 'python':
                                code = ''''''
                                for line in proc['code']:
                                    add = line.replace('<temp>', tempfile.gettempdir()).replace('<package-name>', packet.json_name).replace(
                                        '<display-name>', packet.display_name).replace('<directory>', packet.directory if packet.directory else '').replace('<version>', version) + '\n'

                                    if f'{packet.win64_type}{packet.win64_type}' in add:
                                        add = add.replace(
                                            f'{packet.win64_type}{packet.win64_type}', f'{packet.win64_type}')

                                    code += add

                                exec(code)
                
                if continue_update:
                    ctx.invoke(
                        uninstall,
                        package_name=package,
                        verbose=verbose,
                        debug=debug,
                        no_color=no_color,
                        logfile=logfile,
                        yes=yes,
                        silent=silent,
                        python=None,
                    )
                    ctx.invoke(
                        install,
                        package_name=package,
                        verbose=verbose,
                        debug=debug,
                        no_progress=no_progress,
                        no_color=no_color,
                        logfile=logfile,
                        virus_check=virus_check,
                        yes=yes,
                        silent=silent,
                        python=None,
                        node=None,
                        reduce=reduce,
                        rate_limit=rate_limit
                    )
                    write(
                        f'Successfully Updated {package} to latest version.', 'bright_green', metadata)

                    index += 1
                else:
                    handle_exit('Error', '', metadata)

            else:
                print(f'{packet.display_name} Is Already On The Latest Version')
        else:
            write(f'{packet.display_name} Is Not Installed',
                  'bright_red', metadata)


@cli.command(aliases=['remove', 'u'], context_settings=CONTEXT_SETTINGS)
@click.argument('package_name', required=False, default='test')
@click.option('--manifest', '-m', 'manifest', help='Read from a manifest file instead of querying from the community repository')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose mode for uninstallation')
@click.option('--debug', '-d', is_flag=True, help='Enable debug mode for uninstallation')
@click.option('--no-color', '-nc', is_flag=True, help='Disable colored output for uninstallation')
@click.option('--log-output', '-l', 'logfile', help='Log output to the specified file')
@click.option('-y', '--yes', is_flag=True, help='Accept all prompts during uninstallation')
@click.option('--silent', '-s', is_flag=True, help='Completely silent uninstallation without any output to console')
@click.option('--python', '-py', is_flag=True, help='Specify a Python package to uninstall')
@click.option('--atom', '-ato', is_flag=True, help='Specify an Atom extension to uninstall')
@click.option('--vscode', '-vs', is_flag=True, help='Specify a Visual Studio Code extension to uninstall')
@click.option('--nightly', '--pre-release', is_flag=True, help='Specify a Visual Studio Code extension to uninstall')
@click.option('--node', '-npm', is_flag=True, help='Specify a Python package to uninstall')
@click.option('--portable', '--non-admin', '-p', is_flag=True, help='Uninstall a portable version of a package')
@click.option('--plugin', '-pg', is_flag=True, help='Uninstall a plugin of a package')
@click.option('--configuration', '-cf', is_flag=True, help='Specify a config file to uninstall')
@click.option('--ae', is_flag=True)
@click.option('--skp', is_flag=True)
@click.pass_context
def uninstall(
    ctx,
    package_name: str,
    verbose: bool,
    debug: bool,
    no_color: bool,
    logfile: str,
    yes: bool,
    silent: bool,
    python: bool,
    vscode: bool,
    node: bool,
    atom: bool,
    plugin: bool,
    configuration: bool,
    portable: bool,
    ae: bool,
    nightly: bool,
    skp: bool,
    manifest: str
):
    """
    Uninstall a package or a list of packages.
    """
    
    from timeit import default_timer as timer

    if not manifest and package_name == 'test':
        print(f'{Fore.LIGHTRED_EX}A Package Name Must Be Supplied\nUsage: electric uninstall <package-name>\n\nExamples:\nelectric uninstall {Fore.LIGHTGREEN_EX}sublime-text-3{Fore.RESET}\n{Fore.LIGHTRED_EX}electric uninstall {Fore.LIGHTGREEN_EX}sublime-text-3,notepad++{Fore.RESET}')
        sys.exit()

    start_log()
    if configuration:
        ctx.invoke(
            config,
            config_path=package_name,
            remove=True,
            verbose=verbose,
            debug=debug,
            no_progress=None,
            logfile=logfile,
            install_directory=None,
            virus_check=None,
            yes=yes,
            silent=silent,
            sync=None,
            reduce=None,
            rate_limit=None
        )
        sys.exit()

    if logfile:
        logfile = logfile.replace('.txt', '.log')
        from logging import INFO
        create_config(logfile, INFO, 'Install')
    
    log_info('Generating metadata...', logfile)
    
    metadata = generate_metadata(
        None, silent, verbose, debug, no_color, yes, logfile, None, None, None, Setting.new(), None)

    if plugin:
        handle_plugin_uninstallation(package_name, metadata)

    log_info('Successfully generated metadata.', logfile)

    log_info('Checking if supercache exists...', metadata.logfile)

    handle_external_uninstallation(python, node, vscode, False, atom, package_name, metadata)

    log_info('Setting up custom `ctrl+c` shortcut.', metadata.logfile)
    
    status = 'Initializing'
    setup_name = ''
    add_hotkey(
        'ctrl+c', lambda: handle_exit(status, setup_name, metadata))

    packages = package_name.split(',')

    if len(packages) > 1 and manifest:
        write('Cannot Install Multiple Packages From A Single Manifest. Make sure you install only 1 package at a time while specifying --manifest', 'bright_red', metadata)
        sys.exit()

    if not manifest:
        corrected_package_names = get_autocorrections(
            packages, get_correct_package_names(), metadata)
        corrected_package_names = list(set(corrected_package_names))
    else:
        corrected_package_names = ['']

    write_uninstall_headers(metadata)

    index = 0

    for package in corrected_package_names:
        installed_packages = [''.join(f.replace('.json', '').split(
            '@')[:1]) for f in os.listdir(PathManager.get_appdata_directory() + r'\Current')]
        portable_installed_packages = [''.join(
            f.split('@')[:1]) for f in os.listdir(os.path.expanduser('~') + r'\electric')]
        installed_packages += portable_installed_packages

        from json.decoder import JSONDecodeError
        if not manifest:
            res = send_req_package(package)
        else:
            try:
                f = open(manifest, 'r')
                try:
                    res = json.load(f)
                except JSONDecodeError as e:
                    print('Invalid Manifest JSON Syntax : ', e.msg)
                    sys.exit()

                package = res['package-name']

            except FileNotFoundError:
                write(f'{manifest} Does Not Exist!', 'bright_red', metadata)
                write_verbose(f'{manifest} File Path Not Found!', metadata)
                write_debug(
                    f'{manifest} FileNotFoundError, Specified Manifest Cannot Be Found!', metadata)
                log_info(
                    f'{manifest} FileNotFoundError, Specified Manifest Cannot Be Found!', metadata.logfile)
                sys.exit(1)

        if not metadata.no_color:
            write(
                f'SuperCached [ {Fore.LIGHTCYAN_EX}{res["display-name"]}{Fore.RESET} ]', 'bright_white', metadata)
        else:
            write(f'SuperCached [ {res["display-name"]} ]', 'bright_white', metadata)

        if 'is-portable' in list(res.keys()):
            if res['is-portable'] == True:
                portable = True

        if portable:
            version = 'portable'
        else:
            version = res['latest-version']
        pkg = res[version]
        
        if 'uninstall-override-command' in list(pkg.keys()):
            for operation in pkg['uninstall-override-command']:
                if 'admin' in list(operation.keys()):
                    if operation['admin'] == True:
                        if not is_admin():
                            write(
                                'Uninstallation Must Be Run As Administrator', 'bright_red', metadata)
                            os._exit(1)

                if operation['type'] == 'python':
                    code = ''''''
                    for line in operation['code']:
                        code += line.replace('<display-name>', res['display-name']).replace(
                            '<package-name>', res['package-name']).replace('<version>', version) + '\n'
                    exec(code)

                elif operation['type'] == 'powershell' or operation['type'] == 'ps1':
                    with open(rf'{tempfile.gettempdir()}\electric\temp.ps1', 'w+') as f:
                        for line in operation['code']:
                            f.write(line + '\n')
                    os.system(
                        rf'powershell.exe -noprofile -File {tempfile.gettempdir()}\electric\temp.ps1')

                elif operation['type'] == 'batch' or operation['type'] == 'cmd':
                    with open(rf'{tempfile.gettempdir()}\electric\temp.bat', 'w+') as f:
                        for line in operation['code']:
                            f.write(line + '\n')
                    os.system(rf'{tempfile.gettempdir()}\electric\temp.bat')
            sys.exit()

        # If the package is not installed, let the user know
        if not skp:
            if package not in installed_packages:
                pkg = res
                if 'is-portable' in list(pkg.keys()):
                    if pkg['is-portable'] == True:
                        portable = True

                if portable:
                    version = 'portable'
                else:
                    version = pkg['latest-version']

                uninstall_exit_codes = []
                if 'valid-uninstall-exit-codes' in list(pkg.keys()):
                    uninstall_exit_codes = pkg['valid-install-exit-codes']

                pkg = pkg[version]
                display_name = res['display-name']
                write(
                    f'Could not find any existing installations of {display_name}', 'bright_red', metadata)
                try:
                    os.remove(
                        rf'{PathManager.get_appdata_directory()}\Current\{package}@{packet.version}.json')
                except:
                    pass
                close_log(metadata.logfile, 'Uninstall')
                continue

        # Continue with normal installation because the package has not been installed yet
        pkg = res
        if 'is-portable' in list(pkg.keys()):
            if pkg['is-portable'] == True:
                portable = True

        if portable:
            version = 'portable'
        else:
            version = pkg['latest-version']

        name = pkg['display-name']
        pkg = pkg[version]
        #
        override_uninstall_switches = pkg['override-default-uninstall-switches'] if 'override-default-uninstall-switches' in list(
            pkg.keys()) else False
        log_info('Generating Packet For Further Installation.', metadata.logfile)

        handle_portable_uninstallation(
            version == 'portable', res, pkg, metadata)

        install_exit_codes = []
        uninstall_exit_codes = []

        if 'valid-install-exit-codes' in list(pkg.keys()):
            install_exit_codes = pkg['valid-install-exit-codes']

        if 'valid-uninstall-exit-codes' in list(pkg.keys()):
            uninstall_exit_codes = pkg['valid-uninstall-exit-codes']

        packet = Packet(
            pkg,
            package,
            name,
            pkg['url'],
            pkg['file-type'],
            pkg['custom-location'],
            pkg['install-switches'],
            pkg['uninstall-switches'],
            None,
            pkg['dependencies'],
            install_exit_codes,
            uninstall_exit_codes,
            version,
            pkg['run-check'] if 'run-check' in list(pkg.keys()) else False,
            pkg['set-env'] if 'set-env' in list(pkg.keys()) else None,
            pkg['default-install-dir'].replace('<appdata>', os.environ['APPDATA'].replace(
                '\\Roaming', '')) if 'default-install-dir' in list(pkg.keys()) else None,
            pkg['uninstall'] if 'uninstall' in list(pkg.keys()) else [],
            pkg['add-path'] if 'add-path' in list(pkg.keys()) else None,
            pkg['checksum'] if 'checksum' in list(pkg.keys()) else None,
            pkg['bin'] if 'bin' in list(pkg.keys()) else None,
            pkg['pre-update'] if 'pre-update' in list(pkg.keys()) else None,
        )


        proc = None
        ftp = ['.msix', '.msixbundle', '.appxbundle', '.appx']

        if packet.dependencies:
            handle_uninstall_dependencies(packet, metadata)

        if packet.win64_type in ftp:
            if find_msix_installation(pkg['uninstall-bundle-identifier']):
                if uninstall_msix(pkg['uninstall-bundle-identifier']) == 0:
                    write(
                        f'Successfully Uninstalled {packet.display_name}', 'bright_green', metadata)
                    close_log(metadata.logfile, 'Uninstall')
                    sys.exit()

        add_hotkey(
            'ctrl+c', lambda: kill_proc(proc, metadata))

        log_info(
            f'Rapidquery Successfully Received {packet.json_name}.json', metadata.logfile)

        # Getting UninstallString or QuietUninstallString From The Registry Search Algorithm
        write_verbose(
            'Fetching uninstall key from the registry...', metadata)
        write_debug('Sending query (uninstall-string) to Registry', metadata)
        log_info('Fetching uninstall key from the registry...', metadata.logfile)

        start = timer()
        key = get_uninstall_key(packet.json_name, packet.display_name)
        end = timer()


        if not key:
            log_info(
                f'electric didn\'t detect any existing installations of => {packet.display_name}', metadata.logfile)

            pkg = res
            version = pkg['latest-version']
            name = pkg['display-name']
            pkg = pkg[version]
            log_info('Generating Packet For Further Installation.',
                     metadata.logfile)

            uninstall_exit_codes = []

            packet = Packet(
                pkg,
                package,
                name,
                pkg['url'],
                pkg['file-type'],
                pkg['custom-location'],
                pkg['install-switches'],
                pkg['uninstall-switches'],
                None,
                pkg['dependencies'],
                None,
                uninstall_exit_codes,
                version,
                pkg['run-check'] if 'run-check' in list(res.keys()) else True,
                pkg['set-env'] if 'set-env' in list(pkg.keys()) else None,
                pkg['default-install-dir'].replace('<appdata>', os.environ['APPDATA'].replace(
                    '\\Roaming', '')) if 'default-install-dir' in list(pkg.keys()) else None,
                pkg['uninstall'] if 'uninstall' in list(pkg.keys()) else [],
                pkg['add-path'] if 'add-path' in list(pkg.keys()) else None,
                pkg['checksum'] if 'checksum' in list(pkg.keys()) else None,
                pkg['bin'] if 'bin' in list(pkg.keys()) else None,
                pkg['pre-update'] if 'pre-update' in list(pkg.keys()) else None,
            )


            write(
                f'Could not find any existing installations of {packet.display_name}', 'bright_red', metadata)
            try:
                os.remove(
                    rf'{PathManager.get_appdata_directory()}\Current\{package}@{packet.version}.json')
            except:
                pass
            close_log(metadata.logfile, 'Uninstall')
            index += 1
            continue

        kill_running_proc(packet.json_name, packet.display_name, metadata)

        if not ae:
            write_verbose('Uninstall key found.', metadata)
            log_info('Uninstall key found.', metadata.logfile)
            log_info(key, metadata.logfile)
            write_debug(
                'Successfully Recieved UninstallString from Windows Registry', metadata)

            write(
                f'Successfully Retrieved Uninstall Key In {round(end - start, 4)}s', 'bright_green', metadata)
            log_info(
                f'Successfully Retrieved Uninstall Key In {round(end - start, 4)}s', metadata.logfile)

        command = ''

        # Key Can Be A List Or A Dictionary Based On Results

        if isinstance(key, list):
            if key:
                key = key[0]

        if not metadata.no_color:
            write(
                f'{Fore.LIGHTCYAN_EX}Uninstalling {packet.display_name}{Fore.RESET}', 'bright_white', metadata)
        else:
            write(
                f'Uninstalling {packet.display_name}', 'bright_white', metadata)

        if 'QuietUninstallString' in key:

            command = key['QuietUninstallString']
            if command.startswith("msiexec.exe") or command.startswith("MSIEXEC.EXE"):
                command = command.replace('/I', '/X')
                command = command.replace('/quiet', '/qn')

            if override_uninstall_switches:
                if '--' in command:
                    command = command.split('--')[0:1][0].strip()
                if '/' in command:
                    command = command.split('/')[0:1][0].strip()
            
            additional_switches = None
            if packet.uninstall_switches:
                if packet.uninstall_switches != []:
                    write_verbose(
                        'Adding additional uninstall switches', metadata)
                    write_debug(
                        'Appending additional uninstallation switches', metadata)
                    log_info('Adding additional uninstall switches',
                             metadata.logfile)
                    additional_switches = packet.uninstall_switches

            if additional_switches:
                for switch in additional_switches:
                    command += ' ' + switch

            write_verbose('Executing the quiet uninstall command', metadata)
            log_info(
                f'Executing the quiet uninstall command => {command}', metadata.logfile)
            write_debug('Running silent uninstallation command', metadata)
            run_test = run_cmd(command, metadata, 'uninstallation', packet)

            if not packet.run_test:
                packet.run_test = run_test

            if packet.set_env:
                if isinstance(packet.set_env, list):
                    for obj in packet.set_env:
                        delete_environment_variable(obj['name'])
                
                else:
                    delete_environment_variable(packet.set_env['name'])

            if packet.shim:
                home = os.path.expanduser('~')

                for shim in packet.shim:
                    replace_install_dir = ''

                    if packet.directory:
                        replace_install_dir = packet.directory

                    elif packet.default_install_dir:
                        replace_install_dir = packet.default_install_dir

                    shim = shim.replace(
                        '<install-directory>', replace_install_dir)
                    shim_name = shim.split("\\")[-1].split('.')[0]
                    write(
                        f'Deleting Shims For {packet.display_name}', 'cyan', metadata)
                    try:
                        os.remove(
                            f'{home}\\electric\\shims\\{shim_name.split(".")[0]}.bat')
                    except:
                        pass


            write_verbose('Uninstallation completed.', metadata)
            log_info('Uninstallation completed.', metadata.logfile)

            index += 1

        # If Only UninstallString Exists (Not Preferable)
        elif 'UninstallString' in key:
            command = key['UninstallString']
            command = command.replace('/I', '/X')
            if 'msiexec.exe' in command.lower():
                command += ' /quiet'
            # command = f'"{command}"'
            if override_uninstall_switches:
                if '--' in command:
                    command = command.split('--')[0:1][0].strip()
                if '/' in command:
                    command = command.split('/')[0:1][0].strip()

            if not 'msiexec.exe' in command.lower():
                for switch in packet.uninstall_switches:
                    command += f' {switch}'

            # Run The UninstallString
            write_verbose('Executing the Uninstall Command', metadata)
            log_info('Executing the silent Uninstall Command', metadata.logfile)

            run_test = run_cmd(command, metadata, 'uninstallation', packet)

            if not packet.run_test:
                packet.run_test = run_test

            write_verbose('Uninstallation completed.', metadata)
            log_info('Uninstallation completed.', metadata.logfile)
            index += 1

            if packet.set_env:
                if isinstance(packet.set_env, list):
                    for obj in packet.set_env:
                        delete_environment_variable(obj['name'])
                
                else:
                    delete_environment_variable(packet.set_env['name'])

            if packet.shim:
                home = os.path.expanduser('~')

                for shim in packet.shim:
                    replace_install_dir = ''

                    if packet.directory:
                        replace_install_dir = packet.directory

                    elif packet.default_install_dir:
                        replace_install_dir = packet.default_install_dir

                    shim = shim.replace(
                        '<install-directory>', replace_install_dir)
                    shim_name = shim.split("\\")[-1].split('.')[0]
                    write(
                        f'Deleting Shims For {packet.display_name}', 'cyan', metadata)
                    try:
                        os.remove(
                            f'{home}\\electric\\shims\\{shim_name.split(".")[0]}.bat')
                    except:
                        pass


        if packet.uninstall:
            for pkg in packet.uninstall:
                ctx.invoke(
                    uninstall,
                    package_name=pkg,
                    verbose=metadata.verbose,
                    debug=metadata.debug,
                    no_color=metadata.no_color,
                    logfile=metadata.logfile,
                    yes=metadata.yes,
                    silent=metadata.silent,
                    python=False,
                    vscode=False,
                    node=False,
                    atom=False,
                    configuration=False,
                    portable=False,
                    ae=False,
                    nightly=nightly,
                    skp=True
                )

        if packet.run_test:
            write(
                f'Running Tests For {packet.display_name}', 'bright_white', metadata)
            if not find_existing_installation(packet.json_name, packet.display_name):
                if nightly:
                    os.remove(
                        rf'{PathManager.get_appdata_directory()}\Current\{package}@nightly.json')
                else:
                    os.remove(
                        rf'{PathManager.get_appdata_directory()}\Current\{package}@{packet.version}.json')
                if not metadata.no_color:
                    write(f'[ {Fore.LIGHTGREEN_EX}OK{Fore.RESET} ] Registry Check', 'bright_white', metadata)
                else:
                    write(f'[ OK ] Registry Check', 'bright_white', metadata)

                write(
                    f'Successfully Uninstalled {packet.display_name}', 'bright_magenta', metadata)
            else:
                print(f'[ {Fore.LIGHTRED_EX}ERROR{Fore.RESET} ] Registry Check')
                write(f'Failed: Registry Check', 'bright_red', metadata)
                write('Retrying Registry Check In 7.5 seconds',
                      'bright_yellow', metadata)
                tm.sleep(7.5)
                if not find_existing_installation(packet.json_name, packet.display_name):
                    write(
                        f'[ {Fore.LIGHTGREEN_EX}OK{Fore.RESET} ]  Registry Check', 'bright_white', metadata)
                    os.remove(
                        rf'{PathManager.get_appdata_directory()}\Current\{package}@{packet.version}.json')
                    write(
                        f'Successfully Uninstalled {packet.display_name}', 'bright_magenta', metadata)
                    log_info(
                        f'Successfully Uninstalled {packet.display_name}', metadata.logfile)
                    write_debug(
                f'Terminated debugger at {strftime("%H:%M:%S")} on uninstall::completion', metadata)
                    log_info(
                        f'Terminated debugger at {strftime("%H:%M:%S")} on uninstall::completion', metadata.logfile)
                    close_log(metadata.logfile, 'Uninstall')
                else:
                    write(
                        f'Failed To Uninstall {packet.display_name}', 'bright_magenta', metadata)
                    log_error(f'Failed To Uninstall {packet.display_name}', metadata.logfile)
        else:
            if nightly:
                packet.version = 'nightly'
            write(
                f'Running Tests For {packet.display_name}', 'bright_white', metadata)
            if not skp:
                try:
                    os.remove(
                        rf'{PathManager.get_appdata_directory()}\Current\{package}@{packet.version}.json')
                except FileNotFoundError:
                    pass
            
            if not metadata.no_color:
                write(f'[ {Fore.LIGHTGREEN_EX}OK{Fore.RESET} ] Registry Check',
                    'bright_white', metadata)
            else:
                write(f'[ OK ] Registry Check', 'bright_white', metadata)   

            write(
                f'Successfully Uninstalled {packet.display_name}', 'bright_magenta', metadata)
            log_info(
                f'Succesfully Uninstalled {packet.display_name}', metadata.logfile)
            write_debug(
                f'Terminated debugger at {strftime("%H:%M:%S")} on uninstall::completion', metadata)
            log_info(
                f'Terminated debugger at {strftime("%H:%M:%S")} on uninstall::completion', metadata.logfile)
            close_log(metadata.logfile, 'Uninstall')



@cli.command(aliases=['clean', 'clear'], context_settings=CONTEXT_SETTINGS)
def cleanup():
    '''
    Clean up all temporary files generated by electric.
    '''
    from progress.bar import Bar

    with Halo('Cleaning Up ', text_color='green') as h:
        try:
            files = os.listdir(rf'{tempfile.gettempdir()}\electric')
        except:
            os.mkdir(rf'{tempfile.gettempdir()}\electric')
            h.stop()
            click.echo(click.style('Nothing To Cleanup!', 'bright_cyan'))
            sys.exit()

        if 'configurations' in files:
            if len(files) == 1:
                h.stop()
                click.echo(click.style('Nothing To Cleanup!', 'bright_cyan'))
        elif len(files) == 0:
            h.stop()
            click.echo(click.style('Nothing To Cleanup!', 'bright_cyan'))
            sys.exit()

        sub = 0
        if 'configurations' in files:
            sub = 1

        h.stop()
        with Bar(f'{Fore.LIGHTCYAN_EX}Deleting Temporary Files{Fore.RESET}', max=len(files) - sub, bar_prefix=' [ ', bar_suffix=' ] ', fill=f'{Fore.LIGHTGREEN_EX}={Fore.RESET}', empty_fill=f'{Fore.LIGHTBLACK_EX}-{Fore.RESET}') as b:
            for f in files:
                if f != 'configurations':
                    try:
                        os.remove(rf'{tempfile.gettempdir()}\electric\{f}')
                    except:
                        pass
                    b.next()


@cli.command(aliases=['bdl'], context_settings=CONTEXT_SETTINGS)
@click.argument('bundle_name', required=True)
@click.option('--remove', '-uninst', is_flag=True, help='Uninstall packages in a bundle installed')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose mode for bundle installation')
@click.option('--debug', '-d', is_flag=True, help='Enable debug mode for bundle installation')
@click.option('--no-progress', '-np', is_flag=True, default=False, help='Disable progress bar for bundle installation')
@click.option('--no-color', '-nc', is_flag=True, help='Disable colored output for bundle installation')
@click.option('--log-output', '-l', 'logfile', help='Log output to the specified file')
@click.option('--install-dir', '-dir', 'install_directory', help='Specify an installation directory for a package')
@click.option('--virus-check', '-vc', is_flag=True, help='Check for virus before bundle installation')
@click.option('-y', '--yes', is_flag=True, help='Accept all prompts during bundle installation')
@click.option('--silent', '-s', is_flag=True, help='Completely silent bundle installation without any output to console')
@click.option('--sync', '-sc', is_flag=True, help='Force downloads and installations one after another')
@click.option('--reduce', '-rd', is_flag=True, help='Cleanup all traces of package after bundle installation')
@click.option('--exclude', '-ex', 'exclude', help='Exclude a package from bundle installation')
@click.option('--rate-limit', '-rl', type=int, default=-1)
@click.pass_context
def bundle(
    ctx,
    bundle_name: str,
    remove: bool,
    verbose: bool,
    debug: bool,
    no_progress: bool,
    no_color: bool,
    logfile: str,
    install_directory: str,
    virus_check: bool,
    yes: bool,
    silent: bool,
    sync: bool,
    reduce: bool,
    rate_limit: bool,
    exclude: str,
):
    """
    Installs a bundle of packages from the official electric repository.
    """

    metadata = generate_metadata(
        no_progress, silent, verbose, debug, no_color, yes, logfile, virus_check, reduce, rate_limit, Setting.new(), sync)

    if is_admin():
        if logfile:
            logfile = logfile.replace('=', '')
            logfile = logfile.replace('.txt', '.log')
            from logging import INFO
            create_config(logfile, INFO, 'Install')

        log_info('Setting up custom `ctrl+c` shortcut.', metadata.logfile)
        status = 'Initializing'
        setup_name = ''
        add_hotkey(
            'ctrl+c', lambda: handle_exit(status, setup_name, metadata))

        log_info('Handling Network Request...', metadata.logfile)
        status = 'Networking'
        write_verbose('Sending GET Request To /bundles', metadata)
        write_debug('Sending GET Request To /bundles', metadata)
        log_info('Sending GET Request To /bundles', metadata.logfile)
        res = send_req_bundle(bundle_name)

        if not metadata.silent:
            if not metadata.no_color:
                print(
                    f'SuperCached [{Fore.LIGHTCYAN_EX} {res["display-name"]} {Fore.RESET}]')
            else:
                print(f'SuperCached {res["display-name"]}')

        package_names = ''
        idx = 0

        for value in res['dependencies']:
            if idx == 0:
                package_names += value
                idx += 1
                continue

            package_names += f',{value}'

        if exclude:
            package_names = package_names.replace(exclude, '')
            if package_names[0] == ',':
                package_names = package_names[1:]
        if remove:
            ctx.invoke(
                uninstall,
                package_name=package_names,
                verbose=verbose,
                debug=debug,
                no_color=no_color,
                logfile=logfile,
                yes=yes,
                silent=silent,
                python=None,
            )

        else:
            ctx.invoke(
                install,
                package_name=package_names,
                verbose=verbose,
                debug=debug,
                no_progress=no_progress,
                no_color=no_color,
                logfile=logfile,
                install_directory=install_directory,
                virus_check=virus_check,
                yes=yes,
                silent=silent,
                python=None,
                node=None,
                sync=sync,
                reduce=reduce,
                rate_limit=rate_limit
            )

    else:
        click.echo(click.style(
            '\nAdministrator Elevation Required For Bundle Installation. Exit Code [0001]', 'bright_red'), err=True)
        disp_error_msg(get_error_message(
            '0001', 'installation', 'None', None, metadata, ''), metadata)


@cli.command(aliases=['find'], context_settings=CONTEXT_SETTINGS)
@click.argument('approx_name', required=True)
@click.option('--starts-with', '-sw', is_flag=True, help='Find packages which start with the specified literal')
@click.option('--exact', '-e', is_flag=True, help='Find packages which exactly match the specified literal')
def search(
    approx_name: str,
    starts_with: str,
    exact: str,
):  # pylint: disable=function-redefined
    """
    Searches for a package in the official electric package repository.
    """

    correct_names = get_correct_package_names(all=True)

    matches = []
    if exact:
        for name in correct_names:
            if name == approx_name:
                matches.append(name)
    if starts_with:
        for name in correct_names:
            if name.startswith(approx_name):
                matches.append(name)
    elif not exact and not starts_with:
        from difflib import get_close_matches
        matches = get_close_matches(
            approx_name, correct_names, cutoff=0.7)

    if len(matches) > 0:
        idx = 0
        for match in matches:
            if idx == 0:
                click.echo(click.style(f'{match}', fg='bright_magenta'))
                idx += 1
                continue
            else:
                print(match)
        if len(matches) != 1:
            click.echo(click.style(
                f'{len(matches)} packages found.', fg='bright_green'))
        else:
            click.echo(click.style('1 package found.', fg='bright_yellow'))

    else:
        click.echo(click.style('0 Packages Found!', fg='bright_red'))
        upload = confirm(
            'Would you like to request this package to be added to electric?')
        with Halo(text='Uploading Package Request') as h:
            if upload:
                send_package_request(approx_name)
            h.stop()
            print(
                f'{Fore.GREEN}Successfully Uploaded Package Request For {approx_name}{Fore.RESET}')


@cli.command(aliases=['create'], context_settings=CONTEXT_SETTINGS)
@click.argument('project_name', required=True)
def new(
    project_name: str
):
    """
    Generates a new .electric configuration with a template for ease of development.
    """
    project_name = project_name.replace('.electric', '')
    with open(f'{project_name}.electric', 'w+') as f:
        f.writelines(
            [
                "[ Info ]\n",
                "# Go To https://www.electric.sh/docs/configurations For More Information\n",
                "Publisher =>\n",
                "Description =>\n\n",
                "\n[ Editor-Configuration ]\n",
                "Editor =>\n",
                "\n[ Packages ]\n",
                "\n[ Editor-Extensions ]\n",
                "\n[ Pip-Packages ]\n",
                "\n[ Node-Packages ]\n"
            ]
        )
    click.echo(click.style(
        f'Successfully Created {Fore.LIGHTBLUE_EX}`{project_name}.electric`{Fore.LIGHTGREEN_EX} at {os.getcwd()}\\', 'bright_green'))


@cli.command(context_settings=CONTEXT_SETTINGS)
@click.argument('package_name', required=True)
@click.option('--version', '-v', 'version', help='Register a specific version')
@click.option('--install-dir', '-id', 'install_dir', help='Register a specific installation directory')
def register(
    package_name: str,
    version: str,
    install_dir: str
):
    res = send_req_package(package_name)
    display_name = res['display-name']
    package_name = res['package-name']
    if 'is-portable' in list(res.keys()):
        latest_version = res['portable']['latest-version']
    if not version and not 'is-portable' in list(res.keys()):
        latest_version = res['latest-version']
    else:
        latest_version = version
    custom_directory = install_dir if install_dir else ''
    with open(rf'{PathManager.get_appdata_directory()}\Current\{package_name}@{latest_version}.json', 'w+') as f:
        f.write(
            json.dumps(
                {
                    'display-name': display_name,
                    'json-name': package_name,
                    'version': latest_version,
                    'custom-location-switch': '',
                    'custom-install-directory': custom_directory,
                    'flags': []
                }
            )
        )


@cli.command(context_settings=CONTEXT_SETTINGS)
@click.argument('package_name', required=True)
@click.option('--version', '-v', 'version', help='Deregister a specific version')
def deregister(package_name: str, version: str):
    res = send_req_package(package_name)
    if 'is-portable' in list(res.keys()):
        latest_version = res['portable']['latest-version']
    if not version and not 'is-portable' in list(res.keys()):
        latest_version = res['latest-version']

    try:
        os.remove(
            rf'{PathManager.get_appdata_directory()}\electric\Current\{package_name}@{latest_version}')
    except:
        pass


@cli.command(context_settings=CONTEXT_SETTINGS)
@click.argument('config_path', required=True)
@click.option('--uninstall', '-u', is_flag=True, help='Uninstall packages in a config')
@click.option('--include-versions', '-iv', is_flag=True, help='Include versions for the config installation')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose mode for config installation')
@click.option('--debug', '-d', is_flag=True, help='Enable debug mode for config installation')
@click.option('--no-progress', '-np', is_flag=True, default=False, help='Disable progress bar for config installation')
@click.option('--no-color', '-nc', is_flag=True, help='Disable colored output for config installation')
@click.option('--log-output', '-l', 'logfile', help='Log output to the specified file')
@click.option('--install-dir', '-dir', 'install_directory', help='Specify an installation directory for a package')
@click.option('--virus-check', '-vc', is_flag=True, help='Check for virus before config installation')
@click.option('-y', '--yes', is_flag=True, help='Accept all prompts during config installation')
@click.option('--silent', '-s', is_flag=True, help='Completely silent config installation without any output to console')
@click.option('--sync', '-sc', is_flag=True, help='Force downloads and installations one after another')
@click.option('--reduce', '-rd', is_flag=True, help='Cleanup all traces of package after config installation')
@click.option('--rate-limit', '-rl', type=int, default=-1)
def config(
    config_path: str,
    uninstall: bool,
    verbose: bool,
    debug: bool,
    no_progress: bool,
    no_color: bool,
    logfile: str,
    install_directory: str,
    virus_check: bool,
    yes: bool,
    silent: bool,
    sync: bool,
    reduce: bool,
    rate_limit: bool,
    include_versions: bool
):
    '''
    Install or Uninstalls and configures packages from a .electric configuration file.
    '''
    from Classes.Config import Config

    if not is_admin():
        if '.\\' in config_path:
            config_path = config_path.replace('.\\', '')
            config_path = os.getcwd() + '\\' + config_path

        if not '\\' in config_path:
            config_path = os.getcwd() + '\\' + config_path
        os.system(
            fr'{PathManager.get_current_directory()}\scripts\context-elevate.cmd {config_path}')

        sys.exit()

    metadata = generate_metadata(
        no_progress, silent, verbose, debug, no_color, yes, logfile, virus_check, reduce, rate_limit, Setting.new(), sync)

    config = Config.generate_configuration(config_path)
    config.check_prerequisites()
    if uninstall:
        config.uninstall(include_versions)
    else:
        config.install(include_versions, install_directory, metadata)


@cli.command(aliases=['validate'], context_settings=CONTEXT_SETTINGS)
@click.argument('filepath', required=True)
def sign(
    filepath: str
):
    '''
    Signs and validates a .electric configuration file.
    '''
    from Classes.Config import Config
    import hashlib

    config = Config.generate_configuration(filepath, False)

    click.echo(click.style('No syntax errors found!', 'bright_green'))

    config.verify()

    md5 = hashlib.md5(open(filepath, 'rb').read()).hexdigest()
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        # Read and update hash string value in blocks of 4K
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)

    sha256 = sha256_hash.hexdigest()
    with open(filepath, 'r') as f:
        l = [line.strip() for line in f.readlines()]

        if '# --------------------Checksum Start-------------------------- #' in l and '# --------------------Checksum End--------------------------- #' in l:
            click.echo(click.style(
                'File Already Signed, Aborting Signing!', fg='bright_red'))
            sys.exit()

    with open(filepath, 'a') as f:
        f.writelines([

            '\n# --------------------Checksum Start-------------------------- #',
            '\n',
            f'# {md5}',
            '\n',
            f'# {sha256}',
            '\n',
            '# --------------------Checksum End--------------------------- #'
        ])

    click.echo(click.style(
        f'Successfully Signed {filepath}', fg='bright_green'))


@cli.command(aliases=['gen'], context_settings=CONTEXT_SETTINGS)
@click.argument('filepath', required=False)
def generate(
    filepath: str
):
    from subprocess import Popen, PIPE
    from prompt_toolkit.completion import WordCompleter
    from prompt_toolkit import prompt
    editor_completion = WordCompleter(
        ['Visual Studio Code', 'Visual Studio Code Insiders', 'Sublime Text 3', 'Atom'])

    username = prompt('Enter Publisher Name => ')
    description = prompt('Enter Configuration Description => ')
    use_editor = prompt(
        'Do You Use A Development Text Editor (Example: Visual Studio Code) [y/N]: ')
    use_editor = use_editor in ('y', 'yes', 'Y', 'YES')
    include_editor = False
    editor = ''
    if use_editor:
        include_editor = confirm(
            'Do You Want To Include Your Editor Extensions And Configuration?')
        if include_editor:
            editor = prompt('Enter The Development Text Editor You Use => ',
                            completer=editor_completion, complete_while_typing=True)
    
    if editor not in ['Visual Studio Code', 'Visual Studio Code Insiders', 'Sublime Text 3', 'Atom']:
        print(f'{editor} is not a valid editor')
        sys.exit()
    
    include_python = None
    try:
        proc = Popen('pip --version', stdin=PIPE,
                     stdout=PIPE, stderr=PIPE, shell=True)
        _, err = proc.communicate()
        if not err:
            include_python = confirm(
                'Would you like to include your Python Configuration?')
    except FileNotFoundError:
        pass

    include_npm = None
    try:
        proc = Popen('npm --version', stdin=PIPE,
                     stdout=PIPE, stderr=PIPE, shell=True)
        _, err = proc.communicate()
        if not err:
            include_npm = confirm(
                'Would you like to include your Npm Or Node Configuration?')
    except FileNotFoundError:
        pass

    if filepath:
        with open(f'{filepath}', 'w+') as f:
            f.writelines(get_configuration_data(username, description,
                                                use_editor, include_editor, editor, include_python, include_npm))
    else:
        with open(f'{PathManager.get_desktop_directory()}\electric-configuration.electric', 'w+') as f:
            f.writelines(get_configuration_data(username, description,
                                                use_editor, include_editor, editor, include_python, include_npm))

    os.system(
        f'electric sign {PathManager.get_desktop_directory()}\electric-configuration.electric')


@cli.command(aliases=['list'], context_settings=CONTEXT_SETTINGS)
@click.option('--installed', '-i', is_flag=True, help='List all installed packages')
@click.option('--versions', '-v', is_flag=True, help='List all installed packages')
@click.pass_context
def ls(_, installed: bool, versions: bool):
    '''
    Lists top packages which can be installed.
    If --installed is passed in, lists all installed packages
    '''
    import winreg

    if installed:
        if not versions:
            try:
                installed_packages = [''.join(f.replace('.json', '').split(
                    '@')[:1]) for f in os.listdir(PathManager.get_appdata_directory() + r'\Current')]
                for package_name in installed_packages:
                    print(package_name)
            except:
                print(
                    f'{Fore.LIGHTYELLOW_EX}No installed packages found{Fore.RESET}')
        else:
            os.chdir(PathManager.get_appdata_directory() + r'\Current')
            try:
                installed_packages = [f.replace('.json', '') for f in os.listdir(
                    PathManager.get_appdata_directory() + r'\Current')]
                for package_name in installed_packages:
                    print(package_name)
            except:
                print(
                    f'{Fore.LIGHTYELLOW_EX}No installed packages found{Fore.RESET}')
    else:
        installed_software = send_query(winreg.HKEY_LOCAL_MACHINE, winreg.KEY_WOW64_32KEY) + send_query(
            winreg.HKEY_LOCAL_MACHINE, winreg.KEY_WOW64_64KEY) + send_query(winreg.HKEY_CURRENT_USER, 0)
        
        max_length = 80
        names = [software['DisplayName'] for software in installed_software]

        versions = []
        for software in installed_software:
            # id = re.findall(r'{[A-Z\d-]{36}\}', software['UninstallString'])

            version = software['Version']
            versions.append(version)

        print('Name', ' ' * 76, 'Version')
        print('-' * 105)

        idx = 0
        for name in names:
            length = len(name)
            print(name.strip(), ' ' * (max_length - length), versions[idx])
            idx += 1


@cli.command(aliases=['info'], context_settings=CONTEXT_SETTINGS)
@click.option('--nightly', '--pre-release', is_flag=True, help='Show a nightly or pre-release build of a package')
@click.argument('package_name', required=True)
def show(package_name: str, nightly: bool):
    '''
    Displays information about the specified package.
    '''
    res = send_req_package(package_name)
    click.echo(click.style(display_info(
        res, nightly=nightly), fg='bright_green'))


@cli.command(context_settings=CONTEXT_SETTINGS)
def settings():
    from settings import initialize_settings, open_settings
    from cursor import hide, show
   
    if not os.path.isfile(rf'{PathManager.get_appdata_directory()}\\settings.json'):
        click.echo(click.style(
            f'Creating settings.json at {Fore.LIGHTCYAN_EX}{PathManager.get_appdata_directory()}{Fore.RESET}', fg='bright_green'))
        initialize_settings()
    hide()
    with Halo('Opening Settings... ', text_color='cyan'):
        open_settings()
    show()


@cli.command(context_settings=CONTEXT_SETTINGS)
@click.pass_context
def autoupdate(
    ctx,
):
    from pygments import highlight, lexers, formatters
    from bs4 import BeautifulSoup

    message = '''AU - The Official Electric Auto-Update CLI For Generating Automatically Updating Manifests.
    '''
    print(message)

    print('Enter the path to the manifest / json file: ')
    fp = input(F'>{Fore.LIGHTYELLOW_EX} ').replace('\"', '')

    with open(fp, 'r') as f:
        data = json.load(f)

    package_name = data['package-name']

    latest_version = data['latest-version']

    # url = data[data['latest-version']]['url']

    webpage = data['auto-update']['vercheck']['webpage']

    print(f'{Fore.LIGHTGREEN_EX}Sending Request To {webpage}{Fore.RESET}')

    html = swc(webpage.strip())
    show_html = input(
        'Would you like to see the response of the request? [Y/n]: ')
    if show_html == 'y' or show_html == 'Y' or show_html == 'yes' or show_html == 'YES' or show_html == 'Yes':
        print(html)

    soup = BeautifulSoup(html, features="html.parser")

    version_list = {}

    for tag in soup.find_all('h4', class_='flex-auto min-width-0 pr-2 pb-1 commit-title'):
        if tag:
            try:
                version_list[tag.find('a').text.strip().replace('v', '').replace('V', '')] = int(
                    tag.find('a').text.strip().replace('.', '').replace('v', '').replace('V', ''))
            except:
                pass

    print(f'Detected Versions On Webpage:', list(version_list.keys()))

    try:
        web_version = max(version_list, key=version_list.get)
    except:
        print(f'{Fore.LIGHTRED_EX}No Versions Detected On Webpage!{Fore.RESET}')
        sys.exit()

    print(f'{Fore.LIGHTGREEN_EX}Latest Version Detected:{Fore.RESET} {web_version}')

    int_web_version = int(web_version.strip().replace(
        'v', '').replace('V', '').replace('.', ''))

    try:
        int_current_version = int(latest_version.strip().replace(
            'v', '').replace('V', '').replace('.', ''))
    except:
        print(f'{Fore.LIGHTRED_EX}The Current Version Must Not Contain Any Characters')

    if int_current_version < int_web_version:
        print(
            f'A Newer Version Of {package_name} Is Availiable! Updating Manifest')

        old_latest = latest_version
        data['latest-version'] = web_version
        data[web_version] = data[old_latest]
        data[web_version]['url'] = data['auto-update']['url'].replace(
            '<version>', web_version)
        colorful_json = json.dumps(
            data, indent=4)
        print(colorful_json)


@cli.command()
@click.argument('method', nargs=1, required=True)
@click.argument('feature', nargs=1, required=False)
def feature(method: str, feature: str):
    if method in ['enable', 'disable', 'list']:
        if method == 'list':
            setting = Setting.new()
            message = f'''
[{Fore.LIGHTGREEN_EX if setting.show_support_message else Fore.LIGHTYELLOW_EX}{'X' if setting.show_support_message == True else ' '}{Fore.RESET}] Support Message {Fore.LIGHTMAGENTA_EX}-{Fore.RESET} Send a weekly developers note to request support for electric.
Command: electric feature [enable|disable] support-message

[{Fore.LIGHTGREEN_EX if setting.checksum else Fore.LIGHTYELLOW_EX}{'X' if setting.checksum == True else ' '}{Fore.RESET}] Checksum Verification {Fore.LIGHTMAGENTA_EX}-{Fore.RESET} Verify the checksum of installers downloaded from the internet.
Command: electric feature [enable|disable] checksum

[{Fore.LIGHTGREEN_EX if setting.virus_check else Fore.LIGHTYELLOW_EX}{'X' if setting.virus_check == True else ' '}{Fore.RESET}] Runtime Malware Protection {Fore.LIGHTMAGENTA_EX}-{Fore.RESET} Scan downloaded files for viruses before running the installers.
Command: electric feature [enable|disable] virus-check

[{Fore.LIGHTGREEN_EX if setting.install_metrics else Fore.LIGHTYELLOW_EX}{'X' if setting.install_metrics == True else ' '}{Fore.RESET}] Install Metrics {Fore.LIGHTMAGENTA_EX}-{Fore.RESET} Increment a global counter for the number of installations for a certain package.
Command: electric feature [enable|disable] install-metrics

[{Fore.LIGHTGREEN_EX if setting.show_progress_bar else Fore.LIGHTYELLOW_EX}{'X' if setting.show_progress_bar == True else ' '}{Fore.RESET}] Progress Bar {Fore.LIGHTMAGENTA_EX}-{Fore.RESET} Show a progress while downloading files (shows basic percentage counter if disabled).
Command: electric feature [enable|disable] show-progress-bar

[{Fore.LIGHTGREEN_EX if setting.electrify_progress_bar else Fore.LIGHTYELLOW_EX}{'X' if setting.electrify_progress_bar == True else ' '}{Fore.RESET}] Electrify Progress Bar {Fore.LIGHTMAGENTA_EX}-{Fore.RESET} Add the thunder emoji to the progress bar. Only supported on terminals with emoji support.
Command: electric feature [enable|disable] electric-progress-bar
            '''

            print(message)

        if feature in ['support-message', 'checksum', 'virus-check', 'install-metrics', 'progress-bar', 'electric-progress-bar']:
            
            if feature == 'support-message' and method == 'disable':
                current_settings = Setting.new()
                current_settings.raw_dictionary['supportMessage'] = False
                with open(rf'{PathManager.get_appdata_directory()}\settings.json', 'w+') as f:
                    f.write(json.dumps(current_settings.raw_dictionary, indent=4))
                print(f'{Fore.LIGHTGREEN_EX}Successfully Disabled Support Message{Fore.RESET}')

            elif feature == 'support-message' and method == 'enable':
                current_settings = Setting.new()
                current_settings.raw_dictionary['supportMessage'] = True
                with open(rf'{PathManager.get_appdata_directory()}\settings.json', 'w+') as f:
                    f.write(json.dumps(current_settings.raw_dictionary, indent=4))
                print(f'{Fore.LIGHTGREEN_EX}Successfully Enabled Support Message{Fore.RESET}')

            if feature == 'checksum' and method == 'enable':
                current_settings = Setting.new()
                current_settings.raw_dictionary['checksumInstallers'] = True
                with open(rf'{PathManager.get_appdata_directory()}\settings.json', 'w+') as f:
                    f.write(json.dumps(current_settings.raw_dictionary, indent=4))
                print(f'{Fore.LIGHTGREEN_EX}Successfully Enabled Installer Checksum Verification{Fore.RESET}')
            
            if feature == 'checksum' and method == 'disable':
                current_settings = Setting.new()
                current_settings.raw_dictionary['checksumInstallers'] = False
                with open(rf'{PathManager.get_appdata_directory()}\settings.json', 'w+') as f:
                    f.write(json.dumps(current_settings.raw_dictionary, indent=4))
                print(f'{Fore.LIGHTGREEN_EX}Successfully Disabled Installer Checksum Verification{Fore.RESET}')
            
            
            if feature == 'virus-check' and method == 'enable':
                current_settings = Setting.new()
                current_settings.raw_dictionary['virusCheck'] = True
                with open(rf'{PathManager.get_appdata_directory()}\settings.json', 'w+') as f:
                    f.write(json.dumps(current_settings.raw_dictionary, indent=4))
                print(f'{Fore.LIGHTGREEN_EX}Successfully Enabled Runtime Malware Protection{Fore.RESET}')
            
            if feature == 'virus-check' and method == 'disable':
                current_settings = Setting.new()
                current_settings.raw_dictionary['virusCheck'] = False
                with open(rf'{PathManager.get_appdata_directory()}\settings.json', 'w+') as f:
                    f.write(json.dumps(current_settings.raw_dictionary, indent=4))
                print(f'{Fore.LIGHTGREEN_EX}Successfully Disabled Runtime Malware Protection{Fore.RESET}')
            
            if feature == 'install-metrics' and method == 'enable':
                current_settings = Setting.new()
                current_settings.raw_dictionary['installMetrics'] = True
                with open(rf'{PathManager.get_appdata_directory()}\settings.json', 'w+') as f:
                    f.write(json.dumps(current_settings.raw_dictionary, indent=4))
                print(f'{Fore.LIGHTGREEN_EX}Successfully Enabled Install Metrics{Fore.RESET}')
            
            if feature == 'install-metrics' and method == 'disable':
                current_settings = Setting.new()
                current_settings.raw_dictionary['installMetrics'] = False
                with open(rf'{PathManager.get_appdata_directory()}\settings.json', 'w+') as f:
                    f.write(json.dumps(current_settings.raw_dictionary, indent=4))
                print(f'{Fore.LIGHTGREEN_EX}Successfully Disabled Install Metrics{Fore.RESET}')
            
            if feature == 'progress-bar' and method == 'enable':
                current_settings = Setting.new()
                current_settings.raw_dictionary['showProgressBar'] = True
                with open(rf'{PathManager.get_appdata_directory()}\settings.json', 'w+') as f:
                    f.write(json.dumps(current_settings.raw_dictionary, indent=4))
                print(f'{Fore.LIGHTGREEN_EX}Successfully Enabled Progress Bar{Fore.RESET}')
            
            if feature == 'progress-bar' and method == 'disable':
                current_settings = Setting.new()
                current_settings.raw_dictionary['showProgressBar'] = False
                with open(rf'{PathManager.get_appdata_directory()}\settings.json', 'w+') as f:
                    f.write(json.dumps(current_settings.raw_dictionary, indent=4))
                print(f'{Fore.LIGHTGREEN_EX}Successfully Disabled Progress Bar{Fore.RESET}')
           
            if feature == 'electric-progress-bar' and method == 'enable':
                current_settings = Setting.new()
                current_settings.raw_dictionary['electrifyProgressBar'] = True
                with open(rf'{PathManager.get_appdata_directory()}\settings.json', 'w+') as f:
                    f.write(json.dumps(current_settings.raw_dictionary, indent=4))
                print(f'{Fore.LIGHTGREEN_EX}Successfully Enabled Electric Progress Bar{Fore.RESET}')
            
            if feature == 'electric-progress-bar' and method == 'disable':
                current_settings = Setting.new()
                current_settings.raw_dictionary['electrifyProgressBar'] = False
                with open(rf'{PathManager.get_appdata_directory()}\settings.json', 'w+') as f:
                    f.write(json.dumps(current_settings.raw_dictionary, indent=4))
                print(f'{Fore.LIGHTGREEN_EX}Successfully Disabled Electric Progress Bar{Fore.RESET}')
           
            
    else:
        print(f'{Fore.LIGHTRED_EX}Method Must Be Specified As `enable` or `disable`')
    pass


if __name__ == '__main__':
    try:
        freeze_support()
        cli()  # pylint: disable=no-value-for-parameter
    except KeyboardInterrupt:
        pass

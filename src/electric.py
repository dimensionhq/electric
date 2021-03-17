######################################################################
#                      Copyright 2021 XtremeDevX                     #
#                 SPDX-License-Identifier: Apache-2.0                #
######################################################################

# TODO: Add Conflict-With Field For Json To Differentiate Between Microsoft Visual Studio Code and Microsoft Visual Studio Code Insiders

from timeit import default_timer as timer
import difflib
from logging import INFO
import os
import sys
import time as tm
import click
import halo
import keyboard
from colorama import Fore
from multiprocessing import freeze_support

from Classes.Packet import Packet
from Classes.PortablePacket import PortablePacket
from Classes.Setting import Setting
from Classes.ThreadedInstaller import ThreadedInstaller
from cli import SuperChargeCLI
from external import *
from headers import *
from info import __version__
from logger import *
from registry import get_environment_keys, get_uninstall_key, send_query
from settings import initialize_settings, open_settings
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
        # Create the superlog.txt and write the current timestamp
        with open(rf'{PathManager.get_appdata_directory()}\superlog.txt', 'w+') as f:
            f.write(
                f'{date.today().year} {date.today().month} {date.today().day}')

    # Check if settings.json exists in USERAPPDATA
    if not os.path.isfile(rf'{PathManager.get_appdata_directory()}\settings.json'):
        click.echo(click.style(
            f'Creating settings.json at {Fore.LIGHTCYAN_EX}{PathManager.get_appdata_directory()}{Fore.RESET}', fg='bright_green'))
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
@click.option('--ignore', '-ig', is_flag=True, help='Ignore existing installation')
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
    ignore: bool,
    manifest: str,
):
    """
    Install a package or a list of packages.
    """
    start_log()

    if not manifest and package_name == 'test':
        print(f'{Fore.LIGHTRED_EX}A Package Name Must Be Supplied\nUsage: electric install <package-name>\n\nExamples:\nelectric install {Fore.LIGHTGREEN_EX}sublime-text-3{Fore.RESET}\n{Fore.LIGHTRED_EX}electric install {Fore.LIGHTGREEN_EX}sublime-text-3,notepad++{Fore.RESET}')
        sys.exit()

    if plugin:
        if package_name == 'eel':
            os.chdir(PathManager.get_current_directory() + r'\eel')
            os.system('pip install -e .')
            click.echo(
                f'{Fore.LIGHTGREEN_EX}Successfully Installed eel Plugin, {Fore.LIGHTCYAN_EX}Refreshing Environment Variables.{Fore.RESET}')
            refresh_environment_variables()
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
        create_config(logfile, INFO, 'Install')

    log_info('Generating metadata...', logfile)

    metadata = generate_metadata(
        no_progress, silent, verbose, debug, no_color, yes, logfile, virus_check, reduce, rate_limit, Setting.new(), sync)

    if update:
        write('Updating Electric', 'bright_green', metadata)
        update_package_list()

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
        corrected_package_names, install_directory, metadata,ignore)


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

        if not manifest:
            res = send_req_package(package)
        else:
            try:
                f = open(manifest, 'r')
                try:
                    res = json.load(f)
                except JSONDecodeError as e:
                    print(f'Invalid Manifest JSON Syntax : {Fore.LIGHTRED_EX}{e}{Fore.RESET}')
                    sys.exit()
                package = res['package-name'] 

            except FileNotFoundError:
                write(f'{manifest} Does Not Exist!', 'bright_red', metadata)
                write_verbose(f'{manifest} File Path Not Found!', metadata)
                write_debug(f'{manifest} FileNotFoundError, Specified Manifest Cannot Be Found!', metadata)
                log_info(f'{manifest} FileNotFoundError, Specified Manifest Cannot Be Found!', metadata.logfile)
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
                            write('Installation Must Be Run As Administrator', 'bright_red', metadata)
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
                    os.system(rf'powershell.exe -noprofile -File {tempfile.gettempdir()}\electric\temp.ps1')

                elif operation['type'] == 'batch' or operation['type'] == 'cmd':
                    with open(rf'{tempfile.gettempdir()}\electric\temp.bat', 'w+') as f:
                        for line in operation['code']:
                            f.write(line + '\n')
                    os.system(rf'{tempfile.gettempdir()}\electric\temp.bat')                
            sys.exit()


        install_exit_codes = []
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
            pkg['default-install-dir'].replace('<appdata>', os.environ['APPDATA'].replace('\\Roaming', '')) if 'default-install-dir' in list(pkg.keys()) else None, 
            pkg['uninstall'] if 'uninstall' in list(pkg.keys()) else [], 
            pkg['add-path'] if 'add-path' in list(pkg.keys()) else None,
            pkg['checksum'] if 'checksum' in list(pkg.keys()) else None,
        )

        write_verbose(
            f'Rapidquery Successfully Received {packet.json_name}.json', metadata)
        write_debug(
            f'Rapidquery Successfully Received {packet.json_name}.json', metadata)
        log_info(
            f'Rapidquery Successfully Received {packet.json_name}.json', metadata.logfile)

        handle_existing_installation(package, packet, force, metadata, ignore)

        if 'add-path' in list(pkg.keys()):
            if not is_admin():
                write('Installation Must Be Run As Administrator', 'bright_red', metadata)
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

        if packet.checksum:
            verify_checksum(configs['path'], packet.checksum, metadata)

        log_info('Finished Rapid Download', metadata.logfile)

        if virus_check:
            log_info('Running requested virus scanning', metadata.logfile)
            write('Scanning File For Viruses...', 'bright_cyan', metadata)
            check_virus(configs['path'], metadata)
        write_debug(
            f'Installing {packet.display_name} through Setup{packet.win64_type}', metadata)        
        
        write(f'Installing {packet.display_name}',
              'bright_cyan', metadata)
        log_info(
            'Using Rapid Install To Complete Setup, Accept Prompts Asking For Admin Permission...', metadata.logfile)


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
                                write('Installation Must Be Run As Administrator', 'bright_red', metadata)
                                os._exit(1)
                    if proc['type'] == 'powershell':
                        with open(rf'{tempfile.gettempdir()}\electric\temp.ps1', 'w+') as f:
                            for line in proc['code']:
                                f.write(line.replace('<installer>', configs['path']).replace('<package-name>', packet.json_name).replace('<display-name>', packet.display_name).replace('<version>', version).replace('<temp>', tempfile.gettempdir()) + '\n')

                        os.system(rf'powershell.exe -File {tempfile.gettempdir()}\electric\temp.ps1')

                    if proc['type'] == 'cmd':
                        with open(rf'{tempfile.gettempdir()}\electric\temp.bat', 'w+') as f:
                            for line in proc['code']:
                                f.write(line.replace('<installer>', configs['path']).replace('<package-name>', packet.json_name).replace('<display-name>', packet.display_name).replace('<version>', version).replace('<temp>', tempfile.gettempdir()) + '\n')

                        os.system(rf'{tempfile.gettempdir()}\electric\temp.bat')

                    if proc['type'] == 'python':
                        ldict = {}
                        code = ''''''
                        for line in proc['code']:
                            code += line.replace('<installer>', configs['path']).replace('<temp>', tempfile.gettempdir()).replace('<package-name>', packet.json_name).replace('<display-name>', packet.display_name).replace('<version>', version) + '\n'
                        exec(code, globals(), ldict)
                        for k in configs:
                            if k in ldict:
                                configs[k] = ldict[k]

        setup_name = configs['path'].split('\\')[-1] + packet.win64_type
        status = 'Installing'

        keyboard.add_hotkey('ctrl+c', lambda: handle_exit(status, setup_name, metadata))

        if not get_pid(setup_name):
            # Running The Installer silently And Completing Setup
            write_verbose(f'Running {packet.display_name} Installer at {configs["path"]}', metadata)
            log_info(f'Running {packet.display_name} Installer at {configs["path"]}', metadata.logfile)
            install_package(configs['path'], packet, metadata)
        else:
            disp_error_msg(get_error_message('1618', 'install', packet.display_name, version, metadata, packet.json_name), metadata)

        log_info('Deregistering ctrl+c abort shortcut', metadata.logfile)
        write_verbose('Deregistering ctrl+c abort shortcut', metadata)
        keyboard.remove_hotkey('ctrl+c')
        write_verbose('Checking for post install code', metadata)
        log_info('Checking for post install code', metadata.logfile)

        if 'post-install' in list(pkg.keys()):
            if isinstance(pkg['post-install'], list):
                for proc in pkg['post-install']:
                    if 'admin' in list(proc.keys()):
                        if proc['admin'] == True:
                            if not is_admin():
                                write('Installation Must Be Run As Administrator', 'bright_red', metadata)
                                os._exit(1)
                    if proc['type'] == 'powershell':
                        with open(rf'{tempfile.gettempdir()}\electric\temp.ps1', 'w+') as f:
                            for line in proc['code']:
                                f.write(line.replace('<installer>', configs['path']).replace('<package-name>', packet.json_name).replace('<display-name>', packet.display_name).replace('<version>', version).replace('<temp>', tempfile.gettempdir()) + '\n')

                        os.system(rf'powershell.exe -File {tempfile.gettempdir()}\electric\temp.ps1')

                    if proc['type'] == 'cmd':
                        with open(rf'{tempfile.gettempdir()}\electric\temp.bat', 'w+') as f:
                            for line in proc['code']:
                                f.write(line.replace('<installer>', configs['path']).replace('<package-name>', packet.json_name).replace('<display-name>', packet.display_name).replace('<version>', version).replace('<temp>', tempfile.gettempdir()) + '\n')

                        os.system(rf'{tempfile.gettempdir()}\electric\temp.bat')

                    if proc['type'] == 'python':
                        ldict = {}
                        code = ''''''
                        for line in proc['code']:
                            code += line.replace('<installer>', configs['path']).replace('<temp>', tempfile.gettempdir()).replace('<package-name>', packet.json_name).replace('<display-name>', packet.display_name).replace('<version>', version) + '\n'
                        exec(code, globals())

        status = 'Installed'
        write_verbose('Creating registry end snapshot', metadata)
        log_info('Creating final snapshot of registry', metadata.logfile)
        
        final_snap = get_environment_keys()

        if packet.add_path:
            replace_install_dir = ''

            if packet.directory:
                replace_install_dir = packet.directory

            elif packet.default_install_dir:
                replace_install_dir = packet.default_install_dir
            
            write(f'Appending "{packet.add_path.replace("<install-directory>", replace_install_dir)}" To PATH', 'bright_green', metadata)
            write_verbose(f'Appending "{packet.add_path.replace("<install-directory>", replace_install_dir)}" To PATH', 'bright_green', metadata)
            log_info(f'Appending "{packet.add_path.replace("<install-directory>", replace_install_dir)}" To PATH', metadata.logfile)
            append_to_path(packet.add_path.replace('<install-directory>', replace_install_dir))

        if packet.set_env:
            name = packet.set_env['name']
            replace_install_dir = ''

            if packet.directory:
                replace_install_dir = packet.directory

            elif packet.default_install_dir:
                replace_install_dir = packet.default_install_dir

            write(f'Setting Environment Variable {name}', 'bright_green', metadata)
            write_verbose(f'Setting Environment Variable {name} to {packet.set_env["value"].replace("<install-directory>", replace_install_dir)}', 'bright_green', metadata)
            log_info(f'Setting Environment Variable {name} to {packet.set_env["value"].replace("<install-directory>", replace_install_dir)}', metadata.logfile)
            
            set_environment_variable(
                name, packet.set_env['value'].replace('<install-directory>', replace_install_dir))
       
        if final_snap.env_length > start_snap.env_length or final_snap.sys_length > start_snap.sys_length:
            write('Refreshing Environment Variables', 'bright_green', metadata)
            start = timer()
            log_info(
                'Refreshing Environment Variables At scripts/refreshvars.cmd', metadata.logfile)
            write_debug(
                'Refreshing Env Variables, Calling Batch Script At scripts/refreshvars.cmd', metadata)
            write_verbose('Refreshing Environment Variables', metadata)
            refresh_environment_variables()
            end = timer()
            write_debug(
                f'Successfully Refreshed Environment Variables in {round(end - start)} seconds', metadata)

        if not packet.run_test:
            write_verbose(f'Running tests for {packet.display_name}', metadata)
            
            write_debug(f'No Pre-Defined Tests found for {packet.display_name}', metadata)
            log_info(f'No Pre-Defined Tests found for {packet.display_name}', metadata.logfile)
            
            write(
                f'Running Tests For {packet.display_name}', 'bright_white', metadata)
            
            write_debug(f'All Pre-Defined checks for {packet.display_name} passed. Registering successful package installation', metadata)
            write_verbose(f'All Pre-Defined checks for {packet.display_name} passed', metadata)
            log_info(f'All Pre-Defined checks for {packet.display_name} passed', metadata.logfile)
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
            write_debug(f'Pre-Defined Checks found for {packet.display_name}', metadata)
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

                write_debug('Passed Registry Check. Registering Package Success', metadata)
                register_package_success(packet, install_directory, metadata)
                write(
                    f'Successfully Installed {packet.display_name}', 'bright_magenta', metadata)
                log_info(
                    f'Successfully Installed {packet.display_name}', metadata.logfile)
            else:
                write(
                    f'[ {Fore.LIGHTRED_EX}ERROR{Fore.RESET} ] Registry Check', 'bright_white', metadata)
                write('Retrying Registry Check In 5 seconds', 'bright_yellow', metadata)
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
                    write(f'Failed To Install {packet.display_name}', 'bright_red', metadata)
                sys.exit()

        if metadata.reduce_package:
            write_verbose(f'Deleting installer files at {tempfile.gettempdir()}', metadata)
            log_info(f'Deleting installer files at {tempfile.gettempdir()}', metadata.logfile)
            write_debug(f'Deleting installer files at {tempfile.gettempdir()}. Path : ({configs["path"]}{packet.win64_type})', metadata)
            os.remove(f'{configs["path"]}{packet.win64_type}')
            os.remove(
                Rf'{tempfile.gettempdir()}\electric\downloadcache.pickle')

            log_info(
                'Successfully Cleaned Up Installer From Temporary Directory And DownloadCache', metadata.logfile)
            write('Successfully Cleaned Up Installer From Temp Directory',
                  'bright_green', metadata)
        
        version = ''

        # if metadata.settings.install_metrics == True:
        #     f_and_f(packet.json_name, 'success')

        write_verbose('Installation and setup completed with exit code 0', metadata)
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
    update_package_list()
    if package_name == 'electric' or package_name == 'self':
        sys.exit()

    if package_name == 'all':
        installed_packages = [f.replace('.json', '') for f in os.listdir(
            PathManager.get_appdata_directory() + r'\Current')]
        for package in installed_packages:
            ctx.invoke(
                up,
                package_name=package,
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
    keyboard.add_hotkey(
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
            pkg['default-install-dir'].replace('<appdata>', os.environ['APPDATA'].replace('\\Roaming', '')) if 'default-install-dir' in list(pkg.keys()) else None, 
            pkg['uninstall'] if 'uninstall' in list(pkg.keys()) else [], 
            pkg['add-path'] if 'add-path' in list(pkg.keys()) else None,
            pkg['checksum'] if 'checksum' in list(pkg.keys()) else None,
        )
        log_info('Generating Packet For Further Installation.', metadata.logfile)
        installed_packages = [f.replace('.json', '').split(
            '@')[:-1] for f in os.listdir(PathManager.get_appdata_directory() + r'\Current')]
        if package in installed_packages:
            if check_newer_version(package, packet):
                install_dir = PathManager.get_appdata_directory() + r'\Current'
                with open(rf'{install_dir}\{package}.json', 'r') as f:
                    data = json.load(f)
                installed_version = data['version']
                if not yes:
                    if not local:
                        continue_update = confirm(
                            f'{package} would be updated from version {installed_version} to {packet.version}')
                    else:
                        write(
                            rf'There is a newer version of {packet.display_name} Availiable ({installed_version}) => ({packet.version})', 'bright_yellow', metadata)
                        sys.exit()
                else:
                    continue_update = True
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
                else:
                    handle_exit('Error', '', metadata)

            else:
                print(f'{package} is already on the latest version')
        else:
            write(f'{packet.display_name} Is Not Installed', 'bright_red', metadata)


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
@click.option('--atom', '-ato', is_flag=True, help='Specify an Atom extension to install')
@click.option('--vscode', '-vs', is_flag=True, help='Specify a Visual Studio Code extension to install')
@click.option('--nightly', '--pre-release', is_flag=True, help='Specify a Visual Studio Code extension to install')
@click.option('--node', '-npm', is_flag=True, help='Specify a Python package to install')
@click.option('--portable', '--non-admin', '-p', is_flag=True, help='Install a portable version of a package')
@click.option('--configuration', '-cf', is_flag=True, help='Specify a config file to install')
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
    configuration: bool,
    portable: bool,
    ae: bool,
    nightly: bool,
    skp: bool,
    manifest: str
):
    """
    Uninstalls a package or a list of packages.
    """

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

    log_info('Generating metadata...', logfile)

    metadata = generate_metadata(
        None, silent, verbose, debug, no_color, yes, logfile, None, None, None, Setting.new(), None)

    log_info('Successfully generated metadata.', logfile)

    log_info('Checking if supercache exists...', metadata.logfile)

    if logfile:
        logfile = logfile.replace('.txt', '.log')
        create_config(logfile, INFO, 'Install')

    if python:
        package_names = package_name.split(',')

        for name in package_names:
            handle_python_package(name, 'latest', 'uninstall', metadata)

        sys.exit()

    if node:
        package_names = package_name.split(',')
        for name in package_names:
            handle_node_package(name, 'uninstall', metadata)

        sys.exit()

    if vscode:
        package_names = package_name.split(',')
        for name in package_names:
            handle_vscode_extension(name, 'uninstall', metadata)

        sys.exit()

    if atom:
        package_names = package_name.split(',')
        for name in package_names:
            handle_atom_package(name, 'uninstall', metadata)

    log_info('Setting up custom `ctrl+c` shortcut.', metadata.logfile)
    status = 'Initializing'
    setup_name = ''
    keyboard.add_hotkey(
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
                write_debug(f'{manifest} FileNotFoundError, Specified Manifest Cannot Be Found!', metadata)
                log_info(f'{manifest} FileNotFoundError, Specified Manifest Cannot Be Found!', metadata.logfile)
                sys.exit(1)

        write(
            f'SuperCached [ {Fore.LIGHTCYAN_EX}{res["display-name"]}{Fore.RESET} ]', 'bright_white', metadata)
        

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
                            write('Uninstallation Must Be Run As Administrator', 'bright_red', metadata)
                            os._exit(1)

                if operation['type'] == 'python':
                    code = ''''''
                    for line in operation['code']:
                        code += line.replace('<display-name>', res['display-name']).replace('<package-name>', res['package-name']).replace('<version>', version) + '\n'
                    exec(code)

                elif operation['type'] == 'powershell' or operation['type'] == 'ps1':
                    with open(rf'{tempfile.gettempdir()}\electric\temp.ps1', 'w+') as f:
                        for line in operation['code']:
                            f.write(line + '\n')
                    os.system(rf'powershell.exe -noprofile -File {tempfile.gettempdir()}\electric\temp.ps1')

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
                handle_exit('ERROR', '', metadata)
        
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
        override_uninstall_switches = pkg['override-default-uninstall-switches'] if 'override-default-uninstall-switches' in list(pkg.keys()) else False
        log_info('Generating Packet For Further Installation.', metadata.logfile)

        handle_portable_uninstallation(version == 'portable', res, pkg, metadata)

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
            res['run-check'] if 'run-check' in list(res.keys()) else True, 
            pkg['set-env'] if 'set-env' in list(pkg.keys()) else None,
            pkg['default-install-dir'].replace('<appdata>', os.environ['APPDATA'].replace('\\Roaming', '')) if 'default-install-dir' in list(pkg.keys()) else None, 
            pkg['uninstall'] if 'uninstall' in list(pkg.keys()) else [], 
            pkg['add-path'] if 'add-path' in list(pkg.keys()) else None,
            pkg['checksum'] if 'checksum' in list(pkg.keys()) else None,
        )

        proc = None
        ftp = ['.msix', '.msixbundle', '.appxbundle', '.appx']
        
        if packet.dependencies:
            handle_uninstall_dependencies(packet.dependencies)

        if packet.win64_type in ftp:
            if find_msix_installation(pkg['uninstall-bundle-identifier']):
                if uninstall_msix(pkg['uninstall-bundle-identifier']) == 0:
                    write(f'Successfully Uninstalled {packet.display_name}', 'bright_green', metadata)
                    sys.exit()

        keyboard.add_hotkey(
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
                pkg['default-install-dir'].replace('<appdata>', os.environ['APPDATA'].replace('\\Roaming', '')) if 'default-install-dir' in list(pkg.keys()) else None, 
                pkg['uninstall'] if 'uninstall' in list(pkg.keys()) else [], 
                pkg['add-path'] if 'add-path' in list(pkg.keys()) else None,
                pkg['checksum'] if 'checksum' in list(pkg.keys()) else None,
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

        write(
            f'{Fore.LIGHTCYAN_EX}Uninstalling {packet.display_name}{Fore.RESET}', 'bright_white', metadata)

        if 'QuietUninstallString' in key:
            command = key['QuietUninstallString']
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
            if run_test:
                packet.run_test = False

            write_verbose('Uninstallation completed.', metadata)
            log_info('Uninstallation completed.', metadata.logfile)

            index += 1

            if not packet.run_test:
                if nightly:
                    packet.version == 'nightly'
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

        # If Only UninstallString Exists (Not Preferable)
        if 'UninstallString' in key:
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

            for switch in packet.uninstall_switches:
                command += f' {switch}'

            # Run The UninstallString
            write_verbose('Executing the Uninstall Command', metadata)
            log_info('Executing the silent Uninstall Command', metadata.logfile)

            run_test = run_cmd(command, metadata, 'uninstallation', packet)
            packet.run_test = False
            write_verbose('Uninstallation completed.', metadata)
            log_info('Uninstallation completed.', metadata.logfile)
            index += 1

            if packet.set_env:
                delete_environment_variable(packet.set_env['name'])

            if not packet.run_test:
                if nightly:
                    packet.version = 'nightly'
                write(
                    f'Running Tests For {packet.display_name}', 'bright_white', metadata)
                if not skp:
                    os.remove(
                        rf'{PathManager.get_appdata_directory()}\Current\{package}@{packet.version}.json')
                
                write(f'[ {Fore.LIGHTGREEN_EX}OK{Fore.RESET} ] Registry Check',
                      'bright_white', metadata)

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
                write(
                    f'Successfully Uninstalled {packet.display_name}', 'bright_magenta', metadata)
                log_info(
                    f'Successfully Uninstalled {packet.display_name}', metadata.logfile)

            write_debug(
                f'Terminated debugger at {strftime("%H:%M:%S")} on uninstall::completion', metadata)
            log_info(
                f'Terminated debugger at {strftime("%H:%M:%S")} on uninstall::completion', metadata.logfile)
            close_log(metadata.logfile, 'Uninstall')

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
                print(f'[ {Fore.LIGHTGREEN_EX}OK{Fore.RESET} ] Registry Check')
                write(
                    f'Successfully Uninstalled {packet.display_name}', 'bright_magenta', metadata)
            else:
                print(f'[ {Fore.LIGHTRED_EX}ERROR{Fore.RESET} ] Registry Check')
                write(f'Failed: Registry Check', 'bright_red', metadata)
                write('Retrying Registry Check In 5 seconds', 'bright_yellow', metadata)
                tm.sleep(5)
                if not find_existing_installation(packet.json_name, packet.display_name):
                    write(
                        f'[ {Fore.LIGHTGREEN_EX}OK{Fore.RESET} ]  Registry Check', 'bright_white', metadata)
                    os.remove(
                        rf'{PathManager.get_appdata_directory()}\Current\{package}@{packet.version}.json')
                    write(
                        f'Successfully Uninstalled {packet.display_name}', 'bright_magenta', metadata)
                    log_info(
                        f'Successfully Uninstalled {packet.display_name}', metadata.logfile)
                else:
                    write(
                        f'Failed To Uninstall {packet.display_name}', 'bright_magenta', metadata)


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
                    os.remove(rf'{tempfile.gettempdir()}\electric\{f}')
                    time.sleep(0.0002)
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
            create_config(logfile, INFO, 'Install')

        log_info('Setting up custom `ctrl+c` shortcut.', metadata.logfile)
        status = 'Initializing'
        setup_name = ''
        keyboard.add_hotkey(
            'ctrl+c', lambda: handle_exit(status, setup_name, metadata))

        log_info('Handling Network Request...', metadata.logfile)
        status = 'Networking'
        write_verbose('Sending GET Request To /bundles', metadata)
        write_debug('Sending GET Request To /bundles', metadata)
        log_info('Sending GET Request To /bundles', metadata.logfile)
        res = send_req_bundle(bundle_name)


        write(f'SuperCached [ {bundle_name} (bundle) ]')

        package_names = ''
        idx = 0

        correct_names = get_correct_package_names(res)

        corrected_package_names = get_autocorrections(
            [bundle_name], correct_names, metadata)

        

        for value in res[corrected_package_names[0]]['dependencies']:
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
            '0001', 'installation', 'None', None, metadata, packet.json_name), metadata)


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
        matches = difflib.get_close_matches(approx_name, correct_names, cutoff=0.7)

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
        click.echo(click.style('0 packages found!', fg='bright_red'))


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
                "# Go To https://www.electric.sh/electric-configuration-documentation/ For More Information\n",
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
    with open(rf'{PathManager.get_appdata_directory()}\electric\Current\{package_name}@{latest_version}.json', 'w+') as f:
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
        os.remove(rf'{PathManager.get_appdata_directory()}\electric\Current\{package_name}@{latest_version}')
    except:
        pass


@cli.command(context_settings=CONTEXT_SETTINGS)
@click.argument('config_path', required=True)
@click.option('--exclude-versions', '-ev', is_flag=True, help='Exclude versions from the config installation')
@click.option('--remove', '-uninst', is_flag=True, help='Uninstall packages in a config installed')
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
    exclude_versions: bool
):
    '''
    Installs and configures packages from a .electric configuration file.
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
    if remove:
        config.uninstall()
    else:
        config.install(exclude_versions, install_directory, sync, metadata)


@cli.command(aliases=['validate'], context_settings=CONTEXT_SETTINGS)
@click.argument('filepath', required=True)
def sign(
    filepath: str
):
    '''
    Signs and validates a .electric configuration file.
    '''
    from Classes.Config import Config

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

    click.echo(click.style(f'Successfully Signed {filepath}', fg='bright_green'))


@cli.command(aliases=['gen'], context_settings=CONTEXT_SETTINGS)
@click.argument('filepath', required=False)
def generate(
    filepath: str
):
    from prompt_toolkit.completion import WordCompleter
    from prompt_toolkit import prompt
    editor_completion = WordCompleter(
        ['Visual Studio Code', 'Sublime Text 3', 'Atom'])
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
    import re

    if installed:
        if not versions:
            try:
                installed_packages = [''.join(f.replace('.json', '').split(
                    '@')[:1]) for f in os.listdir(PathManager.get_appdata_directory() + r'\Current')]
                for package_name in installed_packages:
                    print(package_name)
            except:
                print(f'{Fore.LIGHTYELLOW_EX}No installed packages found{Fore.RESET}')
        else:
            os.chdir(PathManager.get_appdata_directory() + r'\Current')
            try:
                installed_packages = [f.replace('.json', '') for f in os.listdir(
                    PathManager.get_appdata_directory() + r'\Current')]
                for package_name in installed_packages:
                    print(package_name)
            except:
                print(f'{Fore.LIGHTYELLOW_EX}No installed packages found{Fore.RESET}')
    else:
        installed_software = send_query(winreg.HKEY_LOCAL_MACHINE, winreg.KEY_WOW64_32KEY) + send_query(winreg.HKEY_LOCAL_MACHINE, winreg.KEY_WOW64_64KEY) + send_query(winreg.HKEY_CURRENT_USER, 0)
        max_length = 80
        names = [ software['DisplayName'] for software in installed_software ]
        
        versions = []
        for software in installed_software:
            id = re.findall(r'{[A-Z\d-]{36}\}', software['UninstallString'])
            
            version = software['Version']
            versions.append(version)

        print('Name', ' ' * 76, 'Version')
        print('-' * 105)
        
        idx = 0
        for name in names:
            id_length = 90
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
    click.echo(click.style(display_info(res, nightly=nightly), fg='bright_green'))


@cli.command(context_settings=CONTEXT_SETTINGS)
def settings():
    if not os.path.isfile(rf'{PathManager.get_appdata_directory()}\\settings.json'):
        click.echo(click.style(
            f'Creating settings.json at {Fore.LIGHTCYAN_EX}{PathManager.get_appdata_directory()}{Fore.RESET}', fg='bright_green'))
        initialize_settings()
    cursor.hide()
    with Halo('Opening Settings... ', text_color='cyan'):
        open_settings()
    cursor.show()


@cli.command(context_settings=CONTEXT_SETTINGS)
def genpkg():
    package_name = input('Package Name: ')
    display_name = input('Package Display Name: ')
    latest_version = input('Latest Package Version: ')
    package_url = input('Download Url For The Package: ')
    file_type = input('Enter Download File Type: ')
    install_switches = input(
        'Enter the install switches (separated by commas): ')


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
 
    url = data[data['latest-version']]['url']

    webpage = data['auto-update']['vercheck']['webpage']
    
    print(f'{Fore.LIGHTGREEN_EX}Sending Request To {webpage}{Fore.RESET}')
    
    html = swc(webpage.strip())
    show_html = input('Would you like to see the response of the request? [Y/n]: ')
    if show_html == 'y' or show_html == 'Y' or show_html == 'yes' or show_html == 'YES' or show_html == 'Yes':
        print(html)
    
    soup = BeautifulSoup(html, features="html.parser")

    version_list = {}
    
    for tag in soup.find_all('h4', class_='flex-auto min-width-0 pr-2 pb-1 commit-title'):
        if tag:
            try:
                version_list[tag.find('a').text.strip().replace('v', '').replace('V', '')] = int(tag.find('a').text.strip().replace('.', '').replace('v', '').replace('V', ''))
            except:
                pass
    
    print(f'Detected Versions On Webpage:', list(version_list.keys()))
    
    try:
        web_version = max(version_list, key=version_list.get)
    except:
        print(f'{Fore.LIGHTRED_EX}No Versions Detected On Webpage!{Fore.RESET}')
        sys.exit()
    
    print(f'{Fore.LIGHTGREEN_EX}Latest Version Detected:{Fore.RESET} {web_version}')
    
    int_web_version = int(web_version.strip().replace('v', '').replace('V', '').replace('.', ''))

    try:
        int_current_version = int(latest_version.strip().replace('v', '').replace('V', '').replace('.', ''))
    except:
        print(f'{Fore.LIGHTRED_EX}The Current Version Must Not Contain Any Characters')
    
    if int_current_version < int_web_version:
        print(f'A Newer Version Of {package_name} Is Availiable! Updating Manifest')
        current = data
        old_latest = latest_version
        data['latest-version'] = web_version
        data[web_version] = data[old_latest]
        data[web_version]['url'] = data['auto-update']['url'].replace('<version>', web_version)
        colorful_json = highlight(json.dumps(data, indent=4), lexers.JsonLexer(), formatters.TerminalFormatter())
        print(colorful_json)


@cli.command()
@click.option('--word', required=True)
@click.option('--commandline', required=True)
@click.option('--position', required=True)
def complete(
    word: str,
    commandline: str,
    position: str,
):

    n = len(commandline.split(' '))
    if word:
        possibilities = []
        if n == 2:
            possibilities = electric_commands

        if n > 2 and not word.startswith('--') and not (word[0] == '-' and word[1] != '-'):
            with open(rf'{PathManager.get_appdata_directory()}\packages.json', 'r') as f:
                packages = json.load(f)['packages']

            possibilities = difflib.get_close_matches(word, packages)
        elif word.startswith('--') or (word[0] == '-' and word[1] != '-'):
            if word.startswith('--'):
                command = commandline.split(' ')[1]
                if command == 'install' or command == 'bundle' or command == 'i':
                    possibilities = install_flags
                if command == 'uninstall' or command == 'remove' or command == 'u':
                    possibilities = uninstall_flags
                if command == 'search' or command == 'find':
                    possibilities = search_flags
                if command == 'config':
                    possibilities = config_flags
            else:
                pass

        completion = ''

        for command in possibilities:
            if command.startswith(word):
                completion = command
        click.echo(completion)

    else:

        if n == 1:
            for completion in electric_commands:
                click.echo(completion)

        if n >= 3:
            command = commandline.split(' ')[1]

            if command == 'install':
                for completion in install_flags:
                    click.echo(completion)

            if command == 'uninstall':
                for completion in uninstall_flags:
                    click.echo(completion)


if __name__ == '__main__':
    freeze_support()
    cli()  # pylint: disable=no-value-for-parameter

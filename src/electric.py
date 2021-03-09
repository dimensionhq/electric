######################################################################
#                      Copyright 2021 XtremeDevX                     #
#                 SPDX-License-Identifier: Apache-2.0                #
######################################################################

# Install .msixbundle file => Add-AppxPackage Microsoft.WindowsTerminal_0.11.1191.0_8wekyb3d8bbwe.msixbundle
# TODO: Add Conflict-With Field For Json To Differentiate Between Microsoft Visual Studio Code and Microsoft Visual Studio Code Insiders
# TODO: Add option to add a directory to bin

import difflib
import logging
import os
import sys
import time as tm
import click
import halo
import keyboard
from colorama import Fore
from progress.bar import Bar
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter

from Classes.Config import Config
from Classes.Packet import Packet
from Classes.PortablePacket import PortablePacket
from Classes.Setting import Setting
from Classes.ThreadedInstaller import ThreadedInstaller
from cli import SuperChargeCLI
from external import *
from headers import *
from info import __version__
from logger import *
from registry import get_environment_keys, get_uninstall_key
from settings import initialize_settings, open_settings
from utils import *
from zip_uninstall import uninstall_portable

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
            f'Creating settings.json at {Fore.CYAN}{PathManager.get_appdata_directory()}{Fore.RESET}', fg='green'))
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
@click.argument('package_name', required=True)
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
):
    """
    Install a package or a list of packages.
    """
    start_log()

    if plugin:
        if package_name == 'eel':
            os.chdir(PathManager.get_current_directory() + r'\eel')
            os.system('pip install -e .')
            click.echo(
                f'{Fore.GREEN}Successfully Installed eel Plugin, {Fore.CYAN}Refreshing Environment Variables.{Fore.RESET}')
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
        create_config(logfile, logging.INFO, 'Install')

    log_info('Generating metadata...', logfile)

    metadata = generate_metadata(
        no_progress, silent, verbose, debug, no_color, yes, logfile, virus_check, reduce, rate_limit, Setting.new(), sync)

    if update:
        write('Updating Electric', 'green', metadata)
        update_package_list()

    log_info('Successfully generated metadata.', metadata.logfile)

    handle_external_installation(
        python, node, vscode, sublime, atom, version, package_name, metadata)

    log_info('Setting up custom `ctrl+c` shortcut.', metadata.logfile)
    status = 'Initializing'
    setup_name = ''
    keyboard.add_hotkey(
        'ctrl+c', lambda: handle_exit(status, setup_name, metadata))

    # Split the supplied package_name by ,
    # For example : 'sublime-text-3,atom' becomes ['sublime-text-3', 'atom']
    packages = package_name.strip(' ').split(',')

    # Autocorrect all package names provided
    corrected_package_names = list(set(get_autocorrections(
        packages, get_correct_package_names(), metadata)))

    # Write install headers to debug
    write_install_headers(metadata)

    # Handle multi-threaded installation (see function for further clarification)
    handle_multithreaded_installation(
        corrected_package_names, install_directory, metadata)

    # normal non-multi-threaded installation
    for package in corrected_package_names:
        log_info('Handling Network Request...', metadata.logfile)
        status = 'Networking'
        write_verbose('Sending GET Request To /packages/', metadata)
        write_debug('Sending GET Request To /packages', metadata)
        log_info('Sending GET Request To /packages', metadata.logfile)
        log_info('Updating SuperCache', metadata.logfile)
        # request the json response of the package
        res = send_req_package(package)

        res = send_req_package(package)
        log_info('Successfully Updated SuperCache', metadata.logfile)

        pkg = res
        log_info('Generating Packet For Further Installation.', metadata.logfile)

        version = get_package_version(
            pkg, res, version, portable, nightly, metadata)
        pkg = pkg[version]

        install_exit_codes = []

        if 'valid-install-exit-codes' in list(pkg.keys()):
            install_exit_codes = pkg['valid-install-exit-codes']

        handle_portable_installation(portable, pkg, res, metadata)

        packet = Packet(pkg, package, res['display-name'], pkg['url'], pkg['file-type'], pkg['custom-location'], pkg['install-switches'], pkg['uninstall-switches'],
                        install_directory, pkg['dependencies'], install_exit_codes, None, version, res['run-test'] if 'run-test' in list(res.keys()) else True, pkg['set-env'] if 'set-env' in list(pkg.keys()) else None, pkg['default-install-dir'] if 'default-install-dir' in list(pkg.keys()) else None, pkg['uninstall'] if 'uninstall' in list(pkg.keys()) else [])

        write_verbose(
            f'Rapidquery Successfully Received {packet.json_name}.json', metadata)
        write_debug(
            f'Rapidquery Successfully Received {packet.json_name}.json', metadata)
        log_info(
            f'Rapidquery Successfully Received {packet.json_name}.json', metadata.logfile)

        handle_existing_installation(package, packet, force, metadata, ignore)

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

        if not metadata.silent:
            if not metadata.no_color:
                print('SuperCached [', Fore.CYAN +
                      f'{packet.display_name}' + Fore.RESET + ' ]')
            else:
                print(f'SuperCached [ {packet.display_name} ]')

        status = 'Download Path'
        download_url = packet.win64
        status = 'Got Download Path'

        log_info(f'Recieved download path : {download_url}', metadata.logfile)
        log_info('Initializing Rapid Download...', metadata.logfile)

        # Downloading The File From Source
        write_debug(
            f'Downloading {packet.display_name} from => {packet.win64}', metadata)
        write_verbose(
            f"Downloading from '{download_url}'", metadata)
        log_info(f"Downloading from '{download_url}'", metadata.logfile)
        status = 'Downloading'

        path = download_installer(packet, download_url, metadata)

        status = 'Downloaded'

        log_info('Finished Rapid Download', metadata.logfile)

        if virus_check:
            log_info('Running requested virus scanning', metadata.logfile)
            write('Scanning File For Viruses...', 'blue', metadata)
            check_virus(path, metadata)

        write(f'{Fore.CYAN}Installing {packet.display_name}{Fore.RESET}',
              'white', metadata)
        log_info(
            'Using Rapid Install To Complete Setup, Accept Prompts Asking For Admin Permission...', metadata.logfile)

        write_debug(
            f'Installing {packet.json_name} through Setup{packet.win64_type}', metadata)
        log_info(
            f'Installing {packet.json_name} through Setup{packet.win64_type}', metadata.logfile)
        log_info('Creating start snapshot of registry...', metadata.logfile)
        start_snap = get_environment_keys()
        status = 'Installing'
        # Running The Installer silently And Completing Setup
        install_package(path, packet, metadata)

        status = 'Installed'
        log_info('Creating final snapshot of registry...', metadata.logfile)
        final_snap = get_environment_keys()

        if packet.set_env:
            name = packet.set_env['name']
            replace_install_dir = ''
            if packet.directory:
                replace_install_dir = packet.directory
            elif packet.default_install_dir:
                replace_install_dir = packet.default_install_dir

            write(f'Setting Environment Variable {name}', 'green', metadata)
            
            set_environment_variable(
                name, packet.set_env['value'].replace('<install-directory>', replace_install_dir))

        

        if final_snap.env_length > start_snap.env_length or final_snap.sys_length > start_snap.sys_length:
            write('Refreshing Environment Variables', 'green', metadata)
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
            write(
                f'Running Tests For {packet.display_name}', 'white', metadata)
            write(f'[{Fore.GREEN} OK {Fore.RESET}] Registry Check',
                  'white', metadata)
            register_package_success(packet, install_directory, metadata)
            write(
                f'Successfully Installed {packet.display_name}', 'bright_magenta', metadata)
            log_info(
                f'Successfully Installed {packet.display_name}', metadata.logfile)
        else:
            write(
                f'Running Tests For {packet.display_name}', 'white', metadata)
            if find_existing_installation(packet.json_name, packet.display_name):
                write(
                    f'[ {Fore.GREEN}OK{Fore.RESET} ]  Registry Check', 'white', metadata)
                register_package_success(packet, install_directory, metadata)
                write(
                    f'Successfully Installed {packet.display_name}', 'bright_magenta', metadata)
                log_info(
                    f'Successfully Installed {packet.display_name}', metadata.logfile)
            else:
                write(
                    f'[ {Fore.RED}ERROR{Fore.RESET} ] Registry Check', 'red', metadata)
                write('Retrying Registry Check In 5 seconds', 'yellow', metadata)
                tm.sleep(5)
                if find_existing_installation(packet.json_name, packet.display_name):
                    write(
                        f'[ {Fore.GREEN}OK{Fore.RESET} ]  Registry Check', 'white', metadata)
                    register_package_success(
                        packet, install_directory, metadata)
                    write(
                        f'Successfully Installed {packet.display_name}', 'bright_magenta', metadata)
                    log_info(
                        f'Successfully Installed {packet.display_name}', metadata.logfile)
                else:
                    write(
                        f'[ {Fore.RED}ERROR{Fore.RESET} ] Registry Check', 'red', metadata)
                sys.exit()

        if metadata.reduce_package:
            os.remove(f'{path}{packet.win64_type}')
            os.remove(
                Rf'{tempfile.gettempdir()}\electric\downloadcache.pickle')

            log_info(
                'Successfully Cleaned Up Installer From Temporary Directory And DownloadCache', metadata.logfile)
            write('Successfully Cleaned Up Installer From Temp Directory',
                  'green', metadata)

        write_verbose('Installation and setup completed.', metadata)
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
    if package_name == 'electric':
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
        packet = Packet(pkg, package, res['display-name'], pkg['url'], pkg['file-type'], pkg['custom-location'], pkg['install-switches'],
                        pkg['uninstall-switches'], None, pkg['dependencies'], None, [], res['latest-version'], res['run-check'] if 'run-check' in list(res.keys()) else True, pkg['set-env'] if 'set-env' in list(pkg.keys()) else None, pkg['default-install-dir'] if 'default-install-dir' in list(pkg.keys()) else None, pkg['uninstall'] if 'uninstall' in list(pkg.keys()) else [])
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
                        continue_update = click.confirm(
                            f'{package} would be updated from version {installed_version} to {packet.version}')
                    else:
                        write(
                            rf'There is a newer version of {packet.display_name} Availiable ({installed_version}) => ({packet.version})', 'yellow', metadata)
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
                        f'Successfully Updated {package} to latest version.', 'green', metadata)
                else:
                    handle_exit('Error', '', metadata)

            else:
                print(f'{package} is already on the latest version')
        else:
            write(f'{packet.display_name} Is Not Installed', 'red', metadata)


@cli.command(aliases=['remove', 'u'], context_settings=CONTEXT_SETTINGS)
@click.argument('package_name', required=True)
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
):
    """
    Uninstalls a package or a list of packages.
    """
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
        create_config(logfile, logging.INFO, 'Install')

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

    corrected_package_names = get_autocorrections(
        packages, get_correct_package_names(), metadata)
    corrected_package_names = list(set(corrected_package_names))

    write_uninstall_headers(metadata)

    index = 0

    for package in corrected_package_names:
        installed_packages = [''.join(f.replace('.json', '').split(
            '@')[:1]) for f in os.listdir(PathManager.get_appdata_directory() + r'\Current')]
        portable_installed_packages = [''.join(
            f.split('@')[:1]) for f in os.listdir(os.path.expanduser('~') + r'\electric')]
        installed_packages += portable_installed_packages

        res = send_req_package(package)
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
                    f'Could not find any existing installations of {display_name}', 'red', metadata)
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

        uninstall_exit_codes = []
        if 'valid-uninstall-exit-codes' in list(pkg.keys()):
            uninstall_exit_codes = pkg['valid-install-exit-codes']

        name = pkg['display-name']
        pkg = pkg[version]

        log_info('Generating Packet For Further Installation.', metadata.logfile)

        if portable and not 'is-portable' in list(res.keys()):
            keys = list(pkg[pkg['latest-version']].keys())

            data = {
                'display-name': pkg['display-name'],
                'package-name': pkg['package-name'],
                'latest-version': pkg['latest-version'],
                'url': pkg[pkg['latest-version']]['url'],
                'file-type': pkg[pkg['latest-version']]['file-type'] if 'file-type' in keys else None,
                'extract-dir': pkg[pkg['latest-version']]['extract-dir'],
                'chdir': pkg[pkg['latest-version']]['chdir'] if 'chdir' in keys else None,
                'bin': pkg[pkg['latest-version']]['bin'] if 'bin' in keys else None,
                'install-notes': pkg[pkg['latest-version']]['install-notes'] if 'install-notes' in keys else None,
                'uninstall-notes': pkg[pkg['latest-version']]['uninstall-notes'] if 'uninstall-notes' in keys else None,
                'shortcuts': pkg[pkg['latest-version']]['shortcuts'] if 'shortcuts' in keys else None,
                'post-install': pkg[pkg['latest-version']]['post-install'] if 'post-install' in keys else None,
                'persist': pkg[pkg['latest-version']]['persist'] if 'presist' in keys else None,
            }

            portable_packet = PortablePacket(data)
            start = timer()
            uninstall_portable(portable_packet, metadata)
            end = timer()
            sys.exit()

        elif portable and 'is-portable' in list(res.keys()):
            keys = list(pkg[pkg['latest-version']].keys())
            data = {
                'display-name': pkg['display-name'],
                'package-name': pkg['package-name'],
                'latest-version': pkg['latest-version'],
                'url': pkg[pkg['latest-version']]['url'],
                'file-type': pkg[pkg['latest-version']]['file-type'],
                'extract-dir': pkg[pkg['latest-version']]['extract-dir'],
                'chdir': pkg[pkg['latest-version']]['chdir'] if 'chdir' in keys else [],
                'bin': pkg[pkg['latest-version']]['bin'] if 'bin' in keys else [],
                'shortcuts': pkg[pkg['latest-version']]['shortcuts'] if 'shortcuts' in keys else [],
                'install-notes': pkg[pkg['latest-version']]['install-notes'] if 'install-notes' in keys else None,
                'uninstall-notes': pkg[pkg['latest-version']]['uninstall-notes'] if 'uninstall-notes' in keys else None,
                'post-install': pkg[pkg['latest-version']]['post-install'] if 'post-install' in keys else [],
                'install-notes': pkg[pkg['latest-version']]['install-notes'] if 'install-notes' in keys else None,
                'uninstall-notes': pkg[pkg['latest-version']]['uninstall-notes'] if 'uninstall-notes' in keys else None,
                'persist': pkg[pkg['latest-version']]['persist'] if 'presist' in keys else None,
            }
            portable_packet = PortablePacket(data)
            uninstall_portable(portable_packet, metadata)
            sys.exit()

        packet = Packet(pkg, package, name, pkg['url'], pkg['file-type'], pkg['custom-location'], pkg['install-switches'], pkg['uninstall-switches'],
                        None, pkg['dependencies'], None, uninstall_exit_codes, version, res['run-check'] if 'run-check' in list(res.keys()) else True, pkg['set-env'] if 'set-env' in list(pkg.keys()) else None, pkg['default-install-dir'] if 'default-install-dir' in list(pkg.keys()) else None, pkg['uninstall'] if 'uninstall' in list(pkg.keys()) else [])
        proc = None
        keyboard.add_hotkey(
            'ctrl+c', lambda: kill_proc(proc, metadata))

        write(
            f'SuperCached [ {Fore.CYAN}{packet.display_name}{Fore.RESET} ]', 'white', metadata)
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
            packet = Packet(pkg, package, name, pkg['url'], pkg['file-type'], pkg['custom-location'], pkg['install-switches'], pkg['uninstall-switches'],
                            None, pkg['dependencies'], None, uninstall_exit_codes, version, res['run-check'] if 'run-check' in list(res.keys()) else True, pkg['set-env'] if 'set-env' in list(pkg.keys()) else None, pkg['default-install-dir'] if 'default-install-dir' in list(pkg.keys()) else None, pkg['uninstall'] if 'uninstall' in list(pkg.keys()) else [])

            write(
                f'Could not find any existing installations of {packet.display_name}', 'red', metadata)
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
                f'Successfully Retrieved Uninstall Key In {round(end - start, 4)}s', 'green', metadata)
            log_info(
                f'Successfully Retrieved Uninstall Key In {round(end - start, 4)}s', metadata.logfile)

        command = ''

        # Key Can Be A List Or A Dictionary Based On Results

        if isinstance(key, list):
            if key:
                key = key[0]

        write(
            f'{Fore.CYAN}Uninstalling {packet.display_name}{Fore.RESET}', 'white', metadata)
        if 'QuietUninstallString' in key:
            command = key['QuietUninstallString']
            command = command.replace('/I', '/X')
            command = command.replace('/quiet', '/qn')

            additional_switches = None
            if packet.uninstall_switches:
                if packet.uninstall_switches != []:
                    write_verbose(
                        'Adding additional uninstall switches', metadata)
                    write_debug(
                        'Appending / Adding additional uninstallation switches', metadata)
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
                    f'Running Tests For {packet.display_name}', 'white', metadata)
                if not skp:
                    os.remove(
                        rf'{PathManager.get_appdata_directory()}\Current\{package}@{packet.version}.json')
                
                write(f'[ {Fore.GREEN}OK{Fore.RESET} ] Registry Check',
                      'white', metadata)

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
                f'Running Tests For {packet.display_name}', 'white', metadata)
            if not find_existing_installation(packet.json_name, packet.display_name):
                if nightly:
                    os.remove(
                        rf'{PathManager.get_appdata_directory()}\Current\{package}@nightly.json')
                else:
                    os.remove(
                        rf'{PathManager.get_appdata_directory()}\Current\{package}@{packet.version}.json')
                print(f'[ {Fore.GREEN}OK{Fore.RESET} ] Registry Check')
                write(
                    f'Successfully Uninstalled {packet.display_name}', 'bright_magenta', metadata)
            else:
                print(f'[ {Fore.RED}ERROR{Fore.RESET} ] Registry Check')
                write(f'Failed: Registry Check', 'red', metadata)
                write('Retrying Registry Check In 5 seconds', 'yellow', metadata)
                tm.sleep(5)
                if not find_existing_installation(packet.json_name, packet.display_name):
                    write(
                        f'[ {Fore.GREEN}OK{Fore.RESET} ]  Registry Check', 'white', metadata)
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
    with Halo('Cleaning Up ', text_color='green') as h:
        try:
            files = os.listdir(rf'{tempfile.gettempdir()}\electric')
        except:
            os.mkdir(rf'{tempfile.gettempdir()}\electric')
            h.stop()
            click.echo(click.style('Nothing To Cleanup!', 'cyan'))
            sys.exit()

        if len(files) == 0:
            h.stop()
            click.echo(click.style('Nothing To Cleanup!', 'cyan'))

        else:
            h.stop()
            with Bar(f'{Fore.CYAN}Deleting Temporary Files{Fore.RESET}', max=len(files), bar_prefix=' [ ', bar_suffix=' ] ', fill=f'{Fore.GREEN}={Fore.RESET}', empty_fill=f'{Fore.LIGHTBLACK_EX}-{Fore.RESET}') as b:
                for f in files:
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
    Installs a bunlde of packages from the official electric repository.
    """
    metadata = generate_metadata(
        no_progress, silent, verbose, debug, no_color, yes, logfile, virus_check, reduce, rate_limit, Setting.new(), sync)

    if is_admin():
        if logfile:
            logfile = logfile.replace('=', '')
            logfile = logfile.replace('.txt', '.log')
            create_config(logfile, logging.INFO, 'Install')

        log_info('Setting up custom `ctrl+c` shortcut.', metadata.logfile)
        status = 'Initializing'
        setup_name = ''
        keyboard.add_hotkey(
            'ctrl+c', lambda: handle_exit(status, setup_name, metadata))

        spinner = halo.Halo(color='grey')
        spinner.start()
        log_info('Handling Network Request...', metadata.logfile)
        status = 'Networking'
        write_verbose('Sending GET Request To /bundles', metadata)
        write_debug('Sending GET Request To /bundles', metadata)
        log_info('Sending GET Request To /bundles', metadata.logfile)
        res = send_req_bundle()
        del res['_id']
        spinner.stop()
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
            '\nAdministrator Elevation Required. Exit Code [0001]', 'red'), err=True)
        disp_error_msg(get_error_message(
            '0001', 'installation', 'None', None), metadata)


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
        matches = difflib.get_close_matches(approx_name, correct_names)

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
                f'{len(matches)} packages found.', fg='green'))
        else:
            click.echo(click.style('1 package found.', fg='yellow'))

    else:
        click.echo(click.style('0 packages found!', fg='red'))


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
        f'Successfully Created {Fore.LIGHTBLUE_EX}`{project_name}.electric`{Fore.GREEN} at {os.getcwd()}\\', 'green'))


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
    config = Config.generate_configuration(filepath, False)
    click.echo(click.style('No syntax errors found!', 'green'))

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
                'File Already Signed, Aborting Signing!', fg='red'))
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

    click.echo(click.style(f'Successfully Signed {filepath}', fg='green'))


@cli.command(aliases=['gen'], context_settings=CONTEXT_SETTINGS)
@click.argument('filepath', required=False)
def generate(
    filepath: str
):

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
        include_editor = click.confirm(
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
            include_python = click.confirm(
                'Would you like to include your Python Configuration?')
    except FileNotFoundError:
        pass

    include_npm = None
    try:
        proc = Popen('npm --version', stdin=PIPE,
                     stdout=PIPE, stderr=PIPE, shell=True)
        _, err = proc.communicate()
        if not err:
            include_npm = click.confirm(
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
    if installed:
        if not versions:
            try:
                installed_packages = [''.join(f.replace('.json', '').split(
                    '@')[:1]) for f in os.listdir(PathManager.get_appdata_directory() + r'\Current')]
                for package_name in installed_packages:
                    print(package_name)
            except:
                print(f'{Fore.YELLOW}No installed packages found{Fore.RESET}')
        else:
            os.chdir(PathManager.get_appdata_directory() + r'\Current')
            try:
                installed_packages = [f.replace('.json', '') for f in os.listdir(
                    PathManager.get_appdata_directory() + r'\Current')]
                for package_name in installed_packages:
                    print(package_name)
            except:
                print(f'{Fore.YELLOW}No installed packages found{Fore.RESET}')
    else:
        with open(f'{PathManager.get_appdata_directory()}\packages.json', 'r') as f:
            data = json.load(f)
        packages = data['packages'][:99]
        print(f'Found {Fore.GREEN}{len(packages)}{Fore.RESET} packages')
        for package_name in packages:
            print(package_name)


@cli.command(aliases=['info'], context_settings=CONTEXT_SETTINGS)
@click.option('--nightly', '--pre-release', is_flag=True, help='Show a nightly or pre-release build of a package')
@click.argument('package_name', required=True)
def show(package_name: str, nightly: bool):
    '''
    Displays information about the specified package.
    '''
    res = send_req_package(package_name)
    click.echo(click.style(display_info(res, nightly=nightly), fg='green'))


@cli.command(context_settings=CONTEXT_SETTINGS)
def settings():
    if not os.path.isfile(rf'{PathManager.get_appdata_directory()}\\settings.json'):
        click.echo(click.style(
            f'Creating settings.json at {Fore.CYAN}{PathManager.get_appdata_directory()}{Fore.RESET}', fg='green'))
        initialize_settings()
    cursor.hide()
    with Halo('Opening Settings... ', text_color='blue'):
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
    cli()  # pylint: disable=no-value-for-parameter

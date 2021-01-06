######################################################################
#                            ELECTRIC CLI                            #
######################################################################


import difflib
import logging
import os
import sys
from itertools import zip_longest
from timeit import default_timer as timer
from urllib.request import urlretrieve

import click
import halo
import keyboard
from colorama import *
from progress.bar import Bar
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter

from decimal import Decimal
from Classes.Config import Config
from Classes.PackageManager import PackageManager
from Classes.Packet import Packet
from Classes.Setting import Setting
from cli import SuperChargeCLI
from constants import *
from external import *
from info import __version__
from limit import Limiter, TokenBucket
from logger import *
from registry import get_environment_keys, get_uninstall_key
from settings import initialize_settings, open_settings
from utils import *

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help', '-?'])

@click.group(cls=SuperChargeCLI)
@click.version_option(__version__)
@click.pass_context
def cli(_):
    if not os.path.isfile(rf'{PathManager.get_appdata_directory()}\\electric-settings.json'):
        click.echo(click.style(f'Creating electric-settings.json at {Fore.CYAN}{PathManager.get_appdata_directory()}{Fore.RESET}', fg='green'))
        initialize_settings()
    setup_supercache()


@cli.command(aliases=['i'], context_settings=CONTEXT_SETTINGS)
@click.argument('package_name', required=True)
@click.option('--version', '-v', type=str, help='Install a certain version of a package')
@click.option('--nightly', '--pre-release', is_flag=True, help='Install a nightly or pre-release build of a package')
@click.option('--verbose', '-vb', is_flag=True, help='Enable verbose mode for installation')
@click.option('--debug', '-d', is_flag=True, help='Enable debug mode for installation')
@click.option('--no-progress', '-np', is_flag=True, default=False, help='Disable progress bar for installation')
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
@click.option('--node', '-npm', is_flag=True, help='Specify a Python package to install')
@click.option('--no-cache', '-nocache', is_flag=True, help='Specify a Python package to install')
@click.option('--sync', '-sc', is_flag=True, help='Force downloads and installations one after another')
@click.option('--reduce', '-rd', is_flag=True, help='Cleanup all traces of package after installation')
@click.option('--rate-limit', '-rl', type=int, default=-1)
@click.option('--force', '-f', is_flag=True, help='Force install a package, ignoring any existing installations of a package.')
@click.option('--configuration', '-cf', is_flag=True, help='Specify a config file to install')
@click.option('--plugin', '-pl', is_flag=True, help='Specify a plugin to install')
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
    install_directory: str,
    virus_check: bool,
    no_cache: bool,
    sync: bool,
    reduce: bool,
    rate_limit: int,
    node: bool,
    vscode: bool,
    atom: bool,
    sublime:bool,
    force: bool,
    configuration: bool,
    version: str,
    nightly: bool,
    plugin: bool
):
    """
    Installs a package or a list of packages.
    """
    if plugin:
        if package_name == 'eel':
            os.chdir(PathManager.get_current_directory() + r'\eel')
            os.system('pip install -e .')
            click.echo(f'{Fore.GREEN}Successfully Installed eel Plugin, {Fore.CYAN}Refreshing Environment Variables.{Fore.RESET}')
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
            no_cache=no_cache,
            sync=sync,
            reduce=reduce,
            rate_limit=rate_limit
        )
        exit()

    if logfile:
        logfile = logfile.replace('=', '')
        logfile = logfile.replace('.txt', '.log')
        create_config(logfile, logging.INFO, 'Install')

    log_info('Generating metadata...', logfile)
    metadata = generate_metadata(
        no_progress, silent, verbose, debug, no_color, yes, logfile, virus_check, reduce, rate_limit, Setting.new())
    log_info('Successfully generated metadata.', metadata.logfile)

    if python:
        if not version:
            version = 'latest'
        package_names = package_name.split(',')

        for name in package_names:
            handle_python_package(name, version, 'install', metadata)

        sys.exit()

    if node:
        package_names = package_name.split(',')
        for name in package_names:
            handle_node_package(name, 'install', metadata)

        sys.exit()

    if vscode:
        package_names = package_name.split(',')
        for name in package_names:
            handle_vscode_extension(name, 'install', metadata)

        sys.exit()

    if sublime:
        package_names = package_name.split(',')
        for name in package_names:
            handle_sublime_extension(name, 'install', metadata)
        sys.exit()

    if atom:
        package_names = package_name.split(',')
        for name in package_names:
            handle_atom_package(name, 'install', metadata)
        sys.exit()

    log_info('Checking if supercache exists...', metadata.logfile)
    super_cache = check_supercache_valid()
    if super_cache:
        log_info('Supercache detected.', metadata.logfile)
    if no_cache:
        log_info('Overriding SuperCache To FALSE', metadata.logfile)
        super_cache = False
    if not super_cache:
        update_supercache(metadata)

    log_info('Setting up custom `ctrl+c` shortcut.', metadata.logfile)
    status = 'Initializing'
    setup_name = ''
    # keyboard.add_hotkey(
    #     'ctrl+c', lambda: handle_exit(status, setup_name, metadata))

    packages = package_name.strip(' ').split(',')

    corrected_package_names = get_autocorrections(packages, get_correct_package_names(), metadata)

    write_debug(install_debug_headers, metadata)
    for header in install_debug_headers:
        log_info(header, metadata.logfile)

        index = 0

    def grouper(iterable, n, fillvalue=None):
        "Collect data into fixed-length chunks or blocks"
        # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx"
        args = [iter(iterable)] * n
        return zip_longest(*args, fillvalue=fillvalue)

    if not sync:
        if len(corrected_package_names) > 1:
            split_package_names = list(grouper(corrected_package_names, 3))
            if len(split_package_names) == 1:
                packets = []
                for package in corrected_package_names:
                    if super_cache:
                        log_info('Handling SuperCache Request.', metadata.logfile)
                        res, time = handle_cached_request(package)
                    else:
                        spinner = halo.Halo(color='grey')
                        spinner.start()
                        log_info('Handling Network Request...', metadata.logfile)
                        status = 'Networking'
                        write_verbose('Sending GET Request To /packages/', metadata)
                        write_debug('Sending GET Request To /packages', metadata)
                        log_info('Sending GET Request To /packages', metadata.logfile)
                        res, time = send_req_package(package)
                        log_info('Updating SuperCache', metadata.logfile)
                        update_supercache(metadata)
                        log_info('Successfully Updated SuperCache', metadata.logfile)
                        spinner.stop()

                    pkg = res
                    custom_dir = None
                    if install_directory:
                        custom_dir = install_directory + f'\\{pkg["package-name"]}'
                    else:
                        custom_dir = install_directory
                    keys = list(pkg.keys())
                    idx = 0
                    for key in keys:
                        if key not in ['package-name', 'nightly', 'display-name']:
                            idx = keys.index(key)
                            break
                    version = keys[idx]
                    pkg = pkg[version]
                    install_exit_codes = None
                    if 'valid-install-exit-codes' in list(pkg.keys()):
                        install_exit_codes = pkg['valid-install-exit-codes']
                    packet = Packet(pkg, package, res['display-name'], pkg['win64'], pkg['win64-type'], pkg['custom-location'], pkg['install-switches'], pkg['uninstall-switches'], custom_dir, pkg['dependencies'], install_exit_codes, None, version)
                    installation = find_existing_installation(
                        package, packet.display_name)
                    if installation:
                        write_debug(
                            f'Aborting Installation As {packet.json_name} is already installed.', metadata)
                        write_verbose(
                            f'Found an existing installation of => {packet.json_name}', metadata)
                        write(
                            f'Found an existing installation {packet.display_name}.', 'yellow', metadata)
                        installation_continue = click.confirm(
                            f'Would you like to reinstall {packet.json_name}')

                        if installation_continue or yes:
                            os.system(f'electric uninstall {packet.json_name}')
                            os.system(f'electric install {packet.json_name}')
                            return
                        else:
                            handle_exit(status, setup_name, metadata)

                    write_verbose(
                        f'Package to be installed: {packet.json_name}', metadata)
                    log_info(
                        f'Package to be installed: {packet.json_name}', metadata.logfile)

                    write_verbose(
                        f'Finding closest match to {packet.json_name}...', metadata)
                    log_info(
                        f'Finding closest match to {packet.json_name}...', metadata.logfile)
                    packets.append(packet)

                    write_verbose('Generating system download path...', metadata)
                    log_info('Generating system download path...', metadata.logfile)

                manager = PackageManager(packets, metadata)
                paths = manager.handle_multi_download()
                cursor.show()
                log_info('Finished Rapid Download...', metadata.logfile)
                log_info(
                    f'Running {packet.display_name} Installer, Accept Prompts Requesting Administrator Permission', metadata.logfile)
                manager.handle_multi_install(paths)
                return
            elif len(split_package_names) > 1:
                for package_batch in split_package_names:
                    package_batch = list(package_batch)
                    package_batch = [x for x in package_batch if x is not None]
                    if len(package_batch) == 1:
                        package = package_batch[0]
                        if super_cache:
                            log_info('Handling SuperCache Request.', metadata.logfile)
                            res, time = handle_cached_request(package)
                        else:
                            spinner = halo.Halo(color='grey')
                            spinner.start()
                            log_info('Handling Network Request...', metadata.logfile)
                            status = 'Networking'
                            write_verbose('Sending GET Request To /packages/', metadata)
                            write_debug('Sending GET Request To /packages', metadata)
                            log_info('Sending GET Request To /packages', metadata.logfile)
                            res, time = send_req_package(package)
                            log_info('Updating SuperCache', metadata.logfile)
                            update_supercache(metadata)
                            log_info('Successfully Updated SuperCache', metadata.logfile)
                            spinner.stop()

                        pkg = res
                        keys = list(pkg.keys())
                        idx = 0
                        for key in keys:
                            if key not in ['package-name', 'nightly', 'display-name']:
                                idx = keys.index(key)
                                break
                        version = keys[idx]
                        pkg = pkg[version]
                        log_info('Generating Packet For Further Installation.', metadata.logfile)

                        install_exit_codes = None
                        if 'valid-install-exit-codes' in list(pkg.keys()):
                            install_exit_codes = pkg['valid-install-exit-codes']

                        packet = Packet(pkg, package, res['display-name'], pkg['win64'], pkg['win64-type'], pkg['custom-location'], pkg['install-switches'], pkg['uninstall-switches'], install_directory, pkg['dependencies'], install_exit_codes, None, version)
                        log_info('Searching for existing installation of package.', metadata.logfile)

                        installation = find_existing_installation(package, packet.json_name)

                        if installation:
                            write_debug(
                                f'Found existing installation of {packet.json_name}.', metadata)
                            write_verbose(
                                f'Found an existing installation of => {packet.json_name}', metadata)
                            write(
                                f'Detected an existing installation {packet.display_name}.', 'yellow', metadata)
                            installation_continue = click.confirm(
                                f'Would you like to reinstall {packet.display_name}')
                            if installation_continue or yes:
                                os.system(f'electric uninstall {packet.json_name}')
                                os.system(f'electric install {packet.json_name}')
                                return
                            else:
                                handle_exit(status, setup_name, metadata)

                        if packet.dependencies:
                            PackageManager.install_dependent_packages(packet, rate_limit, install_directory, metadata)

                        write_verbose(
                            f'Package to be installed: {packet.json_name}', metadata)
                        log_info(f'Package to be installed: {packet.json_name}', metadata.logfile)

                        write_verbose(
                            f'Finding closest match to {packet.json_name}...', metadata)
                        log_info(f'Finding closest match to {packet.json_name}...', metadata.logfile)

                        if index == 0:
                            if super_cache:
                                write_verbose(
                                    f'Rapidquery Successfully SuperCached {packet.json_name} in {round(time, 6)}s', metadata)
                                write_debug(
                                    f'Rapidquery Successfully SuperCached {packet.json_name} in {round(time, 6)}s', metadata)
                                log_info(f'Rapidquery Successfully SuperCached {packet.json_name} in {round(time, 6)}s', metadata.logfile)
                            else:
                                write_verbose(
                                    f'Rapidquery Successfully Received {packet.json_name}.json in {round(time, 6)}s', metadata)
                                write_debug(
                                    f'Rapidquery Successfully Received {packet.json_name}.json in {round(time, 6)}s', metadata)
                                log_info(
                                    f'Rapidquery Successfully Received {packet.json_name}.json in {round(time, 6)}s', metadata.logfile)

                        write_verbose('Generating system download path...', metadata)
                        log_info('Generating system download path...', metadata.logfile)

                        if not metadata.silent:
                            if not metadata.no_color:
                                if super_cache:
                                    print('SuperCached', Fore.GREEN + '=>' + Fore.RESET, '[', Fore.CYAN +  f'{packet.display_name}' + Fore.RESET + ' ]')
                                else:
                                    print('Recieved => [', Fore.CYAN +  f'{packet.display_name}' + Fore.RESET + ' ]')

                            else:
                                print(f'Found => [ {packet.display_name} ]')
                        start = timer()

                        status = 'Download Path'
                        download_url = get_download_url(packet)
                        status = 'Got Download Path'
                        end = timer()

                        log_info('Initializing Rapid Download...', metadata.logfile)

                        # Downloading The File From Source
                        write_debug(f'Downloading {packet.display_name} from => {packet.win64}', metadata)
                        write_verbose(
                            f"Downloading from '{download_url}'", metadata)
                        log_info(f"Downloading from '{download_url}'", metadata.logfile)
                        status = 'Downloading'

                        if rate_limit == -1:
                            start = timer()
                            path, cached = download(download_url, packet.json_name, metadata, packet.win64_type)
                            end = timer()
                        else:
                            log_info(f'Starting rate-limited installation => {rate_limit}', metadata.logfile)
                            bucket = TokenBucket(tokens=10 * rate_limit, fill_rate=rate_limit)

                            limiter = Limiter(
                                bucket=bucket,
                                filename=f'{tempfile.gettempdir()}\Setup{packet.win64_type}',
                            )

                            urlretrieve(
                                url=download_url,
                                filename=f'{tempfile.gettempdir()}\Setup{packet.win64_type}',
                                reporthook=limiter
                            )

                            path = f'{tempfile.gettempdir()}\Setup{packet.win64_type}'

                        status = 'Downloaded'

                        log_info('Finished Rapid Download', metadata.logfile)

                        if virus_check:
                            with Halo('\nScanning File For Viruses...', text_color='blue'):
                                check_virus(path, metadata)
                        if not cached:
                            write(
                                f'\nInstalling {packet.display_name}', 'cyan', metadata)
                        else:
                            write(
                                f'Installing {packet.display_name}', 'cyan', metadata)
                        log_info(
                            f'Running {packet.display_name} Installer, Accept Prompts Requesting Administrator Permission', metadata.logfile)

                        write_debug(
                            f'Installing {packet.json_name} through Setup{packet.win64_type}', metadata)
                        log_info(
                            f'Installing {packet.json_name} through Setup{packet.win64_type}', metadata.logfile)
                        start_snap = get_environment_keys()
                        status = 'Installing'
                        # Running The Installer silently And Completing Setup
                        install_package(path, packet, metadata)

                        status = 'Installed'
                        final_snap = get_environment_keys()
                        if final_snap.env_length > start_snap.env_length or final_snap.sys_length > start_snap.sys_length:
                            write('Refreshing Environment Variables...', 'green', metadata)
                            start = timer()
                            log_info('Refreshing Environment Variables At scripts/refreshvars.cmd', metadata.logfile)
                            write_debug('Refreshing Env Variables, Calling Batch Script At scripts/refreshvars.cmd', metadata)
                            write_verbose('Refreshing Environment Variables', metadata)
                            refresh_environment_variables()
                            end = timer()
                            write_debug(f'Successfully Refreshed Environment Variables in {round(end - start)} seconds', metadata)

                        write(
                            f'Successfully Installed {packet.display_name}!', 'bright_magenta', metadata)
                        log_info(f'Successfully Installed {packet.display_name}!', metadata.logfile)


                        if metadata.reduce_package:

                            os.remove(path)
                            try:
                                os.remove(Rf'{tempfile.gettempdir()}\downloadcache.pickle')
                            except:
                                pass

                            log_info('Successfully Cleaned Up Installer From Temporary Directory And DownloadCache', metadata.logfile)
                            write('Successfully Cleaned Up Installer From Temp Directory...',
                                'green', metadata)

                        write_verbose('Installation and setup completed.', metadata)
                        log_info('Installation and setup completed.', metadata.logfile)
                        write_debug(
                            f'Terminated debugger at {strftime("%H:%M:%S")} on install::completion', metadata)
                        log_info(
                            f'Terminated debugger at {strftime("%H:%M:%S")} on install::completion', metadata.logfile)
                        close_log(metadata.logfile, 'Install')
                        return

                    packets = []
                    for package in package_batch:
                        if super_cache:
                            log_info('Handling SuperCache Request.', metadata.logfile)
                            res, time = handle_cached_request(package)
                        else:
                            spinner = halo.Halo(color='grey')
                            spinner.start()
                            log_info('Handling Network Request...', metadata.logfile)
                            status = 'Networking'
                            write_verbose('Sending GET Request To /packages/', metadata)
                            write_debug('Sending GET Request To /packages', metadata)
                            log_info('Sending GET Request To /packages', metadata.logfile)
                            res, time = send_req_package(package)
                            log_info('Updating SuperCache', metadata.logfile)
                            update_supercache(metadata)
                            log_info('Successfully Updated SuperCache', metadata.logfile)
                            spinner.stop()

                        pkg = res
                        custom_dir = None
                        if install_directory:
                            custom_dir = install_directory + f'\\{pkg["package-name"]}'
                        else:
                            custom_dir = install_directory
                        keys = list(pkg.keys())
                        idx = 0
                        for key in keys:
                            if key not in ['package-name', 'nightly', 'display-name']:
                                idx = keys.index(key)
                                break
                        version = keys[idx]
                        pkg = pkg[version]
                        install_exit_codes = None
                        if 'valid-install-exit-codes' in list(pkg.keys()):
                            install_exit_codes = pkg['valid-install-exit-codes']
                        packet = Packet(pkg, package, res['display-name'], pkg['win64'], pkg['win64-type'], pkg['custom-location'], pkg['install-switches'], pkg['uninstall-switches'], custom_dir, pkg['dependencies'], install_exit_codes, None, version)
                        installation = find_existing_installation(
                            package, packet.display_name)
                        if installation:
                            write_debug(
                                f'Aborting Installation As {packet.json_name} is already installed.', metadata)
                            write_verbose(
                                f'Found an existing installation of => {packet.json_name}', metadata)
                            write(
                                f'Found an existing installation {packet.json_name}.', 'bright_yellow', metadata)
                            installation_continue = click.confirm(
                                f'Would you like to reinstall {packet.json_name}')
                            if installation_continue or yes:
                                os.system(f'electric uninstall {packet.json_name}')
                                os.system(f'electric install {packet.json_name}')
                                return
                            else:
                                handle_exit(status, setup_name, metadata)

                        write_verbose(
                            f'Package to be installed: {packet.json_name}', metadata)
                        log_info(
                            f'Package to be installed: {packet.json_name}', metadata.logfile)

                        write_verbose(
                            f'Finding closest match to {packet.json_name}...', metadata)
                        log_info(
                            f'Finding closest match to {packet.json_name}...', metadata.logfile)
                        packets.append(packet)

                        write_verbose('Generating system download path...', metadata)
                        log_info('Generating system download path...', metadata.logfile)

                    manager = PackageManager(packets, metadata)
                    paths = manager.handle_multi_download()
                    log_info('Finished Rapid Download...', metadata.logfile)
                    log_info(
                        'Using Rapid Install To Complete Setup, Accept Prompts Asking For Admin Permission...', metadata.logfile)
                    manager.handle_multi_install(paths)
                return

    for package in corrected_package_names:
        supercache_availiable = check_supercache_availiable(package)

        if super_cache and supercache_availiable and not no_cache:
            log_info('Handling SuperCache Request.', metadata.logfile)
            res, time = handle_cached_request(package)

        else:
            if not silent:
                spinner = halo.Halo(color='grey' if not no_color else 'white')
                spinner.start()
            log_info('Handling Network Request...', metadata.logfile)
            status = 'Networking'
            write_verbose('Sending GET Request To /packages/', metadata)
            write_debug('Sending GET Request To /packages', metadata)
            log_info('Sending GET Request To /packages', metadata.logfile)
            log_info('Updating SuperCache', metadata.logfile)
            res, time = send_req_package(package)
            log_info('Successfully Updated SuperCache', metadata.logfile)
            if not silent:
                spinner.stop()

        pkg = res
        log_info('Generating Packet For Further Installation.', metadata.logfile)
        keys = list(pkg.keys())
        idx = 0

        if not version:
            for key in keys:
                if key not in ['package-name', 'nightly', 'display-name']:
                    idx = keys.index(key)
                    break
            version = keys[idx]

        if nightly:
            version = 'nightly'
        try:
            pkg = pkg[version]
        except KeyError:
            name = res['display-name']
            write(f'\nCannot Find {name}::v{version}', 'red', metadata)
            handle_exit('ERROR', None, metadata)
        install_exit_codes = None

        if 'valid-install-exit-codes' in list(pkg.keys()):
            install_exit_codes = pkg['valid-install-exit-codes']

        packet = Packet(pkg, package, res['display-name'], pkg['win64'], pkg['win64-type'], pkg['custom-location'], pkg['install-switches'], pkg['uninstall-switches'], install_directory, pkg['dependencies'], install_exit_codes, None, version)
        log_info('Searching for existing installation of package.', metadata.logfile)

        log_info('Finding existing installation of package...', metadata.logfile)
        installation = find_existing_installation(package, packet.json_name)

        if installation and not force:
            log_info('Found existing installation of package...', metadata.logfile)
            write_debug(
                f'Found existing installation of {packet.json_name}.', metadata)
            write_verbose(
                f'Found an existing installation of => {packet.json_name}', metadata)
            write(
                f'Detected an existing installation {packet.display_name}.', 'yellow', metadata)
            installation_continue = click.confirm(
                f'Would you like to reinstall {packet.display_name}?')
            if installation_continue or yes:
                os.system(f'electric uninstall {packet.json_name}')
                os.system(f'electric install {packet.json_name}')
                return
            else:
                handle_exit(status, setup_name, metadata)

        if packet.dependencies:
            PackageManager.install_dependent_packages(packet, rate_limit, install_directory, metadata)

        write_verbose(
            f'Package to be installed: {packet.json_name}', metadata)
        log_info(f'Package to be installed: {packet.json_name}', metadata.logfile)

        write_verbose(
            f'Finding closest match to {packet.json_name}...', metadata)
        log_info(f'Finding closest match to {packet.json_name}...', metadata.logfile)

        if index == 0:
            if super_cache:
                write_verbose(
                    f'Rapidquery Successfully SuperCached {packet.json_name} in {round(time, 6)}s', metadata)
                write_debug(
                    f'Rapidquery Successfully SuperCached {packet.json_name} in {round(time, 6)}s', metadata)
                log_info(f'Rapidquery Successfully SuperCached {packet.json_name} in {round(time, 6)}s', metadata.logfile)
            else:
                write_verbose(
                    f'Rapidquery Successfully Received {packet.json_name}.json in {round(time, 6)}s', metadata)
                write_debug(
                    f'Rapidquery Successfully Received {packet.json_name}.json in {round(time, 6)}s', metadata)
                log_info(
                    f'Rapidquery Successfully Received {packet.json_name}.json in {round(time, 6)}s', metadata.logfile)

        write_verbose('Generating system download path...', metadata)
        log_info('Generating system download path...', metadata.logfile)

        if not metadata.silent:
            if not metadata.no_color:
                if super_cache:
                    print('SuperCached', Fore.GREEN + '=>' + Fore.RESET, '[', Fore.CYAN +  f'{packet.display_name}' + Fore.RESET + ' ]')
                else:
                    print('Recieved => [', Fore.CYAN +  f'{packet.display_name}' + Fore.RESET + ' ]')

            else:
                print(f'Found => [ {packet.display_name} ]')

        status = 'Download Path'
        download_url = get_download_url(packet)
        status = 'Got Download Path'

        log_info(f'Recieved download path => {download_url}', metadata.logfile)
        log_info('Initializing Rapid Download...', metadata.logfile)

        # Downloading The File From Source
        write_debug(f'Downloading {packet.display_name} from => {packet.win64}', metadata)
        write_verbose(
            f"Downloading from '{download_url}'", metadata)
        log_info(f"Downloading from '{download_url}'", metadata.logfile)
        status = 'Downloading'
        cached = False
        if rate_limit == -1:
            start = timer()
            path, cached = download(download_url, packet.json_name, metadata, packet.win64_type)
            end = timer()
        else:
            log_info(f'Starting rate-limited installation => {rate_limit}', metadata.logfile)
            bucket = TokenBucket(tokens=10 * rate_limit, fill_rate=rate_limit)

            limiter = Limiter(
                bucket=bucket,
                filename=f'{tempfile.gettempdir()}\Setup{packet.win64_type}',
            )

            urlretrieve(
                url=download_url,
                filename=f'{tempfile.gettempdir()}\Setup{packet.win64_type}',
                reporthook=limiter
            )

            path = f'{tempfile.gettempdir()}\Setup{packet.win64_type}'

        status = 'Downloaded'

        log_info('Finished Rapid Download', metadata.logfile)

        if virus_check:
            log_info('Running requested virus scanning', metadata.logfile)
            write('Scanning File For Viruses...', 'blue', metadata)
            check_virus(path, metadata)
        if not cached:
            write(
                f'\nInstalling {packet.display_name}', 'cyan', metadata)
        else:
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

        if final_snap.env_length > start_snap.env_length or final_snap.sys_length > start_snap.sys_length:
            write('Refreshing Environment Variables', 'green', metadata)
            start = timer()
            log_info('Refreshing Environment Variables At scripts/refreshvars.cmd', metadata.logfile)
            write_debug('Refreshing Env Variables, Calling Batch Script At scripts/refreshvars.cmd', metadata)
            write_verbose('Refreshing Environment Variables', metadata)
            refresh_environment_variables()
            end = timer()
            write_debug(f'Successfully Refreshed Environment Variables in {round(end - start)} seconds', metadata)

        write(
            f'Successfully Installed {packet.display_name}!', 'bright_magenta', metadata)
        log_info(f'Successfully Installed {packet.display_name}!', metadata.logfile)

        if metadata.reduce_package:
            os.remove(path)
            os.remove(Rf'{tempfile.gettempdir()}\electric\downloadcache.pickle')

            log_info('Successfully Cleaned Up Installer From Temporary Directory And DownloadCache', metadata.logfile)
            write('Successfully Cleaned Up Installer From Temp Directory',
                  'green', metadata)

        write_verbose('Installation and setup completed.', metadata)
        log_info('Installation and setup completed.', metadata.logfile)
        write_debug(
            f'Terminated debugger at {strftime("%H:%M:%S")} on install::completion', metadata)
        log_info(
            f'Terminated debugger at {strftime("%H:%M:%S")} on install::completion', metadata.logfile)
        close_log(metadata.logfile, 'Install')

        index += 1

    finish_log()


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
@click.option('--node', '-npm', is_flag=True, help='Specify a Python package to install')
@click.option('--no-cache', '-nocache', is_flag=True, help='Prevent cache usage for uninstallation')
@click.option('--configuration', '-cf', is_flag=True, help='Specify a config file to install')
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
    no_cache: bool,
    atom: bool,
    configuration: bool
):
    """
    Uninstalls a package or a list of packages.
    """
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
            no_cache=no_cache,
            sync=None,
            reduce=None,
            rate_limit=None
        )
        sys.exit()

    log_info('Generating metadata...', logfile)

    metadata = generate_metadata(
        None, silent, verbose, debug, no_color, yes, logfile, None, None, None, Setting.new())

    log_info('Successfully generated metadata.', logfile)

    log_info('Checking if supercache exists...', metadata.logfile)
    super_cache = check_supercache_valid()

    if super_cache:
        log_info('SuperCache detected.', metadata.logfile)

    if no_cache:
        log_info('Overriding SuperCache To FALSE', metadata.logfile)
        super_cache = False

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

    corrected_package_names = get_autocorrections(packages, get_correct_package_names(), metadata)

    write_debug(install_debug_headers, metadata)
    for header in install_debug_headers:
        log_info(header, metadata.logfile)

    index = 0

    for package in corrected_package_names:
        supercache_availiable = check_supercache_availiable(package)
        if super_cache and supercache_availiable and not no_cache:
            log_info('Handling SuperCache Request.', metadata.logfile)
            res, time = handle_cached_request(package)
            time = Decimal(time)
        else:
            log_info('Handling Network Request...', metadata.logfile)
            status = 'Networking'
            write_verbose('Sending GET Request To /rapidquery/packages', metadata)
            write_debug('Sending GET Request To /rapidquery/packages', metadata)
            log_info('Sending GET Request To /rapidquery/packages', metadata.logfile)
            update_supercache(metadata)
            res, time = handle_cached_request(package)

        pkg = res
        keys = list(pkg.keys())
        idx = 0
        for key in keys:
            if key not in ['package-name', 'nightly', 'display-name']:
                idx = keys.index(key)
                break

        version = keys[idx]
        uninstall_exit_codes = None
        if 'valid-uninstall-exit-codes' in list(pkg.keys()):
            uninstall_exit_codes = pkg['valid-install-exit-codes']

        name = pkg['package-name']
        pkg = pkg[version]
        log_info('Generating Packet For Further Installation.', metadata.logfile)
        packet = Packet(pkg, package, name, pkg['win64'], pkg['win64-type'], pkg['custom-location'], pkg['install-switches'], pkg['uninstall-switches'], None, pkg['dependencies'], None, uninstall_exit_codes, version)
        proc = None
        keyboard.add_hotkey(
            'ctrl+c', lambda: kill_proc(proc, metadata))

        if super_cache:
            write(
                f'Rapidquery Successfully SuperCached {packet.json_name} in {round(time, 6)}s', 'bright_yellow', metadata)
            write_debug(
                f'Rapidquery Successfully SuperCached {packet.json_name} in {round(time, 9)}s', metadata)
            log_info(
                f'Rapidquery Successfully SuperCached {packet.json_name} in {round(time, 6)}s', metadata)
        else:
            write(
                f'Rapidquery Successfully Received {packet.json_name}.json in {round(time, 6)}s', 'bright_green', metadata)
            log_info(
                f'Rapidquery Successfully Received {packet.json_name}.json in {round(time, 6)}s', metadata.logfile)

        # Getting UninstallString or QuietUninstallString From The Registry Search Algorithm
        write_verbose(
            'Fetching uninstall key from the registry...', metadata)
        write_debug('Sending query (uninstall-string) to Registry', metadata)
        log_info('Fetching uninstall key from the registry...', metadata.logfile)

        start = timer()
        key = get_uninstall_key(packet.json_name, packet.display_name)

        end = timer()

        if not key:
            log_info(f'electric didn\'t detect any existing installations of => {packet.display_name}', metadata.logfile)
            write(
                f'Could Not Find Any Existing Installations Of {packet.display_name}', 'yellow', metadata)
            close_log(metadata.logfile, 'Uninstall')
            index += 1
            continue

        kill_running_proc(packet.json_name, packet.display_name, metadata)

        write_verbose('Uninstall key found.', metadata)
        log_info('Uninstall key found.', metadata.logfile)
        log_info(key, metadata.logfile)
        write_debug('Successfully Recieved UninstallString from Windows Registry', metadata)

        write(
            f'Successfully Retrieved Uninstall Key In {round(end - start, 4)}s', 'green', metadata)
        log_info(
            f'Successfully Retrieved Uninstall Key In {round(end - start, 4)}s', metadata.logfile)

        command = ''

        # Key Can Be A List Or A Dictionary Based On Results

        if isinstance(key, list):
            if key:
                key = key[0]

        with Halo(f'Uninstalling {packet.display_name}', text_color='cyan', color='grey') as h:
            # If QuietUninstallString Exists (Preferable)
            if 'QuietUninstallString' in key:
                command = key['QuietUninstallString']
                command = command.replace('/I', '/X')
                command = command.replace('/quiet', '/qn')

                additional_switches = None
                if packet.uninstall_switches:
                    if packet.uninstall_switches != []:
                        write_verbose(
                            'Adding additional uninstall switches', metadata)
                        write_debug('Appending / Adding additional uninstallation switches', metadata)
                        log_info('Adding additional uninstall switches', metadata.logfile)
                        additional_switches = packet.uninstall_switches

                if additional_switches:
                    for switch in additional_switches:
                        command += ' ' + switch

                write_verbose('Executing the quiet uninstall command', metadata)
                log_info(f'Executing the quiet uninstall command => {command}', metadata.logfile)
                write_debug('Running silent uninstallation command', metadata)
                run_cmd(command, metadata, 'uninstallation', packet.display_name, packet.install_exit_codes, packet.uninstall_exit_codes, h, packet)


                h.stop()

                write(
                    f'Successfully Uninstalled {packet.display_name}', 'bright_magenta', metadata)

                write_verbose('Uninstallation completed.', metadata)
                log_info('Uninstallation completed.', metadata.logfile)

                index += 1
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

                run_cmd(command, metadata, 'uninstallation', packet.display_name, packet.install_exit_codes, packet.uninstall_exit_codes, h, packet)
                h.stop()
                write(
                    f'Successfully Uninstalled {packet.display_name}', 'bright_magenta', metadata)
                write_verbose('Uninstallation completed.', metadata)
                log_info('Uninstallation completed.', metadata.logfile)
                index += 1
                write_debug(
                    f'Terminated debugger at {strftime("%H:%M:%S")} on uninstall::completion', metadata)
                log_info(
                    f'Terminated debugger at {strftime("%H:%M:%S")} on uninstall::completion', metadata.logfile)
                close_log(metadata.logfile, 'Uninstall')
    finish_log()


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
            exit()

        if len(files) == 0:
            h.stop()
            click.echo(click.style('Nothing To Cleanup!', 'cyan'))

        else:
            h.stop()
            with Bar(f'{Fore.CYAN}Deleting Temporary Files{Fore.RESET}', max=len(files), bar_prefix=' [ ', bar_suffix=' ] ', fill=f'{Fore.GREEN}={Fore.RESET}', empty_fill=f'{Fore.LIGHTBLACK_EX}-{Fore.RESET}') as b:
                for f in files:
                    os.remove(rf'{tempfile.gettempdir()}\electric\{f}')
                    time.sleep(0.0075)
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
@click.option('--no-cache', '-nocache', is_flag=True, help='Specify a Python package to install')
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
    no_cache: bool,
    sync: bool,
    reduce: bool,
    rate_limit: bool,
    exclude: str,
    ):
    """
    Installs a bunlde of packages from the official electric repository.
    """
    metadata = generate_metadata(
            no_progress, silent, verbose, debug, no_color, yes, logfile, virus_check, reduce, rate_limit, Setting.new())

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
        res, _ = send_req_bundle()
        del res['_id']
        spinner.stop()
        package_names = ''
        idx = 0

        correct_names = get_correct_package_names(res)

        corrected_package_names = get_autocorrections([bundle_name], correct_names, metadata)


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
                no_cache=no_cache,
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
                no_cache=no_cache,
                sync=sync,
                reduce=reduce,
                rate_limit=rate_limit
                )
    else:
        click.echo(click.style('\nAdministrator Elevation Required. Exit Code [0001]', 'red'), err=True)
        disp_error_msg(get_error_message('0001', 'installation', 'None', None), metadata)


@cli.command(aliases=['find'], context_settings=CONTEXT_SETTINGS)
@click.argument('approx_name', required=True)
@click.option('--starts-with', '-sw', is_flag=True, help='Find packages which start with the specified literal')
@click.option('--exact', '-e', is_flag=True, help='Find packages which exactly match the specified literal')
def search(
    approx_name: str,
    starts_with: str,
    exact: str,
    ): # pylint: disable=function-redefined
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
            click.echo(click.style(f'{len(matches)} packages found.', fg='green'))
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
    click.echo(click.style(f'Successfully Created {Fore.LIGHTBLUE_EX}`{project_name}.electric`{Fore.GREEN} at {os.getcwd()}\\', 'green'))


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
@click.option('--no-cache', '-nocache', is_flag=True, help='Specify a Python package to install')
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
    no_cache: bool,
    sync: bool,
    reduce: bool,
    rate_limit: bool,
    exclude_versions: bool
    ):
    '''
    Installs and configures packages from a .electric configuration file.
    '''
    if not is_admin():
        config_path = config_path.replace('.\\', '\\')
        if not '\\' in config_path:
            config_path = '\\' + config_path
        config_path = os.getcwd() + config_path
        print(config_path)
        os.system(fr'{PathManager.get_current_directory()}\scripts\context-elevate.cmd {config_path}')
        sys.exit()

    metadata = generate_metadata(
            no_progress, silent, verbose, debug, no_color, yes, logfile, virus_check, reduce, rate_limit, Setting.new())

    config = Config.generate_configuration(config_path)
    config.check_prerequisites()
    if remove:
        config.uninstall()
    else:
        config.install(exclude_versions, install_directory, no_cache, sync, metadata)


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
    with open(filepath,"rb") as f:
        # Read and update hash string value in blocks of 4K
        for byte_block in iter(lambda: f.read(4096),b""):
            sha256_hash.update(byte_block)

    sha256 = sha256_hash.hexdigest()
    with open(filepath, 'r') as f:
        l = [line.strip() for line in f.readlines()]

        if '# --------------------Checksum Start-------------------------- #' in l and '# --------------------Checksum End--------------------------- #' in l:
            click.echo(click.style('File Already Signed, Aborting Signing!', fg='red'))
            exit()

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

    editor_completion = WordCompleter(['Visual Studio Code', 'Sublime Text 3', 'Atom'])
    username = prompt('Enter Publisher Name => ')
    description = prompt('Enter Configuration Description => ')
    use_editor = prompt('Do You Use A Development Text Editor (Example: Visual Studio Code) [y/N]: ')
    use_editor = use_editor in ('y', 'yes', 'Y', 'YES')
    include_editor = False
    editor = ''
    if use_editor:
        include_editor = click.confirm('Do You Want To Include Your Editor Extensions And Configuration?')
        if include_editor:
            editor = prompt('Enter The Development Text Editor You Use => ', completer=editor_completion, complete_while_typing=True)

    include_python = None
    try:
        proc = Popen('pip --version', stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
        _, err = proc.communicate()
        if not err:
            include_python = click.confirm('Would you like to include your Python Configuration?')
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


@cli.command(aliases=['info'], context_settings=CONTEXT_SETTINGS)
@click.option('--nightly', '--pre-release', is_flag=True, help='Show a nightly or pre-release build of a package')
@click.argument('package_name', required=True)
def show(package_name: str, nightly: bool):
    '''
    Displays information about the specified package.
    '''
    res, _ = send_req_package(package_name)
    click.echo(click.style(display_info(res, nightly=nightly), fg='green'))


@cli.command(context_settings=CONTEXT_SETTINGS)
def settings():
    if not os.path.isfile(rf'{PathManager.get_appdata_directory()}\\electric-settings.json'):
        click.echo(click.style(f'Creating electric-settings.json at {Fore.CYAN}{PathManager.get_appdata_directory()}{Fore.RESET}', fg='green'))
        initialize_settings()
    cursor.hide()
    with Halo('Opening Settings... ', text_color='blue'):
        open_settings()
    cursor.show()


@cli.command()
@click.option('--word', required=True)
@click.option('--commandline', required=True)
@click.option('--position', required=True)
def complete(
    word : str,
    commandline: str,
    position: str
    ):

    n = len(commandline.split(' '))
    if word:
        possibilities = []
        if n == 2:
            possibilities = electric_commands

        if n == 3:

            appdata_dir = PathManager.get_appdata_directory() + r'\SuperCache'

            with open(rf'{appdata_dir}\packages.json', 'r') as f:
                packages = json.load(f)['packages']

            possibilities = difflib.get_close_matches(word, packages)

        if n >= 4:
            command = commandline.split(' ')[1]

            if command == 'install' or command == 'bundle' or command == 'i':
                possibilities = install_flags
            if command == 'uninstall' or command == 'remove' or command == 'u':
                possibilities = uninstall_flags
            if command == 'search' or command == 'find':
                possibilities = search_flags
            if command == 'config':
                possibilities = config_flags

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
    cli() #pylint: disable=no-value-for-parameter

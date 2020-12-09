######################################################################
#                            ELECTRIC CLI                            #
######################################################################


from registry import get_uninstall_key, get_environment_keys
from cli import SuperChargeCLI
from Classes.PackageManager import PackageManager
from timeit import default_timer as timer
from urllib.request import urlretrieve
from limit import Limiter, TokenBucket
from Classes.Config import Config
from Classes.Packet import Packet
from info import __version__
from constants import *
from external import *
from colorama import *
from logger import *
from utils import *
import keyboard
import logging
import difflib
import click
import halo
import sys
import os


@click.group(cls=SuperChargeCLI)
@click.version_option(__version__)
@click.pass_context
def cli(_):
    pass


@cli.command(aliases=['i'])
@click.argument('package_name', required=True)
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose mode for installation')
@click.option('--debug', '-d', is_flag=True, help='Enable debug mode for installation')
@click.option('--no-progress', '-np', is_flag=True, default=False, help='Disable progress bar for installation')
@click.option('--no-color', '-nc', is_flag=True, help='Disable colored output for installation')
@click.option('--log-output', '-l', 'logfile', help='Log output to the specified file')
@click.option('--install-dir', '-dir', 'install_directory', help='Specify an installation directory for a package')
@click.option('--virus-check', '-vc', is_flag=True, help='Check for virus before installation')
@click.option('-y', '--yes', is_flag=True, help='Accept all prompts during installation')
@click.option('--silent', '-s', is_flag=True, help='Completely silent installation without any output to console')
@click.option('--vscode', '-vs', is_flag=True, help='Specify a Visual Studio Code extension to install')
@click.option('--python', '-py', is_flag=True, help='Specify a Python package to install')
@click.option('--node', '-npm', is_flag=True, help='Specify a Python package to install')
@click.option('--no-cache', '-nocache', is_flag=True, help='Specify a Python package to install')
@click.option('--sync', '-sc', is_flag=True, help='Force downloads and installations one after another')
@click.option('--reduce', '-rd', is_flag=True, help='Cleanup all traces of package after installation')
@click.option('--rate-limit', '-rl', type=int, default=-1)
def install(
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
):  
    if logfile:
        logfile = logfile.replace('=', '')
        logfile = logfile.replace('.txt', '.log')
        createConfig(logfile, logging.INFO, 'Install')
    
    log_info('Generating metadata...', logfile)
    metadata = generate_metadata(
        no_progress, silent, verbose, debug, no_color, yes, logfile, virus_check, reduce, rate_limit)
    log_info('Successfully generated metadata.', metadata.logfile)

    if python:

        package_names = package_name.split(',')

        for name in package_names:
            handle_python_package(name, 'install', metadata)

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
        
    log_info('Checking if supercache exists...', metadata.logfile)
    super_cache = check_supercache_valid()
    if super_cache:
        log_info('Supercache detected.', metadata.logfile)
    if no_cache:
        log_info('Overriding SuperCache To FALSE', metadata.logfile)
        super_cache = False

    log_info('Setting up custom `ctrl+c` shortcut.', metadata.logfile)
    status = 'Initializing'
    setup_name = ''
    keyboard.add_hotkey(
        'ctrl+c', lambda: handle_exit(status, setup_name, metadata))

    packages = package_name.strip(' ').split(',')

    if super_cache:
        log_info('Handling SuperCache Request.', metadata.logfile)
        res, time = handle_cached_request()

    else:
        spinner = halo.Halo(color='grey')
        spinner.start()
        log_info('Handling Network Request...', metadata.logfile)
        status = 'Networking'
        write_verbose('Sending GET Request To /packages', metadata)
        write_debug('Sending GET Request To /packages', metadata)
        log_info('Sending GET Request To /packages', metadata.logfile)
        res, time = send_req_all()
        res = json.loads(res)
        update_supercache(res)
        del res['_id']
        spinner.stop()

    correct_names = get_correct_package_names(res)
    corrected_package_names = get_autocorrections(packages, correct_names, metadata)

    write_debug(install_debug_headers, metadata)
    for header in install_debug_headers:
        log_info(header, metadata.logfile)

    index = 0

    if not sync:
        if len(corrected_package_names) > 5:
            log_info('Terminating installation!', metadata.logfile)
            write('electric Doesn\'t Support More Than 5 Parallel Downloads At Once Currently. Use The --sync Flag To Synchronously Download The Packages', 'red', metadata)
        if len(corrected_package_names) > 1:
            packets = []
            for package in corrected_package_names:
                pkg = res[package]
                custom_dir = None
                if install_directory:
                    custom_dir = install_directory + f'\\{pkg["package-name"]}'
                else:
                    custom_dir = install_directory
                packet = Packet(package, pkg['package-name'], pkg['win64'], pkg['win64-type'], pkg['custom-location'], pkg['install-switches'], pkg['uninstall-switches'], custom_dir, pkg['dependencies'])
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
        pkg = res[package]
        log_info('Generating Packet For Further Installation.', metadata.logfile)
        packet = Packet(package, pkg['package-name'], pkg['win64'], pkg['win64-type'], pkg['custom-location'], pkg['install-switches'], pkg['uninstall-switches'], install_directory, pkg['dependencies'])
        log_info('Searching for existing installation of package.', metadata.logfile)
        

        installation = find_existing_installation(package, packet.json_name)

        if installation:
            write_debug(
                f'Found existing installation of {packet.json_name}.', metadata)
            write_verbose(
                f'Found an existing installation of => {packet.json_name}', metadata)
            write(
                f'Detected an existing installation {packet.json_name}.', 'bright_yellow', metadata)
            installation_continue = click.confirm(
                f'Would you like to reinstall {packet.json_name}')
            if installation_continue or yes:
                os.system(f'electric uninstall {packet.json_name}')
                os.system(f'electric install {packet.json_name}')
                return
            else:
                handle_exit(status, setup_name, metadata)

        if packet.dependencies:
            install_dependent_packages(packet, rate_limit, install_directory, metadata)

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
                    print(f'SuperCached', Fore.GREEN + '=>' + Fore.RESET, '[', Fore.CYAN +  f'{packet.display_name}' + Fore.RESET + ' ]')
                else:
                    print(f'Recieved => [', Fore.CYAN +  f'{packet.display_name}' + Fore.RESET + ' ]')

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
            write('Scanning File For Viruses...', 'blue', metadata)
            check_virus(path, metadata)
        if not cached:
            write(
                '\nUsing Rapid Install, Accept Prompts Asking For Admin Permission...', 'cyan', metadata)
        else:
            write(
                'Using Rapid Install, Accept Prompts Asking For Admin Permission...', 'cyan', metadata)
        log_info(
            'Using Rapid Install To Complete Setup, Accept Prompts Asking For Admin Permission...', metadata.logfile)

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
        closeLog(metadata.logfile, 'Install')

        index += 1
    end = timer()


@cli.command(aliases=['remove', 'u'])
@click.argument('package_name', required=True)
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose mode for uninstallation')
@click.option('--debug', '-d', is_flag=True, help='Enable debug mode for uninstallation')
@click.option('--no-color', '-nc', is_flag=True, help='Disable colored output for uninstallation')
@click.option('--log-output', '-l', 'logfile', help='Log output to the specified file')
@click.option('-y', '--yes', is_flag=True, help='Accept all prompts during uninstallation')
@click.option('--silent', '-s', is_flag=True, help='Completely silent uninstallation without any output to console')
@click.option('--python', '-py', is_flag=True, help='Specify a Python package to uninstall')
@click.option('--vscode', '-vs', is_flag=True, help='Specify a Visual Studio Code extension to install')
@click.option('--node', '-npm', is_flag=True, help='Specify a Python package to install')
@click.option('--no-cache', '-nocache', is_flag=True, help='Prevent cache usage for uninstallation')
def uninstall(
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
    no_cache: bool
):

    log_info('Generating metadata...', logfile)

    metadata = generate_metadata(
        None, silent, verbose, debug, no_color, yes, logfile, None, None, None)
    
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
        createConfig(logfile, logging.INFO, 'Install')

    if python:

        package_names = package_name.split(',')

        for name in package_names:
            handle_python_package(name, 'uninstall', metadata)

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

    log_info('Setting up custom `ctrl+c` shortcut.', metadata.logfile)
    status = 'Initializing'
    setup_name = ''
    keyboard.add_hotkey(
        'ctrl+c', lambda: handle_exit(status, setup_name, metadata))

    packages = package_name.split(',')

    if super_cache:
        log_info('Handling SuperCache Request.', metadata.logfile)
        res, time = handle_cached_request()

    else:
        log_info('Handling Network Request...', metadata.logfile)
        status = 'Networking'
        write_verbose('Sending GET Request To /rapidquery/packages', metadata)
        write_debug('Sending GET Request To /rapidquery/packages', metadata)
        log_info('Sending GET Request To /rapidquery/packages', metadata.logfile)
        res, time = send_req_all()
        res = json.loads(res)
        update_supercache(res)

    correct_names = get_correct_package_names(res)
    corrected_package_names = get_autocorrections(packages, correct_names, metadata)

    write_debug(install_debug_headers, metadata)
    for header in install_debug_headers:
        log_info(header, metadata.logfile)

    index = 0

    for package in corrected_package_names:
        pkg = res[package]
        log_info('Generating Packet For Further Installation.', metadata.logfile)
        packet = Packet(package, pkg['package-name'], pkg['win64'], pkg['win64-type'], pkg['custom-location'], pkg['install-switches'], pkg['uninstall-switches'], None, pkg['dependencies'])
        proc = None
        keyboard.add_hotkey(
            'ctrl+c', lambda: kill_proc(proc, metadata))

        kill_running_proc(packet.json_name, packet.display_name, metadata)

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

        # TODO: Add suggestions to uninstall bundled in dependencies

        # If The UninstallString Or QuietUninstallString Doesn't Exist
        # if not key:
        #     write_verbose('No registry keys found', verbose, no_color, silent)
        #     log_info('No registry keys found', logfile)
        #     if "uninstall-command" in pkg:
        #         if pkg['uninstall-command'] == '':
        #             write(
        #                 f'Could Not Find Any Existing Installations Of {packet.json_name}', 'yellow', no_color, silent)
        #             log_error(
        #                 f'Could Not Find Any Existing Installations Of {packet.json_name}', logfile)
        #             closeLog(logfile, 'Uninstall')
        #             index += 1
        #             continue
        #         else:
        #             write_verbose("Executing the uninstall command",
        #                           verbose, no_color, silent)
        #             log_info("Executing the uninstall command", logfile)

        #             try:
        #                 proc = Popen(shlex.split(
        #                     pkg['uninstall-command']), stdout=PIPE, stdin=PIPE, stderr=PIPE)
        #                 proc.wait()
        #                 if proc.returncode != 0:
        #                     write(f'Installation Failed, Make Sure You Accept All Prompts Asking For Admin permission', 'red', no_color, silent)
        #                     handle_exit(status, 'None', no_color, silent)
        #             except FileNotFoundError:

        #                 proc = Popen(shlex.split(
        #                     pkg['uninstall-command']), stdout=PIPE, stdin=PIPE, stderr=PIPE, shell=True)
        #                 proc.wait()
        #                 if proc.returncode != 0:
        #                     write(f'Installation Failed, Make Sure You Accept All Prompts Asking For Admin permission', 'red', no_color, silent)
        #                     handle_exit(status, 'None', no_color, silent)

        #             write(
        #                 f"Successfully Uninstalled {package_name}", "bright_magenta", no_color, silent)

        #             index += 1
        #             write_debug(
        #                 f'Terminated debugger at {strftime("%H:%M:%S")} on uninstall::completion', debug, no_color, silent)
        #             log_info(
        #                 f'Terminated debugger at {strftime("%H:%M:%S")} on uninstall::completion', logfile)
        #             closeLog(logfile, 'Uninstall')
        #             continue
        #     else:
        # write(
        #     f'Could Not Find Any Existing Installations Of {package_name}', 'yellow', no_color, silent)
        # closeLog(logfile, 'Uninstall')
        # index += 1
        # continue

        if not key:
            log_info(f'electric didn\'t detect any existing installations of => {packet.display_name}', metadata.logfile)
            write(
                f'Could Not Find Any Existing Installations Of {packet.display_name}', 'yellow', metadata)
            closeLog(metadata.logfile, 'Uninstall')
            index += 1
            continue

        write_verbose('Uninstall key found.', metadata)
        log_info('Uninstall key found.', metadata.logfile)
        log_info(key, metadata.logfile)
        write_debug('Successfully Recieved UninstallString from Windows Registry', metadata)

        write(
            f'Successfully Retrieved Uninstall Key In {round(end - start, 4)}s', 'cyan', metadata)
        log_info(
            f'Successfully Retrieved Uninstall Key In {round(end - start, 4)}s', metadata.logfile)

        command = ''

        # Key Can Be A List Or A Dictionary Based On Results

        if isinstance(key, list):
            if key:
                key = key[0]
  
        write(f'Uninstalling {packet.display_name}...', 'green', metadata)

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
            write_debug(f'Running silent uninstallation command', metadata)
            run_cmd(command, metadata, 'uninstallation', packet.display_name)

            write(
                f'Successfully Uninstalled {packet.display_name}', 'bright_magenta', metadata)

            write_verbose('Uninstallation completed.', metadata)
            log_info('Uninstallation completed.', metadata.logfile)

            index += 1
            write_debug(
                f'Terminated debugger at {strftime("%H:%M:%S")} on uninstall::completion', metadata)
            log_info(
                f'Terminated debugger at {strftime("%H:%M:%S")} on uninstall::completion', metadata.logfile)
            closeLog(metadata.logfile, 'Uninstall')

        # If Only UninstallString Exists (Not Preferable)
        if 'UninstallString' in key and 'QuietUninstallString' not in key:
            command = key['UninstallString']
            command = command.replace('/I', '/X')
            command = command.replace('/quiet', '/passive')
            # command = f'"{command}"'
            for switch in packet.uninstall_switches:
                command += f' {switch}'

            # Run The UninstallString
            write_verbose('Executing the Uninstall Command', metadata)
            log_info('Executing the silent Uninstall Command', metadata.logfile)

            run_cmd(command, metadata, 'uninstallation', packet.display_name)

            write(
                f'Successfully Uninstalled {packet.display_name}', 'bright_magenta', metadata)
            write_verbose('Uninstallation completed.', metadata)
            log_info('Uninstallation completed.', metadata.logfile)
            index += 1
            write_debug(
                f'Terminated debugger at {strftime("%H:%M:%S")} on uninstall::completion', metadata)
            log_info(
                f'Terminated debugger at {strftime("%H:%M:%S")} on uninstall::completion', metadata.logfile)
            closeLog(metadata.logfile, 'Uninstall')


@cli.command(aliases=['bdl'])
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
    
    metadata = generate_metadata(
            no_progress, silent, verbose, debug, no_color, yes, logfile, virus_check, reduce, rate_limit)

    if is_admin():
        if logfile:
            logfile = logfile.replace('=', '')
            logfile = logfile.replace('.txt', '.log')
            createConfig(logfile, logging.INFO, 'Install')

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
        res = json.loads(res)
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
        disp_error_msg(get_error_message('0001', 'installation', 'None'), metadata)


@cli.command(aliases=['find'])
@click.argument('approx_name', required=True)
@click.option('--starts-with', '-sw', is_flag=True, help='Find packages which start with the specified literal')
@click.option('--exact', '-e', is_flag=True, help='Find packages which exactly match the specified literal')
def search(
    approx_name: str,
    starts_with: str,
    exact: str,
    ):


    super_cache = check_supercache_valid()
    if super_cache:
        res, _ = handle_cached_request()

    else:
        res, _ = send_req_all()
        res = json.loads(res)

    correct_names = get_correct_package_names(res)[1:]

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
            click.echo(click.style(f'1 package found.', fg='yellow'))
    
    else:
        click.echo(click.style('0 packages found!', fg='red'))


@cli.command(aliases=['create'])
@click.argument('project_name', required=True)
def new(
    project_name: str
    ):
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


@cli.command()
@click.argument('config_path', required=True)
@click.option('--remove', '-uninst', is_flag=True, help='Uninstall packages in a bundle installed')
def config(
    config_path: str,
    remove: bool,
    ):
    config = Config.generate_configuration(config_path)
    config.check_prerequisites()
    if remove:
        config.uninstall()
    else:
        config.install()


@cli.command(aliases=['validate'])
@click.argument('filepath', required=True)
def sign(
        filepath: str
    ):

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
            click.echo(click.style(f'File Already Signed, Aborting Signing!', fg='red'))
            exit()
    
    with open(filepath, 'a') as f:
        f.writelines([
            '\n# --------------------Checksum Start-------------------------- #',
            '\n',
            '########################################################################\n',
            f'# {md5}',
            '\n',
            f'# {sha256}',
            '\n',
            '########################################################################',
            '\n# --------------------Checksum End--------------------------- #'
        ])

    click.echo(click.style(f'Successfully Signed {filepath}', fg='green'))


@cli.command(aliases=['info'])
@click.argument('package_name', required=True)
def show(package_name: str):
    super_cache = check_supercache_valid()

    if super_cache:
        res, _ = handle_cached_request()

    else:
        # status = 'Networking'
        # write_verbose('Sending GET Request To /packages', metadata)
        # write_debug('Sending GET Request To /packages', metadata)
        # log_info('Sending GET Request To /packages', logfile)
        res, time = send_req_all()
        res = json.loads(res)
        update_supercache(res)
        del res['_id']

    correct_names = get_correct_package_names(res)
    corrected_package_names = []

    if package_name in correct_names:
        corrected_package_names.append(package_name)
    else:
        corrections = difflib.get_close_matches(package_name, correct_names)
        if corrections:
            
            click.echo(click.style(f'Autocorrecting To {corrections[0]}', fg='bright_magenta'))
            if click.confirm('Would You Like To Continue?'):
                package_name = corrections[0]
                corrected_package_names.append(package_name)
        else:
            click.echo(click.style(f'Could Not Find Any Packages Which Match {package_name}', fg='bright_magenta'))

    pkg_info = res[corrected_package_names[0]]
    click.echo(click.style(display_info(pkg_info), fg='green'))

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
            appdata_dir = PathManager.get_appdata_directory()
            
            with open(rf'{appdata_dir}\supercache.json', 'r') as f:
                dictionary = json.loads(f.read())

            possibilities = list(dictionary.keys())

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
    cli()

# Append To $PROFILE For Powershell Completion
# Register-ArgumentCompleter -Native -CommandName electric -ScriptBlock {
#     param($wordToComplete, $commandAst, $cursorPosition)
#         [Console]::InputEncoding = [Console]::OutputEncoding = $OutputEncoding = [System.Text.Utf8Encoding]::new()
#         $Local:word = $wordToComplete.Replace('"', '""')
#         $Local:ast = $commandAst.ToString().Replace('"', '""')
#         electric complete --word="$Local:word" --commandline "$Local:ast" --position $cursorPosition | ForEach-Object {
#             [System.Management.Automation.CompletionResult]::new($_, $_, 'ParameterValue', $_)
#         }
# }

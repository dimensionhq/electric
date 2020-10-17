from timeit import default_timer as timer
from registry import get_uninstall_key
from time import strftime
from extension import *
from constants import *
from helpers import *
import logging
from logger import *
import difflib
import sys

__version__ = '1.0.0b'


@click.group()
@click.version_option(__version__)
@click.pass_context
def cli(ctx):
    pass


@cli.command()
@click.argument('package_name', required=True)
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose mode for installation')
@click.option('--debug', '-d', is_flag=True, help='Enable debug mode for installation')
@click.option('--no-progress', '-np', is_flag=True, default=False, help='Disable progress bar for installation')
@click.option('--no-color', '-nc', is_flag=True, help='Disable colored output for installation')
@click.option('--log-output', '-l', 'logfile', help='Log output to the specified file')
def install(package_name: str, verbose : bool, debug : bool, no_progress : bool, no_color : bool, logfile : str):

    if logfile:
        logfile = logfile.replace('.txt', '.log')
        createConfig(logfile, logging.INFO, 'Install')

    packages = package_name.split(',')
    write_verbose('Sending GET request to rapidquery/all', verbose, no_color)
    log_info('Sending GET request to rapidquery/all', logfile)

    res, time = send_req_all()
    package_names = get_package_names(res)

    write_verbose(
        f"Packages to be installed: {package_name}", verbose, no_color)
    log_info(f"Packages to be installed: {package_name}", logfile)
    write_debug(install_debug_headers, debug, no_color)
    for header in uninstall_debug_headers:
        log_info(header, logfile)

    for package in packages:
        package = package.strip()
        package_name = package.lower()
        write_verbose(
            f'Finding closest match to {package_name}...', verbose, no_color)
        log_info(f'Finding closest match to {package_name}...', logfile)

        try:
            close_name = difflib.get_close_matches(
                package_name, package_names, n=1)[0]

        except IndexError:
            write('Package not found!', 'red', no_color)
            log_error('Package not found!', logfile)
            closeLog(logfile, 'Install')
            return

        write_verbose(
            f'Successfully found closest match: {close_name}.', verbose, no_color)
        log_info(f'Successfully found closest match: {close_name}.', logfile)

        if package_name != close_name:
            write(
                f'Autocorrecting To Closest Match: {close_name}', 'bright_magenta', no_color=no_color)
            log_info(f'Autocorrecting To Closest Match: {close_name}', logfile)

            if "n" in click.prompt('Do you want to continue? [y/n]')[0]:
                sys.exit()

        package_name = close_name

        write(
            f'Rapidquery Successfully Received {package_name}.json in {time}s', 'green', no_color)
        log_info(f'Rapidquery Successfully Received {package_name}.json in {time}s', logfile)

        start = timer()

        pkg = res[package_name + '.json']

        system_architecture = get_architecture()

        write_verbose('Generating system download path...', verbose, no_color)
        log_info('Generating system download path...', logfile)
        download_url = get_download_url(system_architecture, pkg)

        package_name, source, extension_type, switches = parse_json_response(
            pkg)

        end = timer()



        write(
            f'Electrons Transferred In {round(float(end) - float(start), 5)}s', 'cyan', no_color)
        log_info(f'Electrons Transferred In {round(float(end) - float(start), 5)}s', logfile)

        write('Initializing Rapid Download...', 'green', no_color)
        log_info('Initializing Rapid Download...', logfile)

        # Downloading The File From Source
        write_verbose(f"Downloading from '{download_url}'", verbose, no_color)
        log_info(f"Downloading from '{download_url}'", logfile)
        download(download_url, extension_type, package_name, no_progress)

        write('\nFinished Rapid Download', 'green', no_color)
        log_info('Finished Rapid Download', logfile)

        write(
            'Using Rapid Install To Complete Setup, Accept Prompts Asking For Admin Permission...', 'blue', no_color)
        log_info('Using Rapid Install To Complete Setup, Accept Prompts Asking For Admin Permission...', logfile)

        write_debug(
            f'Installing {package_name} through Setup{extension_type}', debug, no_color)
        log_info(f'Installing {package_name} through Setup{extension_type}', logfile)
        # Running The Installer Silently And Completing Setup
        install_package(package_name, switches, extension_type, no_color)

        # Completing Cleanup By Deleting The Setup File From Downloads
        write_verbose(
            'Cleaning up the setup and installation files...', verbose, no_color)
        log_info('Cleaning up the setup and installation files...', logfile)

        cleanup(extension_type, package_name)

        end = timer()

        write(
            f'Successfully Installed {package_name}!', 'bright_magenta', no_color)
        log_info(f'Successfully Installed {package_name}!', logfile)

        write_verbose('Installation and setup completed.', verbose, no_color)
        log_info('Installation and setup completed.', logfile)
        write_debug(
            f'Terminated debugger at {strftime("%H:%M:%S")} on install::completion', debug, no_color)
        log_info(f'Terminated debugger at {strftime("%H:%M:%S")} on install::completion', logfile)
        closeLog(logfile, 'Install')


@cli.command()
@click.argument('package_name', required=True)
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose mode for uninstallation')
@click.option('--debug', '-d', is_flag=True, help='Enable debug mode for uninstallation')
@click.option('--no-color', '-nc', is_flag=True, help='Disable colored output for installation')
@click.option('--log-output', '-l', 'logfile', help='Log output to the specified file')
def uninstall(package_name: str, verbose, debug, no_color, logfile):

    if logfile:
        logfile = logfile.replace('.txt', '.log')
        createConfig(logfile, logging.INFO, 'Uninstall')

    packages = package_name.split(',')

    res, time = send_req_all()
    package_names = get_package_names(res)
    pkg = res[package_name + ".json"]

    write_debug(uninstall_debug_headers, debug, no_color)
    for header in uninstall_debug_headers:
        log_info(header, logfile)

    for package in packages:
        package = package.strip()
        package_name = package.lower()

        write_verbose(
            f'Finding closest match to {package_name}', verbose, no_color)
        log_info(f'Finding closest match to {package_name}', logfile)
        try:
            close_name = difflib.get_close_matches(
                package_name, package_names, n=1)[0]
        except IndexError:
            write('Package not found.', 'red', no_color)
            log_error('Package not found.', logfile)
            closeLog(logfile, 'Uninstall')
            return

        write_verbose(
            f'Successfully found closest match: {close_name}.', verbose, no_color)
        log_info(f'Successfully found closest match: {close_name}.', logfile)

        if package_name != close_name:
            write(
                f'Autocorrecting To Closest Match: {close_name[0]}', 'bright_magenta', no_color)
            log_info(f'Autocorrecting To Closest Match: {close_name[0]}', logfile)

            if 'n' in click.prompt('Do you want to continue? [y/n]')[0]:
                sys.exit()

        package_name = close_name

        write(
            f'Rapidquery Successfully Received {package_name}.json in {time}s', 'green', no_color)
        log_info(f'Rapidquery Successfully Received {package_name}.json in {time}s', logfile)

        start = timer()
        # Getting UninstallString or QuietUninstallString From The Registry Search Algorithm
        write_verbose(
            "Fetching uninstall key from the registry...", verbose, no_color)
        log_info("Fetching uninstall key from the registry...", logfile)

        key = get_uninstall_key(package_name)

        end = timer()

        # If The UninstallString Or QuietUninstallString Doesn't Exist
        if not key:
            write_verbose('No registry keys found', verbose, no_color)
            log_info('No registry keys found', logfile)
            if "uninstall-command" in pkg:
                write_verbose("Executing the uninstall command",
                              verbose, no_color)
                log_info("Executing the uninstall command", logfile)
                run_uninstall(pkg['uninstall-command'],
                              pkg["package-name"], no_color)
                write_debug(
                    f'Terminated debugger at {strftime("%H:%M:%S")} on uninstall::completion', debug, no_color)
                log_info(f'Terminated debugger at {strftime("%H:%M:%S")} on uninstall::completion', logfile)
            else:
                write(
                    f'Could Not Find Any Existing Installations Of {package_name}', 'yellow', no_color)
                log_error(f'Could Not Find Any Existing Installations Of {package_name}', logfile)
            return

        write_verbose("Uninstall key found.", verbose, no_color)
        log_info("Uninstall key found.", logfile)

        write(
            f'Successfully Got Uninstall Key In {round(end - start, 4)}s', 'cyan', no_color)
        log_info(f'Successfully Got Uninstall Key In {round(end - start, 4)}s', logfile)

        command = ''

        # Key Can Be A List Or A Dictionary Based On Results
        if isinstance(key, list):
            key = key[0]

        # If QuietUninstallString Exists (Preferable)
        if 'QuietUninstallString' in key:
            command = key['QuietUninstallString']
            command = command.replace('/I', '/X')
            command = command.replace('/quiet', '/passive')

            additional_switches = []
            if "uninstall-switches" in pkg:
                write_verbose(
                    "Adding additional uninstall switches", verbose, no_color)
                log_info("Adding additional uninstall switches", logfile)
                additional_switches = pkg['uninstall-switches']

            for switch in additional_switches:
                command += ' ' + switch

            write_verbose("Executing the quiet uninstall command",
                          verbose, no_color)
            log_info("Executing the quiet uninstall command", logfile)
            run_uninstall(command, pkg["package-name"], no_color)
            write_verbose("Uninstallation completed.", verbose, no_color)
            log_info("Uninstallation completed.", logfile)
            write_debug(
                f'Terminated debugger at {strftime("%H:%M:%S")} on uninstall::completion', debug, no_color)
            log_info(f'Terminated debugger at {strftime("%H:%M:%S")} on uninstall::completion', logfile)

        # If Only UninstallString Exists (Not Preferable)
        if 'UninstallString' in key and 'QuietUninstallString' not in key:
            command = key['UninstallString']
            command = command.replace('/I', '/X')
            command = command.replace('/quiet', '/passive')

            # Run The UninstallString
            write_verbose("Executing the uninstall command", verbose, no_color)
            log_info("Executing the uninstall command", logfile)
            run_uninstall(command, pkg["package-name"], no_color)
            write_verbose("Uninstallation completed.", verbose, no_color)
            log_info("Uninstallation completed.", logfile)
            write_debug(
                f'Terminated debugger at {strftime("%H:%M:%S")} on uninstall::completion', debug, no_color)
            log_info(f'Terminated debugger at {strftime("%H:%M:%S")} on uninstall::completion', logfile)

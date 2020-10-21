from timeit import default_timer as timer
from registry import get_uninstall_key
from subprocess import  Popen, PIPE
from decimal import Decimal
from time import strftime
from extension import *
from constants import *
from utils import *
from logger import *
import subprocess
import keyboard
import difflib
import logging
import shlex
import json
import sys

__version__ = '1.0.0a'


@click.group()
@click.version_option(__version__)
@click.pass_context
def cli(ctx):
    pass


# TODO: Make Code Completely Independent Of Server Directory
# TODO: Complete --silent Flag
# TODO: Complete Parallel / Concurrent Installation

@cli.command()
@click.argument('package_name', required=True)
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose mode for installation')
@click.option('--debug', '-d', is_flag=True, help='Enable debug mode for installation')
@click.option('--no-progress', '-np', is_flag=True, default=False, help='Disable progress bar for installation')
@click.option('--no-color', '-nc', is_flag=True, help='Disable colored output for installation')
@click.option('--log-output', '-l', 'logfile', help='Log output to the specified file')
# @click.option('--essential-output', '-eo', is_flag=True, help='Log only essential output to console')
@click.option('-y', '--yes', is_flag=True, help='Accept all prompts during installation')
def install(package_name: str, verbose: bool, debug: bool, no_progress: bool, no_color: bool, logfile: str, yes : bool):

    if logfile:
        logfile = logfile.replace('.txt', '.log')
        createConfig(logfile, logging.INFO, 'Install')

    packages = package_name.split(',')

    correct_names = get_package_names()
    corrected_package_names = []
    corrections = []

    for input_name in packages:
        if input_name not in correct_names:
            corrections.append(difflib.get_close_matches(
                input_name, correct_names, n=1)[0])
        else:
            corrections.append(input_name)

    if corrections:
        for correction in corrections:
            if correction not in packages:
                write_verbose(
                    f'Successfully found closest match: {correction}.', verbose, no_color)
                log_info(
                    f'Successfully found closest match: {correction}.', logfile)
                write(
                    f'Autocorrecting To Closest Match: {correction}', 'bright_magenta', no_color=no_color)
                log_info(
                    f'Autocorrecting To Closest Match: {correction}', logfile)

                if yes:
                    write(f'Successfully Autocorrected To {correction}', color='green', no_color=no_color)

                if "n" in click.prompt('Do you want to continue? [y/n]')[0]:
                    sys.exit()
                else:
                    corrected_package_names.append(correction)

        for input_name in packages:
            if input_name in correct_names:
                corrected_package_names.append(input_name)

    for p in corrected_package_names:
        write_verbose(
            f'Sending GET request to rapidquery/{p}', verbose, no_color)
        log_info(f'Sending GET request to rapidquery/{p}', logfile)

    status = 'Networking'
    res, time = send_req_package(corrected_package_names)

    write_debug(install_debug_headers, debug, no_color)
    for header in install_debug_headers:
        log_info(header, logfile)

    index = 0
    for package in corrected_package_names:
        setup_name = ''
        status = ''
        keyboard.add_hotkey('ctrl+c', lambda : handle_exit(status, setup_name))

        write_verbose(
            f"Package to be installed: {package}", verbose, no_color)
        log_info(f"Package to be installed: {package}", logfile)

        package = package.strip()
        package_name = package.lower()
        write_verbose(
            f'Finding closest match to {package_name}...', verbose, no_color)
        log_info(f'Finding closest match to {package_name}...', logfile)

        package_name = package

        write(
            f'Rapidquery Successfully Received {package_name}.json in {round(time, 6)}s', 'bright_yellow', no_color)
        log_info(
            f'Rapidquery Successfully Received {package_name}.json in {round(time, 6)}s', logfile)

        start = timer()

        pkg = json.loads(res[index])

        system_architecture = get_architecture()

        write_verbose('Generating system download path...', verbose, no_color)
        log_info('Generating system download path...', logfile)
        status = 'Download Path'
        download_url = get_download_url(system_architecture, pkg)
        status = 'Got Download Path'

        package_name, source, extension_type, switches = parse_json_response(
            pkg)

        end = timer()

        val = round(Decimal(end) - Decimal(start), 6)
        write(
            f'Electrons Transferred In {val}s', 'cyan', no_color)
        log_info(f'Electrons Transferred In {val}s', logfile)

        write('Initializing Rapid Download...', 'green', no_color)
        log_info('Initializing Rapid Download...', logfile)

        # Downloading The File From Source
        write_verbose(f"Downloading from '{download_url}'", verbose, no_color)
        log_info(f"Downloading from '{download_url}'", logfile)
        status = 'Downloading'
        setup_name = download(download_url, extension_type,
                              package_name, no_progress)
        status = 'Downloaded'

        write('\nFinished Rapid Download', 'green', no_color)
        log_info('Finished Rapid Download', logfile)

        write(
            'Using Rapid Install, Accept Prompts Asking For Admin Permission...', 'cyan', no_color)
        log_info(
            'Using Rapid Install To Complete Setup, Accept Prompts Asking For Admin Permission...', logfile)

        write_debug(
            f'Installing {package_name} through Setup{extension_type}', debug, no_color)
        log_info(
            f'Installing {package_name} through Setup{extension_type}', logfile)

        status = 'Installing'
        # Running The Installer Silently And Completing Setup
        install_package(package_name, switches, extension_type, no_color)
        status = 'Installed'

        end = timer()

        write(
            f'Successfully Installed {package_name}!', 'bright_magenta', no_color)
        log_info(f'Successfully Installed {package_name}!', logfile)

        write_verbose('Installation and setup completed.', verbose, no_color)
        log_info('Installation and setup completed.', logfile)
        write_debug(
            f'Terminated debugger at {strftime("%H:%M:%S")} on install::completion', debug, no_color)
        log_info(
            f'Terminated debugger at {strftime("%H:%M:%S")} on install::completion', logfile)
        closeLog(logfile, 'Install')

        index += 1


@cli.command()
@click.argument('package_name', required=True)
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose mode for uninstallation')
@click.option('--debug', '-d', is_flag=True, help='Enable debug mode for uninstallation')
@click.option('--no-color', '-nc', is_flag=True, help='Disable colored output for installation')
@click.option('--log-output', '-l', 'logfile', help='Log output to the specified file')
@click.option('-y', '--yes', is_flag=True, help='Accept all prompts during installation')
def uninstall(package_name: str, verbose: bool, debug: bool, no_color: bool, logfile: str, yes : bool):
    if logfile:
        logfile = logfile.replace('.txt', '.log')
        createConfig(logfile, logging.INFO, 'Uninstall')

    packages = package_name.split(',')

    correct_names = get_package_names()
    corrected_package_names = []
    corrections = []

    for input_name in packages:
        if input_name not in correct_names:
            corrections.append(difflib.get_close_matches(
                input_name, correct_names, n=1)[0])
        else:
            corrections.append(input_name)

    if corrections:
        for correction in corrections:
            if correction not in packages:
                write_verbose(
                    f'Successfully found closest match: {correction}.', verbose, no_color)
                log_info(
                    f'Successfully found closest match: {correction}.', logfile)
                write(
                    f'Autocorrecting To Closest Match: {correction}', 'bright_magenta', no_color=no_color)
                log_info(
                    f'Autocorrecting To Closest Match: {correction}', logfile)

                if "n" in click.prompt('Do you want to continue? [y/n]')[0]:
                    sys.exit()
                else:
                    corrected_package_names.append(correction)

        for input_name in packages:
            if input_name in correct_names:
                corrected_package_names.append(input_name)

    for p in corrected_package_names:
        write_verbose(
            f'Sending GET request to rapidquery/{p}', verbose, no_color)
        log_info(f'Sending GET request to rapidquery/{p}', logfile)

    res, time = send_req_package(corrected_package_names)

    write_debug(uninstall_debug_headers, debug, no_color)
    for header in uninstall_debug_headers:
        log_info(header, logfile)

    index = 0

    for package in corrected_package_names:

        proc = None
        keyboard.add_hotkey('ctrl+c', lambda: kill_proc(proc))
        package = package.strip()
        package_name = package.lower()
        kill_running_proc(package_name, no_color, verbose, debug, yes)
        pkg = json.loads(res[index])

        write(
            f'Rapidquery Successfully Received {package_name}.json in {round(time, 6)}s', 'bright_green', no_color)
        log_info(
            f'Rapidquery Successfully Received {package_name}.json in {round(time, 6)}s', logfile)

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
                if pkg['uninstall-command'] == '':
                    write(
                        f'Could Not Find Any Existing Installations Of {package_name}', 'yellow', no_color)
                    log_error(
                        f'Could Not Find Any Existing Installations Of {package_name}', logfile)
                    closeLog(logfile, 'Uninstall')
                    index += 1
                    continue
                else:
                    write_verbose("Executing the uninstall command",
                                  verbose, no_color)
                    log_info("Executing the uninstall command", logfile)

                    write(
                        f"Successfully Uninstalled {package_name}", "bright_magenta")

                    try:
                        proc = Popen(shlex.split(
                            pkg['uninstall-command']), stdout=PIPE, stdin=PIPE, stderr=PIPE)
                        proc.wait()
                    except FileNotFoundError:
                        try:
                            proc = Popen(shlex.split(
                                pkg['uninstall-command']), stdout=PIPE, stdin=PIPE, stderr=PIPE, shell=True)
                            proc.wait()
                        except FileNotFoundError:
                            subprocess.call(pkg['uninstall-command'], stdin=PIPE, stdout=PIPE, stderr=PIPE)

                    index += 1
                    write_debug(
                        f'Terminated debugger at {strftime("%H:%M:%S")} on uninstall::completion', debug, no_color)
                    log_info(
                        f'Terminated debugger at {strftime("%H:%M:%S")} on uninstall::completion', logfile)
                    closeLog(logfile, 'Uninstall')
                    continue
            else:
                write(
                    f'Could Not Find Any Existing Installations Of {package_name}', 'yellow', no_color)
                closeLog(logfile, 'Uninstall')
                index += 1
                continue

        write_verbose("Uninstall key found.", verbose, no_color)
        log_info("Uninstall key found.", logfile)

        write(
            f'Successfully Got Uninstall Key In {round(end - start, 4)}s', 'cyan', no_color)
        log_info(
            f'Successfully Got Uninstall Key In {round(end - start, 4)}s', logfile)

        command = ''

        # Key Can Be A List Or A Dictionary Based On Results

        if isinstance(key, list):
            if key != []:
                key = key[0]

        # If QuietUninstallString Exists (Preferable)
        if 'QuietUninstallString' in key:
            command = key['QuietUninstallString']
            command = command.replace('/I', '/X')
            command = command.replace('/quiet', '/passive')

            additional_switches = []
            if "uninstall-switches" in pkg:
                if pkg['uninstall-switches'] != []:
                    write_verbose(
                        "Adding additional uninstall switches", verbose, no_color)
                    log_info("Adding additional uninstall switches", logfile)
                    additional_switches = pkg['uninstall-switches']

            if additional_switches != []:
                for switch in additional_switches:
                    command += ' ' + switch

            write_verbose("Executing the quiet uninstall command",
                          verbose, no_color)
            log_info("Executing the quiet uninstall command", logfile)

            try:
                proc = Popen(shlex.split(
                    command), stdout=PIPE, stdin=PIPE, stderr=PIPE)
                proc.wait()
            except FileNotFoundError as err:
                try:
                    proc = subprocess(shlex.split(command), stdout=PIPE, stdin=PIPE, stderr=PIPE, shell=True)
                    proc.wait()
                except FileNotFoundError:
                    subprocess.call(command, stdin=PIPE, stdout=PIPE, stderr=PIPE)
            if not no_color:
                click.echo(click.style(
                    f"Successfully Uninstalled {package_name}", fg="bright_magenta"))
            if no_color:
                click.echo(click.style(
                    f"Successfully Uninstalled {package_name}"))
            write_verbose("Uninstallation completed.", verbose, no_color)
            log_info("Uninstallation completed.", logfile)

            index += 1
            write_debug(
                f'Terminated debugger at {strftime("%H:%M:%S")} on uninstall::completion', debug, no_color)
            log_info(
                f'Terminated debugger at {strftime("%H:%M:%S")} on uninstall::completion', logfile)
            closeLog(logfile, 'Uninstall')

        # If Only UninstallString Exists (Not Preferable)
        if 'UninstallString' in key and 'QuietUninstallString' not in key:
            command = key['UninstallString']
            command = command.replace('/I', '/X')
            command = command.replace('/quiet', '/passive')

            # Run The UninstallString
            write_verbose("Executing the uninstall command", verbose, no_color)
            log_info("Executing the uninstall command", logfile)
            try:
                proc = Popen(shlex.split(
                    command), stdout=PIPE, stdin=PIPE, stderr=PIPE)
                proc.wait()
            except FileNotFoundError:
                try:
                    proc = Popen(shlex.split(
                        command), stdout=PIPE, stdin=PIPE, stderr=PIPE, shell=True)
                    proc.wait()
                except FileNotFoundError:
                    subprocess.call(command, stdin=PIPE, stdout=PIPE, stderr=PIPE)
            write_verbose("Uninstallation completed.", verbose, no_color)
            log_info("Uninstallation completed.", logfile)
            index += 1
            write_debug(
                f'Terminated debugger at {strftime("%H:%M:%S")} on uninstall::completion', debug, no_color)
            log_info(
                f'Terminated debugger at {strftime("%H:%M:%S")} on uninstall::completion', logfile)
            closeLog(logfile, 'Uninstall')

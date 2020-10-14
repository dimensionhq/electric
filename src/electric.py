from timeit import default_timer as timer
from registry import get_uninstall_key
from time import strftime
from files import files
from extension import *
from helpers import *

import platform
import requests
import difflib
import click
import json
import sys


@click.group()
def cli():
    pass


@cli.command()
@click.argument('package_name', required=True)
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose mode for installation')
@click.option('--debug', '-d', is_flag=True, help='Enable debug mode for installation')
def install(package_name: str, verbose, debug):
    packages = package_name.split(',')
    
    write_verbose(f"Packages to be installed: {package_name}", verbose)

    # Debug headers
    write_debug([f"Attaching debugger at {strftime('%H:%M:%S')} on install",
                 f"Electric is running on {platform.platform()}",
                 f"Command line: \"{' '.join(sys.argv)}\"",
                 f"Arguments: \"{' '.join(sys.argv[1:])}\""], debug)
    
    for package in packages:
        package = package.strip()
        package_name = package.lower()
        BASE = 'http://127.0.0.1:5000/'

        if not is_admin():
            click.echo(click.style(
                'Electric works best on admin command prompts. Some installations may fail if not being run as administrator.',
                fg='yellow'))

        write_verbose(f'Finding closest match to {package_name} ...', verbose)
        try:
            close_name = difflib.get_close_matches(package_name, files, n=1)[0]
        except IndexError:
            click.echo(click.style(
                                  "Package not found.", fg="red")
                                  )
            return
        write_verbose(f'Successfully found closest match: {close_name}.', verbose)
    

        if package_name != close_name:
            click.echo(click.style(f'Autocorrecting To Closest Match: {close_name}', fg='bright_magenta'))
            if "n" in click.prompt('Do you want to continue? [y/n]')[0]:
                sys.exit()

        package_name = close_name

        write_debug(f"Sending GET request to rapidquery/{package_name}.", debug)
        response = requests.get(BASE + f'rapidquery/{package_name}', timeout=15)
        click.echo(
            click.style(f'Rapidquery Successfully Received {package_name}.json in {response.elapsed.total_seconds()}s',
                        fg='green'))
        write_verbose("Response by Rapidquery received.", verbose)
        
        start = timer()

        pkg = json.loads(response.text)

        # Accessing Values Like A Normal JSON
        write_verbose("Getting details about the system architecture ...", verbose)
        system_architecture = get_architecture()
        write_verbose(f"Detected {system_architecture} architecture.", verbose)
        
        download_url = get_download_url(system_architecture, pkg)
        package_name, source, extension_type, switches = parse_json_response(pkg)
        end = timer()

        click.echo(click.style(f'Electrons Transferred In {round(end - start, 4)}s', fg='cyan'))
        click.echo(click.style('Initializing Rapid Download...', fg='green'))

        # Downloading The File From Source
        write_verbose(f"Downloading from '{download_url}'", verbose)
        download(download_url, extension_type, package_name)

        click.echo(click.style('\nFinished Rapid Download', fg='green'))

        click.echo(
            click.style('Using Rapid Install To Complete Setup, Accept Prompts Asking For Admin Permission...',
                        fg='blue'))

        # Running The Installer Silently And Completing Setup
        install_package(package_name, switches, extension_type)

        # Completing Cleanup By Deleting The Setup File From Downloads
        write_verbose("Cleaning up the setup files ...", verbose)
        cleanup(extension_type, package_name)

        end = timer()

        click.echo(click.style(f'Successfully Installed {package_name}!', fg='bright_magenta'))
        write_verbose("Download completed.", verbose)


@cli.command()
@click.argument('package_name', required=True)
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose mode for uninstallation')
@click.option('--debug', '-d', is_flag=True, help='Enable debug mode for uninstallation')
def uninstall(package_name: str, verbose, debug):
    BASE = 'http://127.0.0.1:5000/'
    packages = package_name.split(',')

    write_debug([f"Attaching debugger at {strftime('%H:%M:%S')} on install",
                 f"Electric is running on {platform.platform()}",
                 f"Command line: \"{' '.join(sys.argv)}\"",
                 f"Arguments: \"{' '.join(sys.argv[1:])}\""], debug)
    
    for package in packages:
        package = package.strip()
        package_name = package.lower()

        write_verbose(f'Finding closest match to {package_name} ...', verbose)
        try:
            close_name = difflib.get_close_matches(package_name, files, n=1)[0]
        except IndexError:
            click.echo(click.style(
                                  "Package not found.", fg="red")
                                  )
            return
        write_verbose(f'Successfully found closest match: {close_name}.', verbose)

        if package_name != close_name:
            click.echo(click.style(f'Autocorrecting To Closest Match: {possible[0]}', fg='bright_magenta'))
            if 'n' in click.prompt('Do you want to continue? [y/n]')[0]:
                sys.exit()

        package_name = close_name

        write_debug(f"Sending GET request to rapidquery/{package_name}.", debug)
        response = requests.get(BASE + f'rapidquery/{package_name}', timeout=20)
        click.echo(
            click.style(f'Rapidquery Successfully Received {package_name}.json in {response.elapsed.total_seconds()}s',
                        fg='green'))
        write_verbose("Response by Rapidquery received.", verbose)

        start = timer()
        # Getting UninstallString or QuietUninstallString From The Registry Search Algorithm
        write_verbose("Fetching uninstall key from the registry ...", verbose)
        key = get_uninstall_key(package_name)

        end = timer()


        # If The UninstallString Or QuietUninstallString Doesn't Exist
        if not key:
            name = package_name.split('-')
            final_name = []

            for obj in name:
                final_name.append(obj.capitalize())

            # Get Correct Package Name For Output Message
            package_name = ' '.join(final_name)
            
            pkg = json.loads(response.text)
            if "uninstall-command" in pkg:
                write_verbose("Executing the uninstall command ...", verbose)
                run_uninstall(pkg['uninstall-command'], pkg["package-name"])
                
            else:
                click.echo(click.style(f'Could Not Find Any Existing Installations Of {package_name}', fg='yellow'))
            return

        write_verbose("Uninstall key found.", verbose)
        click.echo(click.style(f'Successfully Got Uninstall Key In {round(end - start, 4)}s', fg='cyan'))

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
            pkg = json.loads(response.text)
            if "uninstall-switches" in pkg:
                write_verbose("Adding additional uninstall switches", verbose)
                additional_switches = pkg['uninstall-switches']

            for switch in additional_switches:
                command += ' ' + switch

            write_verbose("Executing the quiet uninstall command ...", verbose)
            run_uninstall(command, pkg["package-name"])
            write_verbose("Uninstallation completed.", verbose)

        # If Only UninstallString Exists (Not Preferable)
        if 'UninstallString' in key and 'QuietUninstallString' not in key:
            command = key['UninstallString']
            command = command.replace('/I', '/X')
            command = command.replace('/quiet', '/passive')

            # Run The UninstallString
            write_verbose("Executing the uninstall command ...", verbose)
            run_uninstall(command, pkg["package-name"])
            write_verbose("Uninstallation completed.", verbose)

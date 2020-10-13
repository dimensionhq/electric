from timeit import default_timer as timer
from registry import get_uninstall_key
from files import files
from helpers import *

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
def install(package_name: str):
    admin = is_admin()
    packages = package_name.split(',')
    for package in packages:
        package = package.strip()
        package_name = package
        BASE = 'http://127.0.0.1:5000/'

        if not admin:
            click.echo(click.style(
                'Electric Works Best On Admin Command Prompts. Some Installations May Fail If Not Run As Administrator.',
                fg='yellow'))

        possible = difflib.get_close_matches(package_name, files)

        if package_name != possible[0]:
            click.echo(click.style(f'Autocorrecting To Closest Match: {possible[0]}', fg='bright_magenta'))
            if click.prompt('Do you want to continue? [y/n]') == 'n':
                sys.exit()

        package_name = possible[0]

        # Send HTTP Request For Querying File
        response = requests.get(BASE + f'rapidquery/{package_name}', timeout=20)
        click.echo(
            click.style(f'Rapidquery Successfully Received {package_name}.pkg in {response.elapsed.total_seconds()}s',
                        fg='green'))
        start = timer()

        # Converting to usable .json format.
        pkg = js.loads(response.text)

        # Accessing Values Like A Normal JSON
        tem_architecture = get_architecture()
        download_url = get_download_url(system_architecture, pkg)
        package_name, source, extension_type, switches = parse_json_response(pkg)
        end = timer()

        click.echo(click.style(f'Electrons Transferred In {round(end - start, 4)}s', fg='cyan'))
        click.echo(click.style('Initializing Rapid Download...', fg='green'))

        # Downloading The File From Source
        download(download_url, extension_type, package_name)

        click.echo(click.style('\nFinished Rapid Download', fg='green'))

        click.echo(
            click.style('Using Rapid Install To Complete Setup, Accept Prompts Asking For Admin Permission...',
                        fg='blue'))

        # Running The Installer Silently And Completing Setup
        install_package(package_name, switches, extension_type)

        # Completing Cleanup By Deleting The Setup File From Downloads
        cleanup(extension_type, package_name)

        end = timer()

        click.echo(click.style(f'Successfully Installed {package_name}!', fg='bright_magenta'))


@cli.command()
@click.argument('package_name', required=True)
def uninstall(package_name: str):
    BASE = 'http://127.0.0.1:5000/'
    packages = package_name.split(',')
    
    for package in packages:
        package = package.strip()
        package_name = package
        possible = difflib.get_close_matches(package_name, files)

        if package_name != possible[0]:
            click.echo(click.style(f'Autocorrecting To Closest Match: {possible[0]}', fg='bright_magenta'))
            if click.prompt('Do you want to continue? [y/n]') == 'n':
                ()

        package_name = possible[0]

        response = requests.get(BASE + f'rapidquery/{package_name}', timeout=20)
        click.echo(
            click.style(f'Rapidquery Successfully Received {package_name}.json in {response.elapsed.total_seconds()}s',
                        fg='green'))

        start = timer()
        # Getting UninstallString or QuietUninstallString From The Registry Search Algorithm
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
            
            pkg = js.loads(response.text)
            if "uninstall-command" in pkg:
                run_uninstall(pkg['uninstall-command'], pkg["package-name"])
                
            else:
                click.echo(click.style(f'Could Not Find Any Existing Installations Of {package_name}', fg='yellow'))
            return

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
            pkg = js.loads(response.text)
            if "uninstall-switches" in pkg:
                additional_switches = pkg['uninstall-switches']

            for switch in additional_switches:
                command += ' ' + switch
            run_uninstall(command, pkg["package-name"])

        # If Only UninstallString Exists (Not Preferable)
        if 'UninstallString' in key and 'QuietUninstallString' not in key:
            command = key['UninstallString']
            command = command.replace('/I', '/X')
            command = command.replace('/quiet', '/passive')

            # Run The UninstallString
            run_uninstall(command, pkg["package-name"])

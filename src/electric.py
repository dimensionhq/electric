from timeit import default_timer as timer
from registry import get_uninstall_key
from time import strftime
from extension import *
from helpers import *
import platform
import requests
import difflib
import click
import json
import sys


__version__ = '1.0.0b'

@click.group()
@click.version_option(__version__)
@click.pass_context
def cli(ctx):
    pass


@cli.command()
def version():
    click.echo('electric v{}'.format(__version__))


@cli.command()
@click.argument('package_name', required=True)
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose mode for installation')
@click.option('--debug', '-d', is_flag=True, help='Enable debug mode for installation')
@click.option('--no-progress', '-np', is_flag=True, default=False, help='Disable progress bar for installation')
def install(package_name: str, verbose, debug, no_progress):
    
    packages = package_name.split(',')
    
    write_verbose('Sending GET request to rapidquery/all', verbose)
    BASE = 'http://127.0.0.1:5000/'
    response = requests.get(BASE + 'rapidquery/all', timeout=15)

    res = json.loads(response.text)
    package_names = get_package_names(res)

    write_verbose(f"Packages to be installed: {package_name}", verbose)

    # Debug headers
    write_debug([f"Attaching debugger at {strftime('%H:%M:%S')} on install::initialization",
                 f"Electric is running on {platform.platform()}",
                 f"User domain name: {platform.node()}",
                 f"Command line: \"{' '.join(sys.argv)}\"",
                 f"Arguments: \"{' '.join(sys.argv[1:])}\"",
                 f"Current directory: {os.getcwd()}",
                 f"Electric version: {__version__}",
                 f"System architecture detected: {get_architecture()}"
                 ], debug)
    
    for package in packages:
        package = package.strip()
        package_name = package.lower()

        if not is_admin():
            click.echo(click.style(
                'Electric works best on admin command prompts. Some installations may fail if not being run as administrator.',
                fg='yellow'))

        write_verbose(f'Finding closest match to {package_name} ...', verbose)
        try:
            close_name = difflib.get_close_matches(package_name, package_names, n=1)[0]
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
        
        click.echo(
            click.style(f'Rapidquery Successfully Received {package_name}.json in {response.elapsed.total_seconds()}s',
                        fg='green'))
        
        start = timer()

        pkg = res[package_name + '.json']

        # Accessing Values Like A Normal JSON
        system_architecture = get_architecture()
        
        write_verbose('Generating system download path...', verbose)
        download_url = get_download_url(system_architecture, pkg)
        package_name, source, extension_type, switches = parse_json_response(pkg)
        end = timer()

        click.echo(click.style(f'Electrons Transferred In {round(end - start, 4)}s', fg='cyan'))
        click.echo(click.style('Initializing Rapid Download...', fg='green'))

        # Downloading The File From Source
        write_verbose(f"Downloading from '{download_url}'", verbose)
        download(download_url, extension_type, package_name, no_progress)

        click.echo(click.style('\nFinished Rapid Download', fg='green'))

        click.echo(
            click.style('Using Rapid Install To Complete Setup, Accept Prompts Asking For Admin Permission...',
                        fg='blue'))

        write_debug(f'Installing {package_name} through Setup{extension_type}', debug)
        # Running The Installer Silently And Completing Setup
        install_package(package_name, switches, extension_type)

        # Completing Cleanup By Deleting The Setup File From Downloads
        write_verbose('Cleaning up the setup and installation files...', verbose)
        cleanup(extension_type, package_name)

        end = timer()

        click.echo(click.style(f'Successfully Installed {package_name}!', fg='bright_magenta'))
        write_verbose('Installation and setup completed.', verbose)
        write_debug(f'Terminated debugger at {strftime("%H:%M:%S")} on install::completion', debug)


@cli.command()
@click.argument('package_name', required=True)
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose mode for uninstallation')
@click.option('--debug', '-d', is_flag=True, help='Enable debug mode for uninstallation')
def uninstall(package_name: str, verbose, debug):

    packages = package_name.split(',')

    BASE = 'http://127.0.0.1:5000/'
    response = requests.get(BASE + 'rapidquery/all', timeout=15)
    res = json.loads(response.text)
    package_names = get_package_names(res)
    pkg = res[package_name + ".json"]

    write_debug([f"Attaching debugger at {strftime('%H:%M:%S')} on uninstall",
                 f"Electric is running on {platform.platform()}",
                 f"User domain name: {platform.node()}",
                 f"Command line: \"{' '.join(sys.argv)}\"",
                 f"Arguments: \"{' '.join(sys.argv[1:])}\"",
                 f"Current directory: {os.getcwd()}",
                 f"Electric version: {__version__}",
                 f"System architecture detected: {get_architecture()}"
                 ], debug)
    
    for package in packages:
        package = package.strip()
        package_name = package.lower()

        write_verbose(f'Finding closest match to {package_name}', verbose)
        try:
            close_name = difflib.get_close_matches(package_name, package_names, n=1)[0]
        except IndexError:
            click.echo(click.style(
                                  "Package not found.", fg="red")
                                  )
            return
        write_verbose(f'Successfully found closest match: {close_name}.', verbose)

        if package_name != close_name:
            click.echo(click.style(f'Autocorrecting To Closest Match: {close_name[0]}', fg='bright_magenta'))
            if 'n' in click.prompt('Do you want to continue? [y/n]')[0]:
                sys.exit()

        package_name = close_name

        click.echo(
            click.style(f'Rapidquery Successfully Received {package_name}.json in {response.elapsed.total_seconds()}s',
                        fg='green'))
        
        start = timer()
        # Getting UninstallString or QuietUninstallString From The Registry Search Algorithm
        write_verbose("Fetching uninstall key from the registry...", verbose)
        key = get_uninstall_key(package_name)

        end = timer()

        # If The UninstallString Or QuietUninstallString Doesn't Exist
        if not key:
            write_verbose('No registry keys found', verbose)          
            if "uninstall-command" in pkg:
                write_verbose("Executing the uninstall command", verbose)
                run_uninstall(pkg['uninstall-command'], pkg["package-name"])
                write_debug(f'Terminated debugger at {strftime("%H:%M:%S")} on uninstall::completion', debug)
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
            if "uninstall-switches" in pkg:
                write_verbose("Adding additional uninstall switches", verbose)
                additional_switches = pkg['uninstall-switches']

            for switch in additional_switches:
                command += ' ' + switch

            write_verbose("Executing the quiet uninstall command", verbose)
            run_uninstall(command, pkg["package-name"])
            write_verbose("Uninstallation completed.", verbose)
            write_debug(f'Terminated debugger at {strftime("%H:%M:%S")} on uninstall::completion', debug)

        # If Only UninstallString Exists (Not Preferable)
        if 'UninstallString' in key and 'QuietUninstallString' not in key:
            command = key['UninstallString']
            command = command.replace('/I', '/X')
            command = command.replace('/quiet', '/passive')

            # Run The UninstallString
            write_verbose("Executing the uninstall command", verbose)
            run_uninstall(command, pkg["package-name"])
            write_verbose("Uninstallation completed.", verbose)
            write_debug(f'Terminated debugger at {strftime("%H:%M:%S")} on uninstall::completion', debug)

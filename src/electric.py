import click
# from urllib.request import urlretrieve, urlopen
import requests
import json as js
from sys import exit
from helpers import get_architecture, get_download_url, parse_json_response, download, install_package, cleanup
from timeit import default_timer as timer
from Server.main import files
import difflib


@click.group()
def cli():
    pass


@cli.command()
@click.argument('package_name', required=True)
def install(package_name):
    BASE = 'http://127.0.0.1:5000/'
    all_files = []

    for file in files:
        all_files.append(file.replace('.json', ''))

    possible = difflib.get_close_matches(package_name, all_files)
    if package_name != possible[0]:
        click.echo(click.style(f'Autocorrecting To Closest Match: {possible[0]}', fg='bright_magenta'))
        if click.prompt('Do you want to continue? [y/n]') == 'n':
            exit()

    package_name = possible[0]

    # Send HTTP Request For Querying File
    response = requests.get(BASE + f'rapidquery/{package_name}', timeout=20)
    click.echo(
        click.style(f'Rapidquery Successfully Received {package_name}.json in {response.elapsed.total_seconds()}s',
                    fg='green'))
    start = timer()

    # Converting to usable .json format.
    json = js.loads(response.text)

    # Accessing Values Like A Normal JSON
    system_architecture = get_architecture()
    download_url = get_download_url(system_architecture, json)
    package_name, source, extension_type, switches = parse_json_response(json)
    end = timer()

    click.echo(click.style(f'Electrons Transferred In {round(end - start, 4)}s', fg='cyan'))

    click.echo(click.style('Initializing Rapid Download...', fg='green'))

    download(download_url, extension_type, package_name)

    click.echo(click.style('\nFinished Rapid Download', fg='green'))

    click.echo(
        click.style('Using Rapid Install To Complete Setup, Accept Prompts Asking For Admin Permission...', fg='blue'))
    install_package(package_name, switches, extension_type)

    cleanup(extension_type, package_name)

    click.echo(click.style(f'Successfully Installed {package_name}!', fg='bright_magenta'))


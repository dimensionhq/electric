######################################################################
#                     OFFICIAL ELECTRIC INSTALLER                    #
######################################################################


import argparse
import requests
import zipfile
import ctypes
import shutil
import click
import tqdm
import sys
import os


class Metadata:
    def __init__(self, silent, verbose):
        self.silent = silent
        self.verbose = verbose


parser = argparse.ArgumentParser(description='Electric Installer')
parser.add_argument('--silent', action="store_true")
parser.add_argument('--verbose', action="store_true")
args = parser.parse_args()
metadata = Metadata(args.silent, args.verbose)


def write(text: str, color: str, metadata: Metadata):
    if not metadata.silent:
        click.echo(click.style(text, fg=color))


def write_verbose(text: str, color: str, metadata: Metadata):
    if not metadata.silent and metadata.verbose:
        click.echo(click.style(text, fg=color))


def isAdmin():
    try:
        is_admin = (os.getuid() == 0)
    except AttributeError:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
    return is_admin


while True:
    if not metadata.silent:
        try:
            admin = int(input(
                'Enter 1 For Administrator Installation \nEnter 2 For Non-Administrator Installation\n>> '))
            break
        except ValueError:
            write('Please Enter A Valid Number [1 or 2]', 'red', metadata)
    else:
        admin = 2


if isAdmin() and admin == 1:
    parent_dir = r'C:\\'
    electric_dir = parent_dir + 'Electric'
    write_verbose(
        f'Creating Directory Electric at {parent_dir} With Destination {electric_dir}', 'bright_yellow', metadata)
    os.mkdir(electric_dir)
    write(R'Successfully Created Directory At C:\Electric', 'green', metadata)
    write_verbose(
        f'Downloading Electric.zip From /install To {electric_dir}\\Electric.zip', 'bright_yellow', metadata)
    with open(f'{electric_dir}\\Electric.zip', "wb") as f:
        response = requests.get(
            'https://electric-package-manager.herokuapp.com/install', stream=True)
        total_length = response.headers.get('content-length')

        if total_length is None:
            f.write(response.content)
        else:
            dl = 0
            full_length = int(total_length)

            for data in response.iter_content(chunk_size=7096):
                dl += len(data)
                f.write(data)

                complete = int(20 * dl / full_length)
                fill_c, unfill_c = '#' * complete, ' ' * (20 - complete)
                sys.stdout.write(
                    f"\r[{fill_c}{unfill_c}] ⚡  {round(dl / full_length * 100, 1)} %  ⚡  {round(dl / 1000000, 1)} / {round(full_length / 1000000, 1)} MB ")
                sys.stdout.flush()

    write('\nSuccessfully Downloaded Electric.zip', 'green', metadata)
    write('Unzipping Electric.zip', 'green', metadata)
    write_verbose(
        f'Unzipping Electric.zip at {electric_dir}\\Electric.zip', 'yellow', metadata)
    with zipfile.ZipFile(f'{electric_dir}\\Electric.zip') as zf:
        for member in tqdm.tqdm(zf.infolist(), smoothing=1.0, ncols=60):
            try:
                zf.extract(member, f'{electric_dir}\\electric')
            except zipfile.error as e:
                pass
    os.remove(f'{electric_dir}\\Electric.zip')
    os.rename(f'{electric_dir}\electric', Rf'{electric_dir}\file')
    shutil.move(Rf'{electric_dir}\file\electric',
                f'{electric_dir}\electric')
    shutil.rmtree(Rf'C:\Electric\file')
    write('Successfully Unzipped And Extracted Electric.zip', 'green', metadata)
    write('Running setup.py For Electric', 'green', metadata)
    os.chdir(Rf'C:\Electric\electric')
    os.system('pip install --editable .')
    write('Successfully Installed Electric, Type `electric` To Get A List Of Help Commands!', 'green', metadata)


if admin == 1 and not isAdmin():
    click.echo(click.style(
        'Retry Installation With Administrator Permissions', fg='red'), err=True)


elif admin == 2:
    print('User installation')

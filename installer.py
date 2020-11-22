######################################################################
#                     OFFICIAL ELECTRIC INSTALLER                    #
######################################################################
import os
os.system('pip install tqdm')
os.system('pip install requests')
os.system('pip install click')


import click

click.echo(click.style('All Installer Dependencies Installed!', fg='green'))

import argparse
import requests
import zipfile
import ctypes
import shutil
import tqdm
import sys

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
            installation = int(input(
                'Enter 1 For Default Installation \nEnter 2 For Custom Installation\n>> '))
            break
        except ValueError:
            write('Please Enter A Valid Number [1 or 2]', 'red', metadata)
    else:
        installation = 1


if isAdmin() and installation == 1:
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
            'https://electric-package-manager.herokuapp.com/install/windows/zip', stream=True)
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
                zf.extract(member, f'{electric_dir}\\electric-dist')
            except zipfile.error as e:
                pass
    os.remove(f'{electric_dir}\\Electric.zip')
    os.rename(f'{electric_dir}\electric-dist', Rf'{electric_dir}\file')
    shutil.move(Rf'{electric_dir}\file\electric-dist',
                f'{electric_dir}\electric')
    shutil.rmtree(Rf'C:\Electric\file')
    write('Successfully Unzipped And Extracted Electric.zip', 'green', metadata)
    write('Running setup.py For Electric', 'green', metadata)
    os.chdir(Rf'C:\Electric\electric')
    os.system('pip install --editable .')
    write('Successfully Installed Electric, Type `electric` To Get A List Of Help Commands!', 'green', metadata)

if isAdmin() and installation == 2 and not metadata.silent:
    install_directory = input('Enter the directory you would like to install electric to:\n\n[Enter `DEFAULT` for default directory]\nNOTE:[Don\'t Include `\Electric` In Path]\n>> ')
    if install_directory:
        while True:
            if not metadata.silent:
                compression_type = input(
                    'Enter .zip For A ZIP Installation \nEnter .7z For A 7-ZIP Installation\nEnter .tar For A TAR Installation\n>> ')
                if compression_type not in ['.zip', '.7z', '.tar']:
                    sys.exit(1)
                break
        
        if compression_type == '.zip':
            if install_directory == 'DEFAULT':
                parent_dir = r'C:\\'
            else:
                parent_dir = install_directory + '\\'
            electric_dir = parent_dir + 'Electric'
            write_verbose(
                f'Creating Directory Electric at {parent_dir} With Destination {electric_dir}', 'bright_yellow', metadata)
            os.mkdir(electric_dir)
            write(Rf'Successfully Created Directory At {electric_dir}', 'green', metadata)
            write_verbose(
                f'Downloading Electric.zip From /install To {electric_dir}\\Electric.zip', 'bright_yellow', metadata)
            with open(f'{electric_dir}\\Electric.zip', "wb") as f:
                response = requests.get(
                    'https://electric-package-manager.herokuapp.com/install/windows/zip', stream=True)
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
                        zf.extract(member, f'{electric_dir}\\electric-dist')
                    except zipfile.error as e:
                        pass
            os.remove(f'{electric_dir}\\Electric.zip')
            os.rename(f'{electric_dir}\electric-dist', Rf'{electric_dir}\file')
            print(electric_dir)
            shutil.move(Rf'{electric_dir}\file\electric-dist',
                        f'{electric_dir}\electric')
            shutil.rmtree(Rf'{electric_dir}\file')
            write('Successfully Unzipped And Extracted Electric.zip', 'green', metadata)
            write('Running setup.py For Electric', 'green', metadata)
            os.chdir(Rf'{electric_dir}\electric')
            os.system('pip install --editable .')
            write('Successfully Installed Electric, Type `electric` To Get A List Of Help Commands!', 'green', metadata)

        if compression_type == '.7z':
            os.system('pip install py7zr')
            click.echo(click.style('Successfully Installed All .7z Dependencies!', fg='green'))
            if install_directory == 'DEFAULT':
                parent_dir = r'C:\\'
            else:
                parent_dir = install_directory + '\\'
            electric_dir = parent_dir + 'Electric'
            write_verbose(
                f'Creating Directory Electric at {parent_dir} With Destination {electric_dir}', 'bright_yellow', metadata)
            os.mkdir(electric_dir)
            write(Rf'Successfully Created Directory At {electric_dir}', 'green', metadata)
            write_verbose(
                f'Downloading Electric.zip From /install To {electric_dir}\\Electric.7z', 'bright_yellow', metadata)
            with open(f'{electric_dir}\\Electric.7z', "wb") as f:
                response = requests.get(
                    'https://electric-package-manager.herokuapp.com/install/windows/7z', stream=True)
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

            import py7zr

            archive = py7zr.SevenZipFile(f'{electric_dir}\\Electric.7z', 'r')
            archive.extractall(electric_dir)
            archive.close()
            os.remove(f'{electric_dir}\\Electric.7z')
            os.rename(f'{electric_dir}\\electric-dist', f'{electric_dir}\\electric')
            write('\nSuccessfully Unzipped And Extracted Electric.7z', 'green', metadata)
            write('Running setup.py For Electric', 'green', metadata)
            os.chdir(Rf'{electric_dir}\electric')
            os.system('pip install --editable .')
            write('Successfully Installed Electric, Type `electric` To Get A List Of Help Commands!', 'green', metadata)
        
        if compression_type == '.tar':
            if install_directory == 'DEFAULT':
                parent_dir = r'C:\\'
            else:
                parent_dir = install_directory + '\\'
            electric_dir = parent_dir + 'Electric'
            write_verbose(
                f'Creating Directory Electric at {parent_dir} With Destination {electric_dir}', 'bright_yellow', metadata)
            os.mkdir(electric_dir)
            write(Rf'Successfully Created Directory At {electric_dir}', 'green', metadata)
            write_verbose(
                f'Downloading Electric.zip From /install To {electric_dir}\\Electric.tar', 'bright_yellow', metadata)
            with open(f'{electric_dir}\\Electric.tar', "wb") as f:
                response = requests.get(
                    'https://electric-package-manager.herokuapp.com/install/windows/tar', stream=True)
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
            
            import tarfile

            tar = tarfile.open(f'{electric_dir}\\Electric.tar')
            tar.extractall(electric_dir)
            tar.close()

            os.remove(f'{electric_dir}\\Electric.tar')
            os.rename(f'{electric_dir}\\electric-dist', f'{electric_dir}\\electric')
            write('\nSuccessfully Unzipped And Extracted Electric.tar', 'green', metadata)
            write('Running setup.py For Electric', 'green', metadata)
            os.chdir(Rf'{electric_dir}\electric')
            os.system('pip install --editable .')
            write('Successfully Installed Electric, Type `electric` To Get A List Of Help Commands!', 'green', metadata)


if not isAdmin():
    click.echo(click.style(
        'Retry Installation With Administrator Permissions', fg='red'), err=True)

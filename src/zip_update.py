import json
from json.decoder import JSONDecodeError

import requests
from Classes.Metadata import Metadata
from Classes.PortablePacket import PortablePacket
from extension import write
from colorama import Fore
from zip_utils import *
import os
import sys

home = os.path.expanduser('~')


def update_portable(ctx, packet: PortablePacket, metadata: Metadata):
    import shutil
    import click
    from difflib import get_close_matches

    write(
        f'Updating [ {Fore.LIGHTCYAN_EX}{packet.display_name}{Fore.RESET} ]', 'white', metadata)

    options = os.listdir(rf'{home}\electric')
    matches = get_close_matches(
        rf'{home}\electric\{packet.json_name}@{packet.latest_version}', options)
    if len(matches) == 1:
        # similar package exists and we need to get the version of the currently installed package.
        current_version = matches[0].split('@')[-1].replace('.json', '')

        if current_version != packet.latest_version:
            write(f'{packet.display_name} Will Be Updated From ({current_version}) => ({packet.latest_version})', 'green', metadata)
            write('Requesting Currently Installed Version', 'yellow', metadata)

        REQA = 'http://electric-env.eba-9m7janw8.us-east-1.elasticbeanstalk.com/package/'

        try:
            response = requests.get(
                REQA + packet.json_name + '.json', timeout=5)
        except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout):
            click.echo(click.style(
                f'Failed to request {packet.json_name}.json from server', 'red'))
            sys.exit()

        try:
            res = json.loads(response.text)
        except JSONDecodeError:
            click.echo(click.style(f'{packet.json_name} not found!', 'red'))
            sys.exit()

        pkg = res

        pkg = pkg['portable']

        keys = list(pkg[current_version].keys())
        data = {
            'display-name': res['display-name'],
            'package-name': res['package-name'],
            'latest-version': res['latest-version'],
            'url': pkg[current_version]['url'],
            'file-type': pkg[current_version]['file-type'] if 'file-type' in keys else None,
            'extract-dir': res['package-name'],
            'chdir': pkg[current_version]['chdir'] if 'chdir' in keys else [],
            'bin': pkg[current_version]['bin'] if 'bin' in keys else [],
            'shortcuts': pkg[current_version]['shortcuts'] if 'shortcuts' in keys else [],
            'pre-install': pkg[current_version]['pre-install'] if 'pre-install' in keys else [],
            'post-install': pkg[current_version]['post-install'] if 'post-install' in keys else [],
            'install-notes': pkg[current_version]['install-notes'] if 'install-notes' in keys else None,
            'uninstall-notes': pkg[current_version]['uninstall-notes'] if 'uninstall-notes' in keys else None,
            'set-env': pkg[current_version]['set-env'] if 'set-env' in keys else None,
            'persist': pkg[current_version]['persist'] if 'persist' in keys else None,
            'checksum': pkg[current_version]['checksum'] if 'checksum' in keys else None,
            'dependencies': pkg[current_version]['dependencies'] if 'dependencies' in keys else None,
        }

        old_packet = PortablePacket(data)

        # continue updating the package
        # if a directory has to be saved before uninstallation and installation of the portable

        if old_packet.persist:
            install_directory = rf'{home}\electric\{old_packet.json_name}@{current_version}\\'

            if old_packet.chdir:
                install_directory += old_packet.chdir + '\\'
                install_directory = install_directory.replace('\\\\', '\\')

            if isinstance(old_packet.persist, list):
                for path in old_packet.persist:
                    # multiple directories to backup
                    try:
                        shutil.copytree(
                            install_directory + path, rf'{home}\electric\Persist\{old_packet.json_name}@{current_version}\{path}')
                    except FileExistsError:
                        pass

            else:
                # only 1 directory to backup
                if old_packet.persist:
                    try:
                        shutil.copytree(install_directory + old_packet.persist,
                                        rf'{home}\electric\Persist\{old_packet.json_name}@{current_version}\{old_packet.persist}')
                    except FileExistsError:
                        pass

        os.system(f'electric uninstall {packet.json_name} --portable')
        os.system(f'electric install {packet.json_name} --portable')

        new_install_dir = rf'{home}\electric\{packet.json_name}@{packet.latest_version}\\'
        if packet.chdir:
            new_install_dir += packet.chdir + '\\'

        new_install_dir = new_install_dir.replace('\\\\', '\\')

        if old_packet.persist:
            write('Restoring Old Files And Data', 'green', metadata)

            if isinstance(old_packet.persist, list):
                for path in old_packet.persist:
                    shutil.rmtree(new_install_dir + path)
                    shutil.copytree(
                        rf'{home}\electric\Persist\{old_packet.json_name}@{current_version}\{path}', new_install_dir + path)
            else:
                shutil.rmtree(new_install_dir.replace(
                    '\\\\', '\\') + old_packet.persist.replace('\\\\', '\\'))
                shutil.copytree(
                    rf'{home}\electric\Persist\{old_packet.json_name}@{current_version}\{old_packet.persist}', new_install_dir + old_packet.persist)

        # completed backup of files to backups directory
        write(
            rf'Successfully Completed Backup Of Required Data To {home}\electric\Persist', 'cyan', metadata)

    else:
        write(
            f'Could not find any existing installations of {packet.display_name}', 'red', metadata)

    write(f'Successfully Updated {packet.display_name}',
          'bright_magenta', metadata)
    sys.exit()

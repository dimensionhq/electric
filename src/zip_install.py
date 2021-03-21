from logger import log_info
from Classes.Metadata import Metadata
from Classes.PortablePacket import PortablePacket
from timeit import default_timer as timer
from extension import write, write_debug
from colorama import Fore
from zip_utils import *
import os
import sys

home = os.path.expanduser('~')


def install_portable(packet: PortablePacket, metadata: Metadata):
    if find_existing_installation(f'{packet.extract_dir}@{packet.latest_version}'):
        write(
            f'Found Existing Installation Of {packet.display_name}', 'bright_yellow', metadata)
        continue_installation = confirm(
            f'Would you like to reinstall {packet.display_name}?')
        if continue_installation:
            pass
        else:
            sys.exit()

    if packet.dependencies:
        install_dependencies(packet, metadata)

    changes_environment = False
    shortcuts = packet.shortcuts
    extract_dir = packet.extract_dir
    write_debug(
        f'Downloading {packet.json_name}{packet.file_type} from {packet.url}', metadata)
    log_info(
        f'Downloading {packet.json_name}{packet.file_type} from {packet.url}', metadata)
    show_progress_bar = True if not metadata.silent and not metadata.no_progress else False

    if isinstance(packet.url, str):
        download(packet, packet.url, '.zip', rf'{home}\electric\\' + f'{packet.extract_dir}@{packet.latest_version}',
                 metadata, show_progress_bar=show_progress_bar, is_zip=True)

        unzip_dir = unzip_file(f'{packet.extract_dir}@{packet.latest_version}' +
                               '.zip', extract_dir, packet.file_type, metadata)

    elif isinstance(packet.url, list):
        idx = 0
        for url in packet.url:
            if idx == 0:
                download(packet, url['url'], '.zip', rf'{home}\electric\\' + f'{packet.extract_dir}@{packet.latest_version}',
                         metadata, show_progress_bar=show_progress_bar, is_zip=True)
                unzip_dir = unzip_file(
                    f'{packet.extract_dir}@{packet.latest_version}' + '.zip', extract_dir, url['file-type'], metadata)

            else:
                write(
                    f'Downloading {url["file-name"]}{url["file-type"]}', 'cyan', metadata)
                download(packet, url['url'], url['file-type'],
                         rf'{home}\electric\extras\{packet.extract_dir}@{packet.latest_version}\\{url["file-name"]}', metadata, show_progress_bar=False, is_zip=False)

            idx += 1

    if packet.pre_install:
        if packet.pre_install['type'] == 'powershell':
            packet.pre_install['code'] = [l.replace('<dir>', unzip_dir.replace(
                '\\\\', '\\')) for l in packet.pre_install['code']]

            packet.pre_install['code'] = [l.replace('<extras>', rf'{home}\electric\extras\{packet.extract_dir}@{packet.latest_version}'.replace(
                '\\\\', '\\')) for l in packet.pre_install['code']]

            if not os.path.isdir(rf'{home}\electric\temp\Scripts'):
                try:
                    os.mkdir(rf'{home}\electric\temp')
                except:
                    # temp directory already exists
                    pass

                os.mkdir(rf'{home}\electric\temp\Scripts')

            with open(rf'{home}\electric\temp\Scripts\temp.ps1', 'w+') as f:
                for line in packet.pre_install['code']:
                    f.write(f'\n{line}')
            os.system(
                rf'powershell -executionpolicy bypass -File {home}\electric\temp\Scripts\temp.ps1')
            write('Successfully Executed Pre-Install Code',
                  'bright_green', metadata)

        if packet.pre_install['type'] == 'bat' or packet.pre_install['type'] == 'cmd':
            packet.pre_install['code'] = [l.replace('<dir>', unzip_dir.replace(
                '\\\\', '\\')) for l in packet.pre_install['code']]

            packet.pre_install['code'] = [l.replace('<extras>', rf'{home}\electric\extras\{packet.extract_dir}@{packet.latest_version}'.replace(
                '\\\\', '\\')) for l in packet.pre_install['code']]

            if not os.path.isdir(rf'{home}\electric\temp\Scripts'):
                try:
                    os.mkdir(rf'{home}\electric\temp')
                except:
                    # temp directory already exists
                    pass

                os.mkdir(rf'{home}\electric\temp\Scripts')

            with open(rf'{home}\electric\temp\Scripts\temp.bat', 'w+') as f:
                for line in packet.pre_install['code']:
                    f.write(f'\n{line}')
            os.system(
                rf'{home}\electric\temp\Scripts\temp.bat')
            write('Successfully Executed Pre-Install Code',
                  'bright_green', metadata)

        if packet.pre_install['type'] == 'python':
            code = ''''''

            for l in packet.pre_install['code']:
                code += l + '\n'

            exec(code)

    if packet.chdir:
        dir = packet.chdir
        unzip_dir += f'\\{dir}\\'

    if packet.bin:
        if isinstance(packet.bin, list):
            for bin in packet.bin:
                shim_dir = unzip_dir
                shim = ''.join(bin.split('.')[:-1])
                shim_ext = bin.split('.')[-1]
                if '\\' in bin:
                    shim = ''.join(bin.split('\\')[-1])
                    shim = ''.join(shim.split('.')[:-1])
                    shim_ext = bin.split('.')[-1]
                    shim_dir += ' '.join(bin.split('\\')
                                         [:-1]).replace(' ', '\\')

                start = timer()
                generate_shim(f'{shim_dir}', shim, shim_ext)
                end = timer()
                write(
                    f'{Fore.LIGHTCYAN_EX}Successfully Generated {shim} Shim In {round(end - start, 5)} seconds{Fore.RESET}', 'white', metadata)

    if shortcuts:
        for shortcut in shortcuts:
            shortcut_name = shortcut['shortcut-name']
            file_name = shortcut['file-name']
            create_start_menu_shortcut(unzip_dir, file_name, shortcut_name)

    if packet.set_env:
        changes_environment = True
        write(
            f'Setting Environment Variable {packet.set_env["name"]}', 'bright_green', metadata)
        set_environment_variable(packet.set_env['name'], packet.set_env['value'].replace(
            '<install-directory>', unzip_dir).replace('\\\\', '\\'))

    if changes_environment:
        write(
            f'{Fore.LIGHTGREEN_EX}The PATH environment variable has changed. Run `refreshenv` to refresh your environment variables.{Fore.RESET}', 'white', metadata)

    if packet.post_install:
        for line in packet.post_install:
            exec(line.replace('<install-directory>', unzip_dir).replace('<extras>',
                 rf'{home}\electric\extras\{packet.extract_dir}@{packet.latest_version}'))

    if packet.install_notes:
        display_notes(packet, unzip_dir, metadata)

    write(f'Successfully Installed {packet.display_name}', 'magenta', metadata)

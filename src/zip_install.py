from subprocess import PIPE, Popen
from Classes.Metadata import Metadata
from Classes.PortablePacket import PortablePacket
from timeit import default_timer as timer
from extension import write, write_debug
from colorama import Fore
from zip_utils import *
import click
import os

home = os.path.expanduser('~')


def install_portable(packet: PortablePacket, metadata: Metadata):
    if find_existing_installation(f'{packet.extract_dir}@{packet.latest_version}'):
        write(f'Found Existing Installation Of {packet.display_name}', 'yellow', metadata)
        continue_installation = click.confirm(f'Would you like to reinstall {packet.display_name}?')
        if continue_installation:
            pass
        else:
            sys.exit()

    write(f'Installing [ {Fore.CYAN}{packet.display_name}{Fore.RESET} ]', 'white', metadata)
    changes_environment = False
    shortcuts = packet.shortcuts
    extract_dir = packet.extract_dir
    write_debug(f'Downloading {packet.json_name}{packet.file_type} from {packet.url}', metadata)
    show_progress_bar = True if not metadata.silent and not metadata.no_progress else False
    
    if isinstance(packet.url, str):
        download(packet, packet.url, '.zip', rf'{home}\electric\\' + f'{packet.extract_dir}@{packet.latest_version}', metadata, show_progress_bar=show_progress_bar, is_zip=True)
        unzip_dir = unzip_file(f'{packet.extract_dir}@{packet.latest_version}' + '.zip', extract_dir, packet.file_type, metadata)

    elif isinstance(packet.url, list):
        idx = 0
        for url in packet.url:
            if idx == 0:
                download(packet, url['url'], '.zip', rf'{home}\electric\\' + f'{packet.extract_dir}@{packet.latest_version}', metadata, show_progress_bar=show_progress_bar, is_zip=True)
                unzip_dir = unzip_file(f'{packet.extract_dir}@{packet.latest_version}' + '.zip', extract_dir, url['file-type'], metadata)

            else:
                download(packet, url['url'], url['file-type'], rf'{home}\electric\{packet.extract_dir}@{packet.latest_version}\electric\\{url["file-name"]}', metadata, show_progress_bar=False, is_zip=False)
            
            idx += 1


    if packet.pre_install:
        if packet.pre_install['type'] == 'powershell':
            packet.pre_install['code'] = [ l.replace('<dir>', unzip_dir.replace('\\\\', '\\')) for l in packet.pre_install['code'] ]
            if not os.path.isdir(rf'{home}\electric\temp\Scripts'):
                os.mkdir(rf'{home}\electric\temp')
                os.mkdir(rf'{home}\electric\temp\Scripts')
            with open(rf'{home}\electric\temp\Scripts\temp.ps1', 'w+') as f:
                for line in packet.pre_install['code']:
                    f.write(f'\n{line}')
            os.system(rf'powershell -executionpolicy bypass -File {home}\electric\temp\Scripts\temp.ps1')
            write('Successfully Executed Pre-Install Code', 'green', metadata)

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
                    shim_dir += ' '.join(bin.split('\\')[:-1]).replace(' ', '\\')
                
                start = timer()
                generate_shim(f'{shim_dir}', shim, shim_ext)
                end = timer()
                write(f'{Fore.CYAN}Successfully Generated {shim} Shim In {round(end - start, 5)} seconds{Fore.RESET}', 'white', metadata)
    
    if shortcuts:
        for shortcut in shortcuts:
            shortcut_name = shortcut['shortcut-name']
            file_name = shortcut['file-name']
            create_start_menu_shortcut(unzip_dir, file_name, shortcut_name)

    if changes_environment:
        write(f'{Fore.GREEN}\nRefreshing Environment Variables{Fore.RESET}', 'white', metadata)
        os.system(rf'{home}\Desktop\Electric\Electric-Windows\src\scripts\refreshvars.cmd')

    if packet.post_install:
        for line in packet.post_install:
            eval(line.replace('<dir>', unzip_dir))

    if packet.notes:
        display_notes(packet, unzip_dir, metadata)

    write(f'Successfully Installed {packet.display_name}', 'magenta', metadata)
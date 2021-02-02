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
    if find_existing_installation(f'{packet.extract_dir}{packet.latest_version}'):
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
    download(packet.url, '.zip', rf'{home}\electric\\' + f'{packet.extract_dir}{packet.latest_version}', metadata, show_progress_bar= True if not metadata.silent and not metadata.no_progress else False)
    unzip_dir = unzip_file(f'{packet.extract_dir}{packet.latest_version}' + '.zip', extract_dir, packet.file_type, metadata)
    
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
                
    for shortcut in shortcuts:
        shortcut_name = shortcut['shortcut-name']
        file_name = shortcut['file-name']
        create_start_menu_shortcut(unzip_dir, file_name, shortcut_name)

    if changes_environment:
        write(f'{Fore.GREEN}\nRefreshing Environment Variables{Fore.RESET}', 'white', metadata)
        os.system(rf'{home}\Desktop\Electric\Electric-Windows\src\scripts\refreshvars.cmd')

    if packet.post_install:
        for line in packet.post_install:
            eval(line)

    if packet.notes:
        display_notes(packet, metadata)

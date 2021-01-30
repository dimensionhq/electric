from Classes.Metadata import Metadata
from Classes.PortablePacket import PortablePacket
from timeit import default_timer as timer
from colorama import Fore
from extension import write, write_debug
from zip_utils import *
import os

home = os.path.expanduser('~')

def install_portable(packet: PortablePacket, metadata: Metadata):
    print(f'Installing [ {Fore.CYAN}{packet.display_name}{Fore.RESET} ]')
    changes_environment = False
    shortcuts = packet.shortcuts
    extract_dir = packet.extract_dir
    write_debug(f'Downloading {packet.json_name}{packet.file_type} from {packet.url}', metadata)
    download(packet.url, '.zip', rf'{home}\electric\\' + extract_dir)
    unzip_dir = unzip_file(extract_dir + '.zip', extract_dir, packet.file_type)
    if packet.chdir:
        dir = packet.chdir
        unzip_dir += f'\\{dir}\\'
    
    if packet.bin:
        if isinstance(packet.bin, list):
            for sh in packet.bin:
                shim_dir = unzip_dir 
                shim = ''.join(sh.split('.')[:-1])
                shim_ext = sh.split('.')[-1]
                if '\\' in sh:
                    shim = ''.join(sh.split('\\')[-1])
                    shim = ''.join(shim.split('.')[:-1])
                    shim_ext = sh.split('.')[-1]
                    shim_dir += ' '.join(sh.split('\\')[:-1]).replace(' ', '\\')
                
                start = timer()
                generate_shim(f'{shim_dir}', shim, shim_ext)
                end = timer()
                print(f'{Fore.CYAN}Successfully Generated {shim} Shim In {round(end - start, 5)} seconds{Fore.RESET}')
    

    for shortcut in shortcuts:
        shortcut_name = shortcut['shortcut-name']
        file_name = shortcut['file-name']
        create_start_menu_shortcut(unzip_dir, file_name, shortcut_name)

    if changes_environment:
        print(f'{Fore.GREEN}\nRefreshing Environment Variables{Fore.RESET}')
        os.system(rf'{home}\Desktop\Electric\Electric-Windows\src\scripts\refreshvars.cmd')


# with open('zip-test.json', 'r') as f:
#     data = json.load(f)

# install(data, Metadata(None, None, None, None, None, None, None, None, None, None, None))
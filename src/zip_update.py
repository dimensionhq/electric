from Classes.Metadata import Metadata
from Classes.PortablePacket import PortablePacket
from extension import write
from colorama import Fore
from zip_utils import *
import os
import sys

home = os.path.expanduser('~')


def update_portable(ctx, packet: PortablePacket, metadata: Metadata):
    
    write(f'Updating [ {Fore.LIGHTCYAN_EX}{packet.display_name}{Fore.RESET} ]', 'white', metadata)
    
    install_directory = rf'{home}\{packet.json_name}@{packet.latest_version}\\'
    if packet.chdir:
        install_directory += packet.chdir + '\\'
    
    print(install_directory)
    write(f'Successfully Updated {packet.display_name}', 'magenta', metadata)
    sys.exit()
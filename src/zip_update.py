from Classes.Metadata import Metadata
from Classes.PortablePacket import PortablePacket
from extension import write
from colorama import Fore
from zip_utils import *
import os

home = os.path.expanduser('~')


def update_portable(packet: PortablePacket, metadata: Metadata):
    
    write(f'Updating [ {Fore.LIGHTCYAN_EX}{packet.display_name}{Fore.RESET} ]', 'white', metadata)
    
    write(f'Successfully Updated {packet.display_name}', 'magenta', metadata)
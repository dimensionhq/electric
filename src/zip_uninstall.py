from Classes.PortablePacket import PortablePacket
from extension import write
from zip_utils import delete_start_menu_shortcut, find_existing_installation
from Classes.Metadata import Metadata
from subprocess import Popen, PIPE
import os

home = os.path.expanduser('~')

def uninstall_portable(packet: PortablePacket, metadata: Metadata):
    if find_existing_installation(f'{packet.extract_dir}@{packet.latest_version}'):
        
        loc = rf'{home}\electric\\'

        write(f'Deleting Shims For {packet.display_name}', 'cyan', metadata)
        if packet.bin:
            for sh in packet.bin:
                shim_name = sh.split('\\')[-1].replace('.exe', '').replace('.ps1', '').replace('.cmd', '').replace('.bat', '')
                try:
                    os.remove(loc + '\\' + shim_name + '.bat')
                except FileNotFoundError:
                    pass

        write(f'Deleting Shortcuts For {packet.display_name}', 'cyan', metadata)
        shortcuts = packet.shortcuts
        if shortcuts:
            for shortcut in shortcuts:
                try:
                    delete_start_menu_shortcut(shortcut['shortcut-name'])
                except FileNotFoundError:
                    pass
        
        write(f'Uninstalling {packet.display_name}', 'green', metadata)
        package_directory = loc + f'{packet.extract_dir}@{packet.latest_version}'
        proc = Popen(f'del /f/s/q {package_directory} > nul'.split(), stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
        proc.communicate()
        proc = Popen(f'rmdir /s/q {package_directory}'.split(), stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
        proc.communicate()
        loc = rf'{home}\electric\shims'
        
        write(f'Successfully Uninstalled {packet.display_name}', 'green', metadata)
    else:
        write(f'Could Not Find Any Existing Installations Of {packet.display_name}', 'yellow', metadata)
from Classes.PortablePacket import PortablePacket
from extension import write
from zip_utils import delete_environment_variable, delete_start_menu_shortcut, find_existing_installation, display_notes, uninstall_dependencies
from Classes.Metadata import Metadata
from subprocess import Popen, PIPE
import os

home = os.path.expanduser('~')

def uninstall_portable(packet: PortablePacket, metadata: Metadata):
    if find_existing_installation(f'{packet.extract_dir}@{packet.latest_version}'):

        loc = rf'{home}\electric\\'

        if packet.dependencies:
            uninstall_dependencies(packet, metadata)

        if packet.bin:
            write(f'Deleting Shims For {packet.display_name}', 'cyan', metadata)
            for sh in packet.bin:
                shim_name = sh.split('\\')[-1].replace('.exe', '').replace('.ps1', '').replace('.cmd', '').replace('.bat', '')
                try:
                    os.remove(loc + 'shims\\' + shim_name + '.bat')
                except FileNotFoundError:
                    pass

        shortcuts = packet.shortcuts

        if shortcuts:
            write(f'Deleting Shortcuts For {packet.display_name}', 'cyan', metadata)
            for shortcut in shortcuts:
                try:
                    delete_start_menu_shortcut(shortcut['shortcut-name'])
                except FileNotFoundError:
                    pass
        
        if packet.set_env:
            write(f'Deleting {packet.set_env["name"]} Environment Variable', 'bright_green', metadata)
            delete_environment_variable(packet.set_env['name'])
        
        write(f'Uninstalling {packet.display_name}', 'bright_green', metadata)
        package_directory = loc + f'{packet.extract_dir}@{packet.latest_version}'
        proc = Popen(f'del /f/s/q {package_directory} > nul'.split(), stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
        proc.communicate()
        proc = Popen(f'rmdir /s/q {package_directory}'.split(), stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
        proc.communicate()
        loc = rf'{home}\electric\shims'
                
        write(f'Successfully Uninstalled {packet.display_name}', 'bright_green', metadata)
        if packet.uninstall_notes:
            display_notes(packet, '', metadata, uninstall=True)

    else:
        write(f'Could Not Find Any Existing Installations Of {packet.display_name}', 'bright_yellow', metadata)

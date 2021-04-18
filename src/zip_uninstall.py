from Classes.PortablePacket import PortablePacket
from extension import write
from zip_utils import delete_environment_variable, delete_start_menu_shortcut, find_existing_installation, display_notes, uninstall_dependencies
from Classes.Metadata import Metadata
from subprocess import Popen, PIPE
from logger import log_info
import os

home = os.path.expanduser('~')

def uninstall_portable(packet: PortablePacket, metadata: Metadata):
    if find_existing_installation(f'{packet.extract_dir}@{packet.latest_version}'):

        loc = rf'{home}\electric\\'

        if packet.dependencies:
            log_info(f'Uninstalling dependencies for {packet.display_name}', metadata.logfile)
            uninstall_dependencies(packet, metadata)

        if packet.bin:
            log_info(rf'Deleting shims for {packet.display_name} from {loc}\shims', metadata.logfile)
            write(f'Deleting Shims For {packet.display_name}', 'cyan', metadata)
            for sh in packet.bin:
                if isinstance(sh, str):
                    shim_name = sh.split('\\')[-1].split('.')[0]
                    try:
                        os.remove(loc + 'shims\\' + shim_name + '.bat')
                    except FileNotFoundError:
                        pass
                else:
                    shim_name = sh['shim-name'].split('\\')[-1].split('.')[0]
                    try:
                        os.remove(loc + 'shims\\' + shim_name + '.bat')
                    except FileNotFoundError:
                        pass

        shortcuts = packet.shortcuts

        if shortcuts:
            log_info(f'Deleting shortcuts for {packet.display_name}', metadata.logfile)
            write(f'Deleting Shortcuts For {packet.display_name}', 'cyan', metadata)
            for shortcut in shortcuts:
                try:
                    delete_start_menu_shortcut(shortcut['shortcut-name'])
                except FileNotFoundError:
                    pass
        
        if packet.set_env:
            write(f'Deleting {packet.set_env["name"]} Environment Variable', 'bright_green', metadata)
            delete_environment_variable(packet.set_env['name'])
        
        log_info(f'Deleting folders related to {packet.display_name}@{packet.latest_version}', metadata.logfile)
        write(f'Uninstalling {packet.display_name}', 'bright_green', metadata)
        package_directory = loc + f'{packet.extract_dir}@{packet.latest_version}'

        proc = Popen(f'del /f/s/q {package_directory} > nul'.split(), stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
        proc.communicate()

        proc = Popen(f'rmdir /s/q {package_directory}'.split(), stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
        proc.communicate()
        loc = rf'{home}\electric\shims'

        if packet.set_env:
            if isinstance(packet.set_env, list):
                changes_environment = True
                for obj in packet.set_env:
                    log_info(f'Setting environment variables for {packet.display_name}', metadata.logfile)
                    write(
                        f'Setting Environment Variable {obj["name"]}', 'bright_green', metadata)
                    delete_environment_variable(obj['name'])

            else:
                log_info(f'Removing environment variables for {packet.display_name}', metadata.logfile)
                write(
                    f'Deleting Environment Variable {packet.set_env["name"]}', 'bright_green', metadata)
                delete_environment_variable(packet.set_env["name"])

        if packet.uninstall_notes:
            display_notes(packet, '', metadata, uninstall=True)

        write(f'Successfully Uninstalled {packet.display_name}', 'bright_magenta', metadata)
    else:
        write(f'Could Not Find Any Existing Installations Of {packet.display_name}', 'bright_yellow', metadata)

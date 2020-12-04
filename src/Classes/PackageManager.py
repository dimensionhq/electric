######################################################################
#                           PACKAGE MANAGER                          #
######################################################################


from logger import log_info, closeLog
from Classes.Download import Download
from Classes.Install import Install
from multiprocessing import Process
from subprocess import PIPE
from threading import Thread
from colorama import Back
from extension import *
from utils import *
from time import *
import subprocess
import tempfile
import requests
import zipfile
import cursor
import click
import sys
import os


paths = {}


class PackageManager:

    def __init__(self, packets, metadata):
        self.packets = packets
        self.metadata = metadata

    def download(self, download: Download):
        cursor.hide()
        if not os.path.isdir(Rf'{tempfile.gettempdir()}\electric'):
            os.mkdir(Rf'{tempfile.gettempdir()}\electric')

        path = Rf'{tempfile.gettempdir()}\electric\{download.name}{download.extension}'

        with open(path, 'wb') as f:
            response = requests.get(download.url, stream=True)
            total_length = response.headers.get('content-length')
            if total_length is None:
                f.write(response.content)
            else:
                dl = 0
                full_length = int(total_length)

                for data in response.iter_content(chunk_size=4096):
                    dl += len(data)
                    f.write(data)

                    complete = int(20 * dl / full_length)
                    fill_c, unfill_c = '#' * complete, ' ' * (20 - complete)
                    try:
                        sys.stdout.write(
                            f"\r[{fill_c}{unfill_c}] ⚡ {round(dl / full_length * 100, 1)} % ⚡ {round(dl / 1000000, 1)} / {round(full_length / 1000000, 1)} MB")
                    except UnicodeEncodeError:
                        pass
                    sys.stdout.flush()

        paths.update({download.display_name: {'path': path,
                                              'display_name': download.display_name}})
        cursor.show()

    def install_package(self, install: Install) -> str:
        path = install.path
        switches = install.install_switches
        download_type = install.download_type
        custom_install_switch = install.custom_install_switch
        directory = install.directory


        if download_type == '.exe':
            if '.exe' not in path:
                if not os.path.isfile(path + '.exe'):
                    os.rename(path, f'{path}.exe')
                path = path + '.exe'
            command = path + ' '

            for switch in switches:
                command = command + ' ' + switch

            if custom_install_switch and directory:
                if '/D=' in custom_install_switch:
                    command += ' ' + custom_install_switch + f'{directory}'
                else:
                    command += ' ' + custom_install_switch + f'"{directory}"'
                if directory == '':
                    click.echo(click.style(
                        f'Installing {install.display_name} To Default Location, Custom Installation Directory Not Supported By This Installer!', fg='yellow'))

            run_cmd(command, self.metadata, 'installation', install.display_name)

        elif download_type == '.msi':
            command = 'msiexec.exe /i' + path + ' '
            for switch in switches:
                command = command + ' ' + switch

            run_cmd(command, self.metadata, 'installation', install.display_name)

        elif download_type == '.zip':
            if not self.metadata.no_color:
                click.echo(click.style(
                    f'Unzipping File At {path}', fg='green'))
            if self.metadata.no_color:
                click.echo(click.style(
                    f'Unzipping File At {path}'))

            zip_directory = fR'{tempfile.gettempdir()}\\{self.metadata.display_name}'
            with zipfile.ZipFile(path, 'r') as zip_ref:
                zip_ref.extractall(zip_directory)
            executable_list = []
            for name in os.listdir(zip_directory):
                if name.endswith('.exe'):
                    executable_list.append(name)
            executable_list.append('Exit')

            file_path = fR'{tempfile.gettempdir()}\\{self.metadata.display_name}'

            def trigger():
                click.clear()
                for executable in executable_list:
                    if executable == executable_list[index]:
                        print(Back.CYAN + executable + Back.RESET)
                    else:
                        print(executable)

            trigger()

            def up():
                global index
                if len(executable_list) != 1:
                    index -= 1
                    if index >= len(executable_list):
                        index = 0
                        trigger()
                        return
                    trigger()

            def down():
                global index
                if len(executable_list) != 1:
                    index += 1
                    if index >= len(executable_list):
                        index = 0
                        trigger()
                        return
                    trigger()

            def enter():
                if executable_list[index] == 'Exit':
                    os._exit(0)

                else:
                    path = file_path + "\\" + executable_list[index]
                    click.echo(click.style(
                        f'Running {executable_list[index]}. Hit Control + C to Quit', fg='magenta'))
                    subprocess.call(path, stdout=PIPE,
                                    stdin=PIPE, stderr=PIPE)
                    quit()

            keyboard.add_hotkey('up', up)
            keyboard.add_hotkey('down', down)
            keyboard.add_hotkey('enter', enter)
            keyboard.wait()

    def calculate_spwn(self, number: int) -> str:
        if number <= 3:
            return 'threading'
        return 'processing'

    def handle_dependencies(self):
        for packet in self.packets:
            if packet.dependencies:
                install_dependent_packages(packet, self.metadata.rate_limit, packet.directory, self.metadata)

    def handle_multi_download(self) -> list:

        self.handle_dependencies()
        metadata = self.metadata

        write(
            f'Successfully Transferred Electrons', 'cyan', metadata)
        log_info(f'Electrons Successfully Transferred', metadata.logfile)

        write('Initializing Rapid Download...', 'green', metadata)
        log_info('Initializing Rapid Download...', metadata.logfile)

        packets = self.packets

        download_items = []
        if len(packets) > 1:
            idx = 0
            for packet in packets:
                download_items.append(Download(packet.win64, packet.win64_type,
                                               f'Setup{idx}', packet.display_name, f"{tempfile.gettempdir()}\\Setup{idx}{packet.win64_type}"))
                idx += 1
        elif len(packets) == 1:
            download_items.append(Download(packets[0].win64, packets[0].win64_type, 'Setup0',
                                           packets[0].display_name, f"{tempfile.gettempdir()}\\Setup0{packets[0].win64_type}"))

        for item in download_items:
            write_verbose(f'Sending request to {item.url} for downloading {item.display_name}', self.metadata)
            write_debug(f'Downloading {item.display_name} from {item.url} into {item.name}{item.extension}', self.metadata)

        method = self.calculate_spwn(len(packets))

        if method == 'threading':
            threads = []

            for item in download_items:
                threads.append(Thread(target=self.download, args=(item,)))

            for thread in threads:
                thread.start()

            for x in threads:
                x.join()

        if method == 'processing':
            processes = []

            for item in download_items:
                processes.append(Process(target=self.download, args=(item,)))

            for process in processes:
                process.start()

            for x in processes:
                x.join()

        for item in download_items:
            if self.metadata.virus_check:
                write(
                    f'\nScanning {item.display_name} For Viruses...', 'blue', metadata)
                check_virus(item.path, metadata)

        write_debug(f'Rapid Download Successfully Downloaded {len(download_items)} Packages Using RapidThreading', metadata)
        write_debug('Rapid Download Exiting With Code 0', metadata)
        if not self.metadata.debug:
            write('\nFinished Rapid Download...', 'green', metadata)
        else:
            write('Finished Rapid Download...', 'green', metadata)
        log_info('Finished Rapid Download', metadata.logfile)
        write(
            'Using Rapid Install, Accept Prompts Asking For Admin Permission...', 'cyan', metadata)
        log_info(
            'Using Rapid Install To Complete Setup, Accept Prompts Asking For Admin Permission...', metadata.logfile)
        return paths

    def generate_installers(self, paths) -> list:
        install_items = []

        packets = self.packets

        install_items = []

        if len(packets) > 1:
            for pack in packets:
                for path in paths.items():
                    if pack.display_name == path[1]['display_name']:
                        install_items.append(Install(
                            pack.display_name, path[1]['path'], pack.install_switches, pack.win64_type, pack.directory, pack.custom_location, self.metadata))
        else:
            return Install(packets[0].display_name, paths[0][1]['display_name'], packets[0].install_switche, packets[0].win64_type, packets[0].directory, packets[0].custom_location, self.metadata)

        return self.generate_split(install_items)

    def generate_split(self, install_items) -> list:
        exe_list = []
        msi_list = []
        other_list = []

        for item in install_items:
            if item.download_type == '.exe':
                exe_list.append(item)
            elif item.download_type == '.msi':
                msi_list.append(item)
            else:
                other_list.append(item)
        install_items = [exe_list, msi_list, other_list]
        return install_items

    def handle_multi_install(self, paths):
        write_debug('Initialising Rapid Install Procedure...', self.metadata)

        processes = []

        install_items = self.generate_installers(paths)

        idx = 0
        for item in install_items:

            is_msi = False
            try:
                item[1]
                is_msi = True
            except IndexError:
                is_msi = False

            try:
                item[idx]
                is_msi = True
            except IndexError:
                is_msi = False

            if is_msi:
                if item[idx] == item[1]:
                    for val in item:
                        self.install_package(val)

            if item:
                for val in item:
                    write_debug(f'Running Installer For <{val.display_name}> On Thread {item.index(val)}', self.metadata)
                    processes.append(
                        Process(target=self.install_package, args=(val,)))
                for process in processes:
                    process.start()
                for x in processes:
                    x.join()
                processes.clear()
            idx += 1

        if self.metadata.reduce_package:
            for path in paths:
                os.remove(path)
            write('Successfully Cleaned Up Installer From Temp Directory...',
                  'green', self.metadata)

        write(
            'Successfully Installed Packages!', 'bright_magenta', self.metadata)
        log_info('Successfully Installed Packages!', self.metadata.logfile)

        log_info('Refreshing Environment Variables', self.metadata.logfile)
        write_debug(
            'Refreshing Env Variables, Calling Batch Script', self.metadata)
        write_verbose('Refreshing Environment Variables', self.metadata)
        start = timer()
        refresh_environment_variables()
        end = timer()
        write_debug(f'Successfully Refreshed Environment Variabled in {round((end - start), 2)} seconds', self.metadata)
        write_verbose('Installation and setup completed.', self.metadata)
        log_info('Installation and setup completed.', self.metadata.logfile)
        write_debug(
            f'Terminated debugger at {strftime("%H:%M:%S")} on install::completion', self.metadata)
        log_info(
            f'Terminated debugger at {strftime("%H:%M:%S")} on install::completion', self.metadata.logfile)

        if self.metadata.logfile:
            closeLog(self.metadata.logfile, 'Install')

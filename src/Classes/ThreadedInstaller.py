######################################################################
#                           PACKAGE MANAGER                          #
######################################################################


from time import strftime
from timeit import default_timer as timer
from urllib.request import urlretrieve
from logger import log_info, close_log
from Classes.Download import Download
from Classes.Install import Install
from Classes.Packet import Packet
from extension import *
import multiprocessing
from colorama import Fore
import tempfile
import requests
import cursor
import click
import sys
import os
import utils
from zip_utils import set_environment_variable, confirm

paths = {}


class ThreadedInstaller:
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
                    fill_c, unfill_c = '█' * complete, ' ' * (20 - complete)
                    try:
                        sys.stdout.write(
                            f"\r({fill_c}{unfill_c}) {round(dl / full_length * 100)} % ")
                    except UnicodeEncodeError:
                        pass
                    sys.stdout.flush()
        paths.update({
            download.display_name:
                {
                    'path': path,
                    'display_name': download.display_name
                }
        })
        sys.stdout.write('')
        # cursor.show()

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

            if custom_install_switch == 'None' and install.directory:
                click.echo(click.style(
                    f'Installing {install.display_name} To Default Location, Custom Installation Directory Not Supported By This Installer!', fg='bright_yellow'))

            utils.run_cmd(command, self.metadata, 'installation', install)

        elif download_type == '.msi':
            command = 'msiexec.exe /i' + path + ' '
            for switch in switches:
                command = command + ' ' + switch

            utils.run_cmd(command, self.metadata, 'installation', install)

    def calculate_spwn(self, number: int) -> str:
        if number <= 3:
            return 'threading'
        return 'processing'

    def handle_dependencies(self):
        for packet in self.packets:
            if packet.dependencies:
                ThreadedInstaller.install_dependent_packages(
                    packet, self.metadata.rate_limit, packet.directory, self.metadata)

    def handle_multi_download(self) -> list:
        from threading import Thread

        self.handle_dependencies()
        metadata = self.metadata
        package_list = [packet.display_name for packet in self.packets]
        package_list = str(package_list).replace(
            '[', '').replace(']', '').replace('\'', '')
        write(
            f'SuperCached [ {Fore.LIGHTCYAN_EX}{package_list}{Fore.RESET} ]', 'white', metadata)
        log_info('Initializing Rapid Download', metadata.logfile)

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
            write_verbose(
                f'Sending request to {item.url} for downloading {item.display_name}', self.metadata)
            write_debug(
                f'Downloading {item.display_name} from {item.url} into {item.name}{item.extension}', self.metadata)

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
                processes.append(multiprocessing.Process(
                    target=self.download, args=(item,)))

            for process in processes:
                process.start()

            for x in processes:
                x.join()

        for item in download_items:
            if self.metadata.virus_check:
                write(
                    f'\nScanning {item.display_name} For Viruses...', 'bright_cyan', metadata)
                utils.check_virus(item.path, metadata)

        write_debug(
            f'Rapid Download Successfully Downloaded {len(download_items)} Packages Using RapidThreading', metadata)
        write_debug('Rapid Download Exiting With Code 0', metadata)
        if not self.metadata.debug:
            write('\nSuccessfully Downloaded Installation Files',
                  'bright_green', metadata)
        else:
            write('Successfully Downloaded Installation Files',
                  'bright_green', metadata)
        log_info('Finished Rapid Download', metadata.logfile)
        write(
            'Installing Packages', 'cyan', metadata)
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
                        install_items.append(
                            Install(
                                pack.json_name,
                                pack.display_name, path[1]['path'], pack.install_switches, pack.win64_type, pack.directory, pack.custom_location, pack.install_exit_codes, pack.uninstall_exit_codes, self.metadata, pack.version))
        else:
            return Install(packets[0].json_name, packets[0].display_name, paths[0][1]['display_name'], packets[0].install_switches, packets[0].win64_type, packets[0].directory, packets[0].custom_location, packets[0].install_exit_codes, packets[0].uninstall_exit_codes, self.metadata, packets[0].version)

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

        install_items = [{'exe': exe_list}, {
            'msi': msi_list}, {'other': other_list}]
        return install_items

    def handle_multi_install(self, paths):
        write_debug('Initialising Rapid Install Procedure...', self.metadata)

        processes = []

        install_items = self.generate_installers(paths)

        idx = 0

        for item in install_items:
            if 'msi' in list(item.keys()):
                for val in item['msi']:
                    self.install_package(val)
                continue

            else:
                string = ''
                if 'other' in list(item.keys()):
                    string = 'other'
                else:
                    string = 'exe'
                for val in item[string]:
                    write_debug(
                        f'Running Installer For <{val.display_name}> On Thread {item[string].index(val)}', self.metadata)
                    processes.append(
                        multiprocessing.Process(
                            target=self.install_package, args=(val,))
                    )

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
                  'bright_green', self.metadata)

        for packet in self.packets:
            utils.register_package_success(
                packet, packet.directory, self.metadata)

        write(
            'Successfully Installed Packages!', 'bright_magenta', self.metadata)
        log_info('Successfully Installed Packages!', self.metadata.logfile)
        log_info('Refreshing Environment Variables', self.metadata.logfile)
        write_debug(
            'Refreshing Env Variables, Calling Batch Script', self.metadata)
        write_verbose('Refreshing Environment Variables', self.metadata)
        start = timer()
        write('The PATH environment variable has changed. Run `refreshenv` to refresh your environment variables.', 'green', self.metadata)
        end = timer()
        write_debug(
            f'Successfully Refreshed Environment Variables in {round((end - start), 2)} seconds', self.metadata)
        write_verbose('Installation and setup completed.', self.metadata)
        log_info('Installation and setup completed.', self.metadata.logfile)
        write_debug(
            f'Terminated debugger at {strftime("%H:%M:%S")} on install::completion', self.metadata)
        log_info(
            f'Terminated debugger at {strftime("%H:%M:%S")} on install::completion', self.metadata.logfile)

        if self.metadata.logfile:
            close_log(self.metadata.logfile, 'Install')

    @staticmethod
    def install_dependent_packages(packet: Packet, rate_limit: int, install_directory: str, metadata: Metadata):
        from limit import Limiter, TokenBucket
        from registry import get_environment_keys

        disp = str(packet.dependencies).replace(
            "[", "").replace("]", "").replace("\'", "")
        write(f'{packet.display_name} has the following dependencies: {disp}',
              'bright_yellow', metadata)
        continue_install = confirm(
            'Would you like to install the above dependencies ?')
        if continue_install:
            write(
                f'Installing Dependencies For => {packet.display_name}', 'cyan', metadata)
            if len(packet.dependencies) > 1 and len(packet.dependencies) <= 5:
                write(
                    f'Using Parallel Installation For Installing Dependencies', 'bright_green', metadata)
                packets = []
                for package in packet.dependencies:
                    res = utils.send_req_package(package)
                    pkg = res
                    keys = list(pkg.keys())
                    idx = 0
                    for key in keys:
                        if key not in ['package-name', 'nightly', 'display-name']:
                            idx = keys.index(key)
                            break
                    version = keys[idx]
                    pkg = pkg[version]
                    custom_dir = None
                    if install_directory:
                        custom_dir = install_directory + \
                            f'\\{pkg["package-name"]}'
                    else:
                        custom_dir = install_directory

                    install_exit_codes = None
                    if 'valid-install-exit-codes' in list(pkg.keys()):
                        install_exit_codes = pkg['valid-install-exit-codes']

                    packet = Packet(
                        package,
                        res['package-name'],
                        pkg['url'],
                        pkg['file-type'],
                        pkg['custom-location'],
                        pkg['install-switches'],
                        pkg['uninstall-switches'],
                        custom_dir,
                        pkg['dependencies'],
                        install_exit_codes,
                        None,
                        pkg['set-env'] if 'set-env' in list(
                            pkg.keys()) else None,
                        pkg['default-install-dir'] if 'default-install-dir' in list(
                            pkg.keys()) else None,
                        pkg['uninstall'] if 'uninstall' in list(
                            pkg.keys()) else [],
                        pkg['add-path'] if 'add-path' in list(
                            pkg.keys()) else None,
                        pkg['checksum'] if 'checksum' in list(
                            pkg.keys()) else None,
                        pkg['bin'] if 'bin' in list(pkg.keys()) else None,
                        pkg['pre-update'] if 'pre-update' in list(pkg.keys()) else None,
                    )

                    installation = utils.find_existing_installation(
                        package, packet.json_name)

                    if installation:
                        write_debug(
                            f'Aborting Installation As {packet.json_name} is already installed.', metadata)
                        write_verbose(
                            f'Found an existing installation of => {packet.json_name}', metadata)
                        write(
                            f'Found an existing installation {packet.json_name}.', 'bright_yellow', metadata)
                        installation_continue = confirm(
                            f'Would you like to reinstall {packet.json_name}')
                        if installation_continue or metadata.yes:
                            os.system(f'electric uninstall {packet.json_name}')
                            os.system(f'electric install {packet.json_name}')
                            return
                        else:
                            utils.handle_exit('ERROR', None, metadata)

                    write_verbose(
                        f'Package to be installed: {packet.json_name}', metadata)
                    log_info(
                        f'Package to be installed: {packet.json_name}', metadata.logfile)

                    write_verbose(
                        f'Finding closest match to {packet.json_name}...', metadata)
                    log_info(
                        f'Finding closest match to {packet.json_name}...', metadata.logfile)
                    packets.append(packet)

                    write_verbose(
                        'Generating system download path...', metadata)
                    log_info('Generating system download path...',
                             metadata.logfile)

                manager = ThreadedInstaller(packets, metadata)
                paths = manager.handle_multi_download()
                log_info('Finished Rapid Download...', metadata.logfile)
                log_info(
                    'Using Rapid Install To Complete Setup, Accept Prompts Asking For Admin Permission...', metadata.logfile)
                manager.handle_multi_install(paths)
                return
            else:
                write('Starting Sync Installation', 'bright_green', metadata)
                for package in packet.dependencies:
                    res = utils.send_req_package(package)
                    write(
                        f'SuperCached [ {Fore.LIGHTCYAN_EX}{res["display-name"]}{Fore.RESET} ]', 'white', metadata)
                    pkg = res[res['latest-version']]
                    log_info(
                        'Generating Packet For Further Installation.', metadata.logfile)

                    install_exit_codes = None
                    if 'valid-install-exit-codes' in list(pkg.keys()):
                        install_exit_codes = pkg['valid-install-exit-codes']

                    packet = Packet(
                        res,
                        res['package-name'],
                        res['display-name'],
                        pkg['url'],
                        pkg['file-type'],
                        pkg['custom-location'],
                        pkg['install-switches'],
                        pkg['uninstall-switches'],
                        install_directory,
                        pkg['dependencies'],
                        install_exit_codes,
                        [],
                        None,
                        False,
                        pkg['set-env'] if 'set-env' in list(
                            pkg.keys()) else None,
                        pkg['default-install-dir'] if 'default-install-dir' in list(
                            pkg.keys()) else None,
                        pkg['uninstall'] if 'uninstall' in list(
                            pkg.keys()) else [],
                        pkg['add-path'] if 'add-path' in list(
                            pkg.keys()) else None,
                        pkg['checksum'] if 'checksum' in list(
                            pkg.keys()) else None,
                        pkg['bin'] if 'bin' in list(pkg.keys()) else None,
                        pkg['pre-update'] if 'pre-update' in list(pkg.keys()) else None,
                    )

                    log_info(
                        'Searching for existing installation of package.', metadata.logfile)
                    installation = utils.find_existing_installation(
                        package, packet.json_name)

                    if installation:
                        write_debug(
                            f'Found existing installation of {packet.json_name}.', metadata)
                        write_verbose(
                            f'Found an existing installation of => {packet.json_name}', metadata)
                        write(
                            f'Found an existing installation {packet.json_name}.', 'bright_yellow', metadata)
                        continue

                    if packet.dependencies:
                        ThreadedInstaller.install_dependent_packages(
                            packet, rate_limit, install_directory, metadata)

                    write_verbose(
                        f'Package to be installed: {packet.json_name}', metadata)
                    log_info(
                        f'Package to be installed: {packet.json_name}', metadata.logfile)

                    write_verbose(
                        'Generating system download path...', metadata)
                    log_info('Generating system download path...',
                             metadata.logfile)

                    download_url = packet.win64

                    write('Initializing Rapid Download',
                          'bright_green', metadata)
                    log_info('Initializing Rapid Download...',
                             metadata.logfile)

                    # Downloading The File From Source
                    write_debug(
                        f'Downloading {packet.display_name} from => {packet.win64}', metadata)
                    write_verbose(
                        f"Downloading from '{download_url}'", metadata)
                    log_info(
                        f"Downloading from '{download_url}'", metadata.logfile)

                    if rate_limit == -1:
                        path = utils.download(
                            download_url, packet.json_name, metadata, packet.win64_type)
                    else:
                        log_info(
                            f'Starting rate-limited installation => {rate_limit}', metadata.logfile)
                        bucket = TokenBucket(
                            tokens=10 * rate_limit, fill_rate=rate_limit)

                        limiter = Limiter(
                            bucket=bucket,
                            filename=f'{tempfile.gettempdir()}\Setup{packet.win64_type}',
                        )

                        urlretrieve(
                            url=download_url,
                            filename=f'{tempfile.gettempdir()}\Setup{packet.win64_type}',
                            reporthook=limiter
                        )

                        path = f'{tempfile.gettempdir()}\Setup{packet.win64_type}'

                    write('Completed Rapid Download', 'bright_green', metadata)

                    log_info('Finished Rapid Download', metadata.logfile)

                    if metadata.virus_check:
                        write('Scanning File For Viruses...',
                              'bright_cyan', metadata)
                        utils.check_virus(path, metadata)

                    write(
                        'Using Rapid Install, Accept Prompts Asking For Admin Permission...', 'cyan', metadata)
                    log_info(
                        'Using Rapid Install To Complete Setup, Accept Prompts Asking For Admin Permission...', metadata.logfile)

                    write_debug(
                        f'Installing {packet.json_name} through Setup{packet.win64_type}', metadata)
                    log_info(
                        f'Installing {packet.json_name} through Setup{packet.win64_type}', metadata.logfile)
                    start_snap = get_environment_keys()

                    # Running The Installer silently And Completing Setup
                    utils.install_package(path, packet, metadata)

                    changes_environment = False
                    if packet.shim:
                        changes_environment = True
                        for shim in packet.shim:
                            replace_install_dir = ''

                        if packet.directory:
                            replace_install_dir = packet.directory

                        elif packet.default_install_dir:
                            replace_install_dir = packet.default_install_dir

                        shim = shim.replace(
                            '<install-directory>', replace_install_dir)
                        shim_name = shim.split("\\")[-1].split('.')[0]
                        write(
                            f'Generating Shim For {shim_name}', 'cyan', metadata)
                        utils.generate_shim(
                            shim, shim_name, shim.split('.')[-1])

                    if packet.add_path:

                        replace_install_dir = ''

                        if packet.directory:
                            replace_install_dir = packet.directory

                        elif packet.default_install_dir:
                            replace_install_dir = packet.default_install_dir

                        write(
                            f'Appending "{packet.add_path.replace("<install-directory>", replace_install_dir)}" To PATH', 'bright_green', metadata)
                        utils.append_to_path(packet.add_path.replace(
                            '<install-directory>', replace_install_dir))

                    if packet.set_env:
                        name = packet.set_env['name']
                        replace_install_dir = ''

                        if packet.directory:
                            replace_install_dir = packet.directory

                        elif packet.default_install_dir:
                            replace_install_dir = packet.default_install_dir

                        write(
                            f'Setting Environment Variable {name}', 'bright_green', metadata)

                        set_environment_variable(
                            name, packet.set_env['value'].replace('<install-directory>', replace_install_dir))

                    final_snap = get_environment_keys()
                    if final_snap.env_length > start_snap.env_length or final_snap.sys_length > start_snap.sys_length or changes_environment:
                        write('The PATH environment variable has changed. Run `refreshenv` to refresh your environment variables.',
                              'bright_green', metadata)

                    write(
                        f'Successfully Installed {packet.display_name}!', 'bright_magenta', metadata)
                    log_info(
                        f'Successfully Installed {packet.display_name}!', metadata.logfile)
                    utils.register_package_success(
                        packet, install_directory, metadata)

                    if metadata.reduce_package:

                        os.remove(path)
                        try:
                            os.remove(
                                Rf'{tempfile.gettempdir()}\downloadcache.pickle')
                        except:
                            pass

                        log_info(
                            'Successfully Cleaned Up Installer From Temporary Directory And DownloadCache', metadata.logfile)
                        write('Successfully Cleaned Up Installer From Temp Directory...',
                              'bright_green', metadata)

                    write_verbose(
                        'Dependency successfully Installed.', metadata)
                    log_info('Dependency successfully Installed.',
                             metadata.logfile)
        else:
            os._exit(1)

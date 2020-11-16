######################################################################
#                               INSTALL                              #
######################################################################


class Install:
    def __init__(self, display_name, path, install_switches, download_type, directory, custom_install_switch, metadata):
        self.display_name = display_name
        self.path = path
        self.install_switches = install_switches
        self.download_type = download_type
        self.directory = directory
        self.custom_install_switch = custom_install_switch
        self.metadata = metadata

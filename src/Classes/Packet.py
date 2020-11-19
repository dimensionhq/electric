######################################################################
#                               PACKET                               #
######################################################################

class Packet:
    def __init__(self, json_name, display_name, win64, darwin, debian, win64_type, darwin_type, debian_type, custom_location, install_switches, uninstall_switches, directory):
        self.json_name = json_name
        self.display_name = display_name
        self.win64 = win64
        self.darwin = darwin
        self.debian = debian
        self.win64_type = win64_type
        self.darwin_type = darwin_type
        self.debian_type = debian_type
        self.custom_location = custom_location
        self.install_switches = install_switches
        self.uninstall_switches = uninstall_switches
        self.directory = directory
        
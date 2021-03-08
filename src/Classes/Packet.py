######################################################################
#                               PACKET                               #
######################################################################

class Packet:
    """
    Used to store data related to the package being installed
    """

    def __init__(self, raw, json_name, display_name, win64, win64_type, custom_location, install_switches, uninstall_switches, directory, dependencies, install_exit_codes, uninstall_exit_codes, version, run_test, set_env, default_install_dir):
        self.raw = raw
        self.json_name = json_name
        self.display_name = display_name
        self.win64 = win64
        self.win64_type = win64_type
        self.custom_location = custom_location
        self.install_switches = install_switches
        self.uninstall_switches = uninstall_switches
        self.directory = directory
        self.dependencies = dependencies
        self.install_exit_codes = install_exit_codes if install_exit_codes != None else []
        self.uninstall_exit_codes = uninstall_exit_codes if uninstall_exit_codes != None else []
        self.version = version
        self.run_test = run_test
        self.set_env = set_env
        self.default_install_dir = default_install_dir

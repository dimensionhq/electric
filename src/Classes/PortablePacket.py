class PortablePacket:
    """
    Similar to the packet class but used for --portable installations
    """    
    def __init__(self, data):
        self.display_name = data['display-name']
        self.json_name = data['package-name']
        self.latest_version = data['latest-version']
        self.url = data['url']
        self.file_type = data['file-type']
        self.extract_dir = data['extract-dir']

        try:
            self.chdir = data['chdir']
        except:
            self.chdir = None
        try:
            self.bin = data['bin']
        except:
            self.bin = None
        try:
            self.shortcuts = data['shortcuts']
        except:
            self.shortcuts = None
        try:
            self.pre_install = data['pre-install']
        except:
            self.pre_install = None
        try:
            self.post_install = data['post-install']
        except:
            self.post_install = None
        try:
            self.install_notes = data['install-notes']
        except:
            self.install_notes = None
        try:
            self.uninstall_notes = data['uninstall-notes']
        except:
            self.uninstall_notes = None
        try:
            self.persist = data['persist']
        except:
            self.presist = None
        try:
            self.set_env = data['set-env']
        except:
            self.set_env = None
        try:
            self.dependencies = data['dependencies']
        except:
            self.dependencies = None

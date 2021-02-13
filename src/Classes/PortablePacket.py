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
            self.post_install = data['post-install']
        except:
            self.post_install = None
        try:
            self.notes = data['notes']
        except:
            self.notes = None

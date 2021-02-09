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
        self.chdir = data['chdir']
        self.bin = data['bin']
        self.shortcuts = data['shortcuts']
        self.post_install = data['post-install']
        self.notes = data['notes']
        

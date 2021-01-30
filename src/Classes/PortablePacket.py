class PortablePacket:
    def __init__(self, data):

        self.display_name = data['display-name']
        self.json_name = data['package-name']
        self.latest_version = data['latest-version']
        self.url = data['url']
        self.file_type = data['file-type']
        self.extract_dir = data['extract-dir']
        try:
            self.chdir = data['chdir']
        except KeyError:
            self.chdir = None
        try:
            self.bin = data['bin']
        except KeyError:
            self.bin = None
        try:
            self.shortcuts = data['shortcuts']
        except KeyError:
            self.shortcuts = None

class PortablePacket:
    def __init__(self, data):

        self.display_name = data['display-name']
        self.json_name = data['package-name']
        self.latest_version = data['latest-version']
        self.url = data[data['latest-version']]['url']
        self.file_type = data[data['latest-version']]['file-type']
        self.extract_dir = data[data['latest-version']]['extract-dir']
        try:
            self.chdir = data[data['latest-version']]['chdir']
        except KeyError:
            self.chdir = None
        try:
            self.bin = data[data['latest-version']]['bin']
        except KeyError:
            self.bin = None
        try:
            self.shortcuts = data[data['latest-version']]['shortcuts']
        except KeyError:
            self.shortcuts = None

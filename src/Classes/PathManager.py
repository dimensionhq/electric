######################################################################
#                            PATH MANAGER                            #
######################################################################


import os

class PathManager:
    @staticmethod
    def get_parent_directory() -> str:
        directory = os.path.dirname(os.path.abspath(__file__))
        return directory.replace('Classes', '').replace('src', '')[:-1].replace(R'\bin', '')

    @staticmethod
    def get_current_directory() -> str:
        directory = os.path.dirname(os.path.abspath(__file__))
        return os.path.split(directory)[0]

    @staticmethod
    def get_appdata_directory() -> str:
        return os.environ['APPDATA'] + R'\electric'
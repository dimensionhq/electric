######################################################################
#                            PATH MANAGER                            #
######################################################################


import os

class PathManager:
    def get_parent_directory(self) -> str:
        directory = os.path.dirname(os.path.abspath(__file__))
        return directory.replace('Classes', '').replace('src', '')[:-1]

    def get_current_directory(self) -> str:
        directory = os.path.dirname(os.path.abspath(__file__))
        return os.path.split(directory)[0]

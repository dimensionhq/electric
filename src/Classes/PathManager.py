import os


class PathManager:
    def get_parent_directory(self) -> str:
        directory = os.path.dirname(os.path.abspath(__file__))
        return os.path.split(directory)[0]

    def get_current_directory(self) -> str:
        directory = os.path.dirname(os.path.abspath(__file__))
        return directory.replace('Classes', '')
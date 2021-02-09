######################################################################
#                            PATH MANAGER                            #
######################################################################

import os

class PathManager:
    """
    Handles path related queries, like the appdata and current directory
    """    
    @staticmethod
    def get_parent_directory() -> str:
        """
        Gets the parent directory of electric (Usually Appdata)

        Returns:
            str: Parent directory
        """        
        directory = os.path.dirname(os.path.abspath(__file__))
        return directory.replace('Classes', '').replace('src', '')[:-1].replace(R'\bin', '')

    @staticmethod
    def get_current_directory() -> str:
        """
        Gets the current directory of electric

        Returns:
            str: Current directory
        """        
        directory = os.path.dirname(os.path.abspath(__file__))
        return os.path.split(directory)[0]

    @staticmethod
    def get_appdata_directory() -> str:
        """
        Gets the path to the Appdata directory

        Returns:
            str: Appdata directory of the user
        """        
        return os.environ['APPDATA'] + R'\electric'

    @staticmethod
    def get_desktop_directory() -> str:
        """
        Gets the path to the user's desktop

        Returns:
            str: The desktop directory of the user
        """        
        return os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')

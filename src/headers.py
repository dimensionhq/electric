######################################################################
#                              CONSTANTS                             #
######################################################################


# from Classes.SystemManager import SystemManager
from time import strftime
import platform
import sys
import os

# Set Of Constants That Can Be Used Throughout The Code

__version__ = '1.0.0a'

def get_architecture():
    """
    Get the cpu architecture of the user's pc 

    Returns:
        architecture(str): The architecture of the user's pc
    """    
    if platform.machine().endswith('64'):
        return 'x64'
    if platform.machine().endswith('86'):
        return 'x32'
    return None


# Install Debug Headers
install_debug_headers = [
    f'Attaching debugger at {strftime("%H:%M:%S")} on install::initialization',
    f'Electric is running on {platform.platform()}',
    f'User machine name: {platform.node()}',
    f'Command line: \"{" ".join(sys.argv)}\"',
    f'Arguments: \"{" ".join(sys.argv[1:])}\"',
    f'Current directory: {os.getcwd()}',
    f'Electric version: {__version__}',
    f'System architecture detected: {get_architecture()}',
    # f'Processor detected: {processor}'
]

# Uninstall Debug Headers
uninstall_debug_headers = [
    f'Attaching debugger at {strftime("%H:%M:%S")} on uninstall::initialization',
    f'Electric is running on {platform.platform()}',
    f'User domain name: {platform.node()}',
    f'Command line: \"{" ".join(sys.argv)}\"',
    f'Arguments: \"{" ".join(sys.argv[1:])}\"',
    f'Current directory: {os.getcwd()}',
    f'Electric version: {__version__}',
    f'System architecture detected: {get_architecture()}'
]


# Valid Installer Exit Codes Which Are Ignored By Electric
valid_install_exit_codes = [
    0,
    1641,
    2359302,
    2149842956
]

# Valid Uninstaller Exit Codes Which Are Ignored By Electric
valid_uninstall_exit_codes = [
    0,
    1605,
    1614,
    1641,
    2359303,
    2149842956
]


# Set of commands that electric can execute (used for autocompletion)
electric_commands = [
    'install',
    'uninstall',
    'bundle',
    'search',
    'new',
    'config',
    'sign',
    'show',
    'find',
    'list'
]


# Set of flags that can be used with `electric install`
install_flags = [
    '--verbose',
    '--debug',
    '--no-progress',
    '--no-color',
    '--log-output',
    '--install-dir',
    '--virus-check',
    '--yes',
    '--silent',
    '--vscode',
    '--python',
    '--node',
    '--sync',
    '--reduce',
    '--rate-limit',
    '--portable'
]

# Set of flags that can be used with `electric uninstall`
uninstall_flags = [
    '--verbose',
    '--debug',
    '--no-color',
    '--log-output',
    '--yes',
    '--silent',
    '--vscode',
    '--python',
    '--node',
    '--no-cache',
    '--portable'
]

# Set of flags that can be used with `electric search`
search_flags = [
    '--starts-with',
    '--exact'
]

# Set of flags that can be used with `electric config`
config_flags = [
    '--remove'
]


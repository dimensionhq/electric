from utils import get_architecture
from time import strftime
import platform
import sys
import os


__version__ = '1.0.0a'

# Install Debug Headers
install_debug_headers = [
    f"Attaching debugger at {strftime('%H:%M:%S')} on install::initialization",
    f"Electric is running on {platform.platform()}",
    f"User machine name: {platform.node()}",
    f"Command line: \"{' '.join(sys.argv)}\"",
    f"Arguments: \"{' '.join(sys.argv[1:])}\"",
    f"Current directory: {os.getcwd()}",
    f"Electric version: {__version__}",
    f"System architecture detected: {get_architecture()}"
]

# Uninstall Debug Headers
uninstall_debug_headers = [
    f"Attaching debugger at {strftime('%H:%M:%S')} on uninstall::initialization",
    f"Electric is running on {platform.platform()}",
    f"User domain name: {platform.node()}",
    f"Command line: \"{' '.join(sys.argv)}\"",
    f"Arguments: \"{' '.join(sys.argv[1:])}\"",
    f"Current directory: {os.getcwd()}",
    f"Electric version: {__version__}",
    f"System architecture detected: {get_architecture()}"
]

from subprocess import call
from urllib.request import urlretrieve
from getpass import getuser
from subprocess import Popen, PIPE
from sys import platform


installed = True
try:
    process = Popen('python', stdout=PIPE, stdin=PIPE, stderr=PIPE)
except FileNotFoundError:
    installed = False


def download_python() -> int:
    # Download Python
    download_path = ''

    if platform == 'win32':
        download_path = f'C:\\Users\\{getuser()}\\Downloads\\PythonSetup.exe'
    elif platform == 'darwin':
        download_path = f'\\Users\\{getuser()}\\Downloads\\PythonSetup.pkg'
    elif platform == 'linux':
        download_path = f'\\home\\{getuser()}\\Downloads\\PythonSetup.deb'

    python_download_url = None

    if platform == 'win32':
        python_download_url = 'https://www.python.org/ftp/python/3.9.0/python-3.9.0-amd64.exe'
    elif platform == 'darwin':
        python_download_url = 'https://www.python.org/ftp/python/3.9.0/python-3.9.0-macosx10.9.pkg'

    urlretrieve(python_download_url, download_path)

    setup_python = []

    if platform == 'win32':
        setup_python = [f'{download_path} /passive']
    elif platform == 'macos':
        setup_python = [
            f'sudo installer -store -pkg "{download_path}" -target /Applications']

    for command in setup_python:
        call(command)

    success = True

    try:
        Popen('python', stdout=PIPE, stdin=PIPE, stderr=PIPE)
    except FileNotFoundError:
        success = False

    return success


def download_dependencies() -> int:
    # Download Dependencies Using Pip
    # Change to turbocharge in the case of TurboCharge
    commands = 'python -m pip install electric'

    for command in commands:
        call(command)
        return 0


if not installed:
    download_python()
    if download_python():
        download_dependencies()


if installed:
    download_dependencies()

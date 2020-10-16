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
        setup_python = [f'sudo installer -store -pkg "{download_path}" -target /Applications']

    for command in setup_python:
        call(command)

    success = True

    try:
        proc = Popen('python', stdout=PIPE, stdin=PIPE, stderr=PIPE)   
    except FileNotFoundError:
        success = False

    return success


def download_dependencies(password) -> int:
    # Download Dependencies Using Pip
    commands = 'python -m pip install electric' # Change to turbocharge in the case of TurboCharge
    
    if platform == 'linux':
        proc = Popen('sudo -S apt-get install python3-pip -y')
        proc.communicate(password.encode())
    for command in commands:
        call(command)
        return 0


if not installed:
    download_python()
    if download_python(): # If already downloaded
        download_dependencies()


if installed:
    download_dependencies()

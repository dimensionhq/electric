from subprocess import call
from urllib.request import urlretrieve
from getpass import getuser
from subprocess import Popen, PIPE


installed = True
try:
    process = Popen('python', stdout=PIPE, stdin=PIPE, stderr=PIPE)
except FileNotFoundError:
    installed = False


def download_python() -> int:
    # Download Python
    download_path = ''
    if platform == 'win32':
        download_path = fR'C:\Users\{getuser()}\Downloads\PythonSetup.exe'
    if platform == 'darwin':
        download_path = fR'/Users/{getuser()}/Downloads/PythonSetup.pkg'
    if platform == 'linux':
        download_path = fR'/home/{getuser()}/Downloads/PythonSetup.deb'

    python_download_url = None
    if platform == 'win32':
        python_download_url = 'https://www.python.org/ftp/python/3.9.0/python-3.9.0-amd64.exe'
    if platform == 'darwin':
        python_download_url = 'https://www.python.org/ftp/python/3.9.0/python-3.9.0-macosx10.9.pkg'

    urlretrieve(python_download_url, download_path)

    setup_python = []
    if platform == 'win32':
        setup_python = [f'{download_path} /passive']
    if platform == 'macos':
        setup_python = [f'sudo installer -store -pkg "{download_path}" -target /Applications']

    for command in setup_python:
        subprocess.call(command)

    working = True
    try:
        proc = Popen('python', stdout=PIPE, stdin=PIPE, stderr=PIPE)
    except FileNotFoundError:
        working = False

    if working:
        return 0
    else:
        return 1


def download_dependencies() -> int:
    # Download Dependencies Using Pip
    commands = 'pip install electric' # Change to turbocharge in the case of turbocharge
    for command in commands:
        subprocess.call(command)
        return 0


if not installed:
    download_python()
    if download_python() == 0:
        download_dependencies()


if installed:
    download_dependencies()

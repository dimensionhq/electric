######################################################################
#                                SETUP                               #
######################################################################


from setuptools import setup, find_packages
from getpass import getuser
from sys import platform
import os

user = getuser()


def run():
    if platform == 'linux':
        os.system(f'echo "export PATH="/home/{user}/.local/bin:$PATH"" >> ~/.bashrc')


run()

setup(
    name = 'electric',
    version = '1.0.0',
    description= 'The Official Package Manager For Windows, MacOS and Linux!',
    url='https://github.com/XtremeDevX/Electric-Windows',
    author = 'XtremeDevX',
    author_email = 'xtremedevx@gmail.com',
    py_modules=['electric'],
    packages=find_packages(),
    scripts=[os.path.join(os.path.abspath(os.getcwd()), 'src', 'electric.py')],
    install_requires = [
        'click',
        'progress',
        'requests',
        'keyboard',
        'colorama',
        'click_didyoumean',
        'virustotal-api',
        'switch',
        'click_didyoumean',
        'click_completion',
        'mslex',
        'halo',
        'cursor',
        'google',
        'prompt-toolkit',
        'py7zr',
        'pywin32',
        'patool',
        'tqdm'
    ],
    package_dir={'': 'src'},
    entry_points =
    '''
        [console_scripts]
        electric=electric:cli
    ''',
    classifiers=[
        "License :: OSI Approved :: Apache License 2.0",
        "Operating System :: OS Independent",
    ]
)

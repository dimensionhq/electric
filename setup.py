######################################################################
#                                SETUP                               #
######################################################################


from setuptools import setup, find_packages
from getpass import getuser
import os
from sys import platform

user = getuser()


def run():
    if platform == 'linux':
        os.system(f'echo "export PATH="/home/{user}/.local/bin:$PATH"" >> ~/.bashrc')


run()

setup(
    name = 'electric',
    version = '1.0.0',
    description= 'The Official Package Manager For Windows, MacOS and Linux!',
    url="https://github.com/TheBossProSniper/Electric",
    author = 'TheBossProSniper',
    author_email = 'thebossprosniper@gmail.com',
    py_modules=['electric'],
    packages=find_packages(),
    scripts=[os.path.join(os.path.abspath(os.getcwd()), 'src', 'electric.py')],
    install_requires = [
        'click',
        'progress',
        'requests',
        'keyboard',
        'colorama',
        'aiothrottle',
        'click_didyoumean',
        'wheel',
        'virustotal-api',
        'switch',
        'click_didyoumean',
        'click_completion',
        'pyperclip'
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

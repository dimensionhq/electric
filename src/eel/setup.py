from setuptools import setup, find_packages
from getpass import getuser
from sys import platform
import os

user = getuser()


def run():
    if platform == 'linux':
        os.system(
            f'echo "export PATH="/home/{user}/.local/bin:$PATH"" >> ~/.bashrc')


run()

setup(
    name='eel',
    version='1.0.0',
    description='The Official electric package manager plugin!',
    url='https://github.com/XtremeDevX/Electric-Windows',
    author='XtremeDevX',
    author_email='xtremedevx@gmail.com',
    py_modules=['eel'],
    packages=find_packages(),
    scripts=[os.path.join(os.path.abspath(os.getcwd()), 'eel.py')],
    install_requires=[
        'click',
        'colorama',
        'moviepy',
        'pydub'
    ],
    entry_points='''
        [console_scripts]
        eel=eel:cli
    ''',
    classifiers=[
        "License :: OSI Approved :: Apache License 2.0",
        "Operating System :: OS Independent",
    ]
)

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
]


tab_completion = '''
Register-ArgumentCompleter -Native -CommandName electric -ScriptBlock {
    param($wordToComplete, $commandAst, $cursorPosition)
        [Console]::InputEncoding = [Console]::OutputEncoding = $OutputEncoding = [System.Text.Utf8Encoding]::new()
        $Local:word = $wordToComplete.Replace('"', '""')
        $Local:ast = $commandAst.ToString().Replace('"', '""')
        electric complete --word="$Local:word" --commandline "$Local:ast" --position $cursorPosition | ForEach-Object {
            [System.Management.Automation.CompletionResult]::new($_, $_, 'ParameterValue', $_)
        }
    }
'''


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
    '--no-cache',
    '--sync',
    '--reduce',
    '--rate-limit',
    '--portable'
]

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

search_flags = [
    '--starts-with',
    '--exact'
]

config_flags = [
    '--remove'
]

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

import click
import json
import difflib

@click.group()
def cli():
    pass

@cli.command()
@click.option('--word', required=True)
@click.option('--commandline', required=True)
@click.option('--position', required=True)
def complete(
    word : str,
    commandline: str,
    position: str,
    ):

    n = len(commandline.split(' '))
    if word:
        possibilities = []
        if n == 2:
            possibilities = electric_commands

        if (
            n > 2
            and not word.startswith('--')
            and (word[0] != '-' or word[1] == '-')
        ):
            with open(rf'{PathManager.get_appdata_directory()}\packages.json', 'r') as f:
                packages = json.load(f)['packages']

            possibilities = difflib.get_close_matches(word, packages)
        elif word.startswith('--') or (word[0] == '-' and word[1] != '-'):
            if word.startswith('--'):
                command = commandline.split(' ')[1]
                if command in ['install', 'bundle', 'i']:
                    possibilities = install_flags
                if command in ['uninstall', 'remove', 'u']:
                    possibilities = uninstall_flags
                if command in ['search', 'find']:
                    possibilities = search_flags
                if command == 'config':
                    possibilities = config_flags
        completion = ''

        for command in possibilities:
            if command.startswith(word):
                completion = command
        click.echo(completion)

    else:

        if n == 1:
            for completion in electric_commands:
                click.echo(completion)

        if n >= 3:
            command = commandline.split(' ')[1]

            if command == 'install':
                for completion in install_flags:
                    click.echo(completion)

            if command == 'uninstall':
                for completion in uninstall_flags:
                    click.echo(completion)

if __name__ == '__main__':
    cli()
from subprocess import *
from sys import platform
import click
import time
import halo


class Config:
    def __init__(self, dictionary):
        self.dictionary = dictionary
        self.publisher = dictionary['Info'][0]['Publisher']
        self.description = dictionary['Info'][1]['Description']
        self.os = dictionary['Info'][2]['OS']
        self.headers = dictionary.keys()

    def check_prerequisites(self):
        dictionary = self.dictionary
        headers = dictionary.keys()
        
        if 'Info' in headers:
           
            click.echo(click.style(f'Publisher => {self.publisher}'))
            click.echo(click.style(f'Description => {self.description}', fg='yellow'))
            
            with halo.Halo('Validating Operating System ', text_color='cyan') as h:
                time.sleep(0.11)
                if platform == 'win32' and not self.os == 'Windows':
                    h.stop()
                    if not click.confirm(f'WARNING: This Config Has A Target OS Of {self.os}. Would you like to continue?'):
                        exit()

        if 'Pip-Packages' in headers:
            with halo.Halo('Testing Pip ', text_color='cyan') as h:
                time.sleep(0.11)
                try:
                    Popen('pip', stdin=PIPE, stdout=PIPE, stderr=PIPE)
                except FileNotFoundError:
                    h.stop()
                    click.echo(click.style('Pip Not Found, Aborting Config Installation!', fg='red'))
                    exit()

        if 'Node-Packages' in headers:
            with halo.Halo('Testing Node ', text_color='cyan') as h:
                time.sleep(0.11)
                try:
                   Popen('npm', stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
                except FileNotFoundError:
                    h.stop()
                    click.echo(click.style('Node Not Found, Aborting Config Installation!', fg='red'))
                    exit()
        
        click.echo(click.style('All Tests Passed!', 'green'))

    @staticmethod
    def generate_configuration(filepath: str):
        d = {}
        with open(f'{filepath}', 'r') as f:
            chunks = f.read().split("[")

            for chunk in chunks:
                chunk = chunk.replace("=>", ":").split('\n')
                header = chunk[0].replace("[", '').replace(']', '').strip()
                d[header] = []

                for line in chunk[1:]:
                    if line and '#' not in line:
                        try:
                            k, v = line.split(":")
                            k, v = k.strip(), v.strip()
                            if v == '':
                                with open(f'{filepath}', 'r') as f:
                                    lines = f.readlines()
                                ln_number = 0
                                idx = 0
                                for val in lines:
                                    if val.strip() == line.replace(':', '=>').strip():
                                        ln_number = idx
                                    idx += 1
                                click.echo(click.style(f'Error On Line {ln_number + 1} At {filepath}', fg='red'))
                                message = line.replace(':', '')
                                click.echo(click.style(f'ValueNotFoundError : No Value Provided For Key :: {colorama.Fore.CYAN}{message}', fg='yellow'))
                                exit()
                        except ValueError:
                            if header in ['Packages', 'Pip-Packages', 'Editor-Extensions']:
                                k, v = line, "latest"           
                            else:
                                with open(f'{filepath}', 'r') as f:
                                    lines = f.readlines()

                                ln_number = 0
                                idx = 0
                                for val in lines:
                                    if val.strip() == line.replace(':', '=>').strip():
                                        ln_number = idx
                                    idx += 1

                                click.echo(click.style(f'Error On Line {ln_number + 1} At {filepath}', fg='red'))
                                message = line.replace(':', '')
                                click.echo(click.style(f'ValueNotFoundError : Expecting A Value Pair With `=>` Operator For Key :: {colorama.Fore.CYAN}{message}', fg='yellow'))
                                exit()

                        d[header].append({ k : v.replace('"', '') })

        d.pop("")

        return Config(d)

    def install():
        pass


filepath = rf"{input('Enter the path to the .electric File => ')}".replace('\"', '')
config = Config.generate_configuration(filepath)
config.check_prerequisites()
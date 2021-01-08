import colorama
import click
import json


publisher, description = '', ''
packages, editor_configuration, editor_extensions, pip_packages = {}, {}, {}, {}

d = {}
with open('test.electric', 'r') as f:
    chunks = f.read().split("\n\n")

    for chunk in chunks:
        chunk = chunk.replace("=>", ":").split('\n')
        header = chunk[0].replace("[", '').replace(']', '').strip()
        d[header] = []

        for line in chunk[1:]:
            if line != '':
                try:
                    k, v = line.split(":")
                    k, v = k.strip(), v.strip()
                    if v == '':
                        raise ValueError()
                except ValueError:
                    if header in ['Packages', 'Pip-Packages', 'Editor-Extensions']:
                        k, v = line, "latest"           
                    else:
                        with open(r'test.electric') as f:
                            lines = f.readlines()

                        ln_number = 0
                        idx = 0
                        for val in lines:
                            if val.strip() == line.strip():
                                ln_number = idx
                            idx += 1

                        click.echo(click.style(f'Error On Line {ln_number + 1} At test.electric', fg='red'))
                        message = line.replace(':', '')
                        click.echo(click.style(f'Expecting A Value Pair With `=>` Operator On Key :: {colorama.Fore.CYAN}{message}', fg='yellow'))
                        exit()

                d[header].append({ k : v.replace('"', '') })

print(json.dumps(d))

import click
import os

def write(text : str, color : str, has_color : bool, quiet : bool):
    if quiet:
        return
    if not has_color:
        if color:
            click.echo(click.style(text, fg=f"{color}"))
        else:
            click.echo(text)
    if has_color:
        if not color:
            click.echo(text)

def write_verbose(log : str, verbose: bool, has_color: bool, quiet : bool):
    if quiet:
        return
    if verbose:
        HEADER = "VERBOSE: "
        if not has_color:
            click.echo(click.style(HEADER + log, fg="green", dim=True))
        else:
            click.echo(click.style(HEADER + log))


def write_debug(log : str, debug: bool, has_color: bool, quiet : bool):
    if quiet:
        return
    if debug:
        if isinstance(log, list):
            log = "\nDEBUG: ".join(log)

        HEADER = "DEBUG: "
        if not has_color:
            click.echo(click.style(HEADER + log, fg="bright_yellow"))
        else:
            click.echo(click.style(HEADER + log))

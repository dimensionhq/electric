import click

from Classes.Metadata import Metadata


def write(text: str, color: str, metadata: Metadata):
    if metadata.silent:
        return
    if not metadata.no_color:
        if color:
            click.echo(click.style(text, fg=f"{color}"))
        else:
            click.echo(text)
    if metadata.no_color:
        if not color:
            click.echo(text)


def write_verbose(log: str, metadata: Metadata):
    if metadata.silent:
        return
    if metadata.verbose:
        HEADER = "VERBOSE: "
        if not metadata.no_color:
            click.echo(click.style(HEADER + log, fg="green", dim=True))
        else:
            click.echo(click.style(HEADER + log))


def write_debug(log: str, metadata: Metadata):
    if metadata.silent:
        return
    if metadata.debug:
        if isinstance(log, list):
            log = "\nDEBUG: ".join(log)

        HEADER = "DEBUG: "
        if not metadata.no_color:
            click.echo(click.style(HEADER + log, fg="bright_yellow"))
        else:
            click.echo(click.style(HEADER + log))

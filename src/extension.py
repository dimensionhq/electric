import click


def write_verbose(log, verbose: bool, color: bool):
    if verbose:
        HEADER = "VERBOSE: "
        if not color:
            click.echo(click.style(HEADER + log, fg="green", dim=True))
        else:
            click.echo(click.style(HEADER + log))


def write_debug(log, debug: bool, color: bool):
    if debug:
        if isinstance(log, list):
            log = "\nDEBUG: ".join(log)

        HEADER = "DEBUG: "
        if not color:
            click.echo(click.style(HEADER + log, fg="bright_yellow"))
        else:
            click.echo(click.style(HEADER + log))


def write(text, color, no_color=False):
    if not no_color:
        if color:
            click.echo(click.style(text, fg=f"{color}"))
        else:
            click.echo(text)
    if no_color:
        if not color:
            click.echo(text)

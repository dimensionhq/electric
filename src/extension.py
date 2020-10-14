import click


def write_verbose(log, verbose: bool):
    if verbose:
        HEADER = "VERBOSE: "
        click.echo(click.style(HEADER + log, fg="green", dim=True))

def write_debug(log, debug: bool):
    if debug:
        if isinstance(log, list):
            log = "\n".join(log)
            
        HEADER = "DEBUG: "
        click.echo(click.style(HEADER + log, fg="bright_yellow"))

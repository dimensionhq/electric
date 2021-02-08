######################################################################
#                                WRITE                               #
######################################################################


from Classes.Metadata import Metadata
import click


def write(text: str, color: str, metadata: Metadata):
    """
    Prints to output keeping in mind metadata properties.

    Args:
        text (str): Text to display to output
        color (str): Text color
        metadata (Metadata): Metadata for the method
    """    
    if metadata.silent:
        return
    if not metadata.no_color:
        if color:
            click.echo(click.style(text, fg=color))
        else:
            click.echo(text)
    if metadata.no_color:
        if not color:
            click.echo(text)


def write_verbose(log: str, metadata: Metadata):
    """
    Write verbose text to the output (used with --verbose). All logs are prefixed with `VERBOSE:`

    Args:
        log (str): Text to write to verbose output
        metadata (Metadata): Metadata for the method
    """    
    if metadata.silent:
        return
    if metadata.verbose:
        HEADER = "VERBOSE: "
        if not metadata.no_color:
            click.echo(click.style(HEADER + log, fg="green", dim=True))
        else:
            click.echo(click.style(HEADER + log))


def write_debug(log: str, metadata: Metadata, newline=False):
    """
    Write debug text to the output (used with --debug). All logs are prefixed with `DEBUG:`
    Args:
        log (str): Text to write to debug output
        metadata (Metadata): Metadata for the method.
        newline (bool, optional): Whether debug has to be logged into a new line. Defaults to False.
    """    
    if metadata.silent:
        return
    if metadata.debug:
        if isinstance(log, list):
            log = "\nDEBUG: ".join(log)
        if not newline:
            HEADER = "DEBUG: "
        else:
            HEADER = "\nDEBUG: "
        if not metadata.no_color:
            click.echo(click.style(HEADER + log, fg="bright_yellow"))
        else:
            click.echo(click.style(HEADER + log))


def write_all(text: str, color: str, metadata: Metadata):
    """
    Writes text to all 3 levels (standard, verbose and debug)

    Args:
        text (str): Text to write to all levels
        color (str): Color of the text used in `write`
        metadata (Metadata): Metadata for the method
    """    
    write(text, color, metadata)
    write_verbose(text, metadata)
    write_debug(text, metadata)

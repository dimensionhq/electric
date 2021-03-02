######################################################################
#                                WRITE                               #
######################################################################


from Classes.Metadata import Metadata
import click


def write(text: str, color: str, metadata: Metadata):
    """
    Prints to output and automatically handles metadata properties.
    
    >>> write('Hello!', 'green', metadata)
    >>> Hello!
    
    #### Arguments
        text (`str`): Text to display to output
        color (`str`): Text color
        metadata (`Metadata`): Metadata for the method
    """

    if not metadata.silent:
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
    Write verbose text to the output (used with --verbose). 
    
    All logs are `green` in color prefixed with `VERBOSE:`

    Uses `click.echo()` for better unicode support.

    #### Usage
    >>> write_verbose('Writing to verbose!', metadata)
    >>> VERBOSE: Writing to verbose!
    
    #### Arguments
        log (`str`): Text to write to verbose output
        metadata (`Metadata`): Metadata for the method
    """

    if metadata.verbose and not metadata.silent:
        HEADER = "VERBOSE: "
        
        if not metadata.no_color:
            click.echo(click.style(HEADER + log, fg="green", dim=True))
        else:
            click.echo(click.style(HEADER + log))


def write_debug(log: str, metadata: Metadata, newline=False):
    """
    Write debug text to the output (used with --debug). 
    All logs are `yellow` in color prefixed with `DEBUG:`
    Uses `click.echo()` for better unicode support.

    #### Usage
    >>> write('Writing to debug!', metadata)
    >>> DEBUG: Writing to debug!

    #### Arguments 
        log (`str`): Text to write to debug output
        metadata (`Metadata`): Metadata for the method.
        newline (`bool`, `optional`): Whether debug has to be logged into a new line. Defaults to False.
    """
    
    if metadata.debug and not metadata.silent:
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
    
    #### Usage
    >>> write_all('Writing to all 3 levels!', 'green', metadata)
    
    ##### Output
    `Writing to all 3 levels!`
    `VERBOSE: Writing to all 3 levels!`
    `DEBUG: Writing to all 3 levels!`
    

    #### Arguments
        text (`str`): Text to write to all levels
        color (`str`): Color of the text used in `write`
        metadata (`Metadata`): Metadata for the method
    """    
    write(text, color, metadata)
    write_verbose(text, metadata)
    write_debug(text, metadata)

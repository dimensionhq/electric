######################################################################
#                     SUPERCHARGECLI (EXTENSIONS)                    #
######################################################################


# -*- coding: utf-8 -*-

"""
    Extension for the python ``click`` module to provide
    a group with a git-like *did-you-mean* feature.
"""

import click
import difflib
from colorama import Fore

__version__ = "0.0.3"

_click7 = click.__version__[0] >= '7'


class DYMMixin(object):  # pylint: disable=too-few-public-methods
    """
    Mixin class for click MultiCommand inherited classes
    to provide git-like *did-you-mean* functionality when
    a certain command is not registered.
    """

    def __init__(self, *args, **kwargs):
        self.max_suggestions = kwargs.pop("max_suggestions", 3)
        self.cutoff = kwargs.pop("cutoff", 0.5)
        super(DYMMixin, self).__init__(*args, **kwargs)
        self._commands = {}
        self._aliases = {}

    def resolve_command(self, ctx, args):
        """
        Overrides clicks ``resolve_command`` method
        and appends *Did you mean ...* suggestions
        to the raised exception message.
        """
        original_cmd_name = click.utils.make_str(args[0])

        try:
            return super(DYMMixin, self).resolve_command(ctx, args)
        except click.exceptions.UsageError as error:
            error_msg = str(error)
            matches = difflib.get_close_matches(original_cmd_name,
                                                self.list_commands(ctx), self.max_suggestions, self.cutoff)
            if matches:
                error_msg += '\n\nDid you mean one of these?\n    %s' % '\n    '.join(
                    matches)  # pylint: disable=line-too-long

            raise click.exceptions.UsageError(error_msg, error.ctx)

    def command(self, *args, **kwargs):
        aliases = kwargs.pop('aliases', [])
        decorator = super(DYMMixin, self).command(*args, **kwargs)
        if not aliases:
            return decorator

        def _decorator(f):
            cmd = decorator(f)
            if aliases:
                self._commands[cmd.name] = aliases
                for alias in aliases:
                    self._aliases[alias] = cmd.name
            return cmd

        return _decorator

    def group(self, *args, **kwargs):
        aliases = kwargs.pop('aliases', [])
        decorator = super(DYMMixin, self).group(*args, **kwargs)
        if not aliases:
            return decorator

        def _decorator(f):
            cmd = decorator(f)
            if aliases:
                self._commands[cmd.name] = aliases
                for alias in aliases:
                    self._aliases[alias] = cmd.name
            return cmd

        return _decorator

    def resolve_alias(self, cmd_name):
        if cmd_name in self._aliases:
            return self._aliases[cmd_name]
        return cmd_name

    def get_command(self, ctx, cmd_name):
        cmd_name = self.resolve_alias(cmd_name)
        command = super(DYMMixin, self).get_command(ctx, cmd_name)
        if command:
            return command

    def format_commands(self, ctx, formatter):
        rows = []

        sub_commands = self.list_commands(ctx)

        max_len = max(len(cmd) for cmd in sub_commands)
        limit = formatter.width - 6 - max_len

        for sub_command in sub_commands:
            cmd = self.get_command(ctx, sub_command)
            if cmd is None:
                continue
            if hasattr(cmd, 'hidden') and cmd.hidden:
                continue
            if sub_command in self._commands:
                aliases = ','.join(sorted(self._commands[sub_command]))
                sub_command = '{0} ({1})'.format(sub_command, aliases)
            cmd_help = cmd.get_short_help_str(limit) if _click7 else cmd.short_help or ''
            rows.append((sub_command, cmd_help))

        if rows:
            with formatter.section('Commands'):
                formatter.write_dl(rows)

    def format_help(self, ctx, formatter):
        message = f'''eel Electric Plugin Manager v1.0.0 Alpha
Copyright (c) Electric Inc.

Usage: eel <command> [<options>]

{Fore.LIGHTGREEN_EX}Commands:{Fore.RESET}
    convert'''
        click.echo(message)


class SuperChargeCLI(DYMMixin, click.Group):  # pylint: disable=too-many-public-methods
    """
    click Group to provide git-like
    *did-you-mean* functionality when a certain
    command is not found in the group.
    """
    # def format_help(self, ctx, formatter):
    #     # Custom Help Message =>
    #     click.echo(click.style('Commands :', fg='bright_green'))
    #     click.echo('Next Line')


class DYMCommandCollection(DYMMixin, click.CommandCollection):  # pylint: disable=too-many-public-methods
    """
    click CommandCollection to provide git-like
    *did-you-mean* functionality when a certain
    command is not found in the group.
    """

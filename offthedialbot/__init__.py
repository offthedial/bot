"""Contains client subclass of discord.ext.Bot, and registers listeners, commands, and cogs."""

from discord.ext.commands import Bot

from offthedialbot import cogs
from offthedialbot import commands
from offthedialbot import listeners
from . import log, help


class Client(Bot):
    """Subclass of commands.Bot containing helpful constants."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.logger = log.logger
        self.help_command = help.help_command


client = Client(command_prefix='$')

cogs.register_cogs(client)
commands.register_commands(client)
listeners.register_listeners(client)

"""Contains client subclass of discord.ext.Bot, and registers listeners, commands, and cogs."""
from discord.ext.commands import Bot

from .env import env
from .log import logger
from .help import help_command

from offthedialbot import cogs
from offthedialbot import commands
from offthedialbot import listeners


class Client(Bot):
    """Subclass of commands.Bot containing helpful constants."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.logger = logger
        self.help_command = help_command


client = Client(command_prefix='$')

cogs.register_cogs(client)
logger.debug("Cogs registered.")
commands.register_commands(client)
logger.debug("Commands registered.")
listeners.register_listeners(client)
logger.debug("Listeners registered.")

"""Holds client subclass of discord.ext.Bot, and registeres commands."""

from discord.ext.commands import Bot

from offthedialbot import listeners
from offthedialbot import commands
from offthedialbot import cogs

client = Bot(command_prefix='$')

listeners.register_listeners(client)
commands.register_commands(client)
cogs.register_cogs(client)

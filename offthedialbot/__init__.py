"""Holds client subclass of discord.ext.Bot, and registeres commands."""

from discord.ext.commands import Bot

from offthedialbot import commands
from offthedialbot import cogs
from offthedialbot import listeners

client = Bot(command_prefix='$')

commands.register_commands(client)
cogs.register_cogs(client)
listeners.register_listeners(client)

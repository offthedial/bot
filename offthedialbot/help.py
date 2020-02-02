"""Sets up help command for the bot."""
import discord
from discord.ext import commands
from offthedialbot import utils


class HelpCommand(commands.DefaultHelpCommand):
    """Help command for the bot."""


help_command = HelpCommand()

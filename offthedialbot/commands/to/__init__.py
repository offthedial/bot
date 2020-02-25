"""$to"""
from discord.ext import commands

from offthedialbot import utils


@utils.deco.require_role("Organiser")
async def main(ctx):
    """Command tools for managing tournaments."""
    raise commands.TooManyArguments

"""$test"""
from offthedialbot import utils


@utils.deco.require_role("Developer")
async def main(ctx):
    """Commands to help with testing the bot."""
    pass

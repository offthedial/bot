"""$test"""
from offthedialbot import utils


class Test(utils.Command, hidden=True):
    """Commands to help with testing the bot."""

    @classmethod
    @utils.deco.require_role("Developer")
    async def main(cls, ctx):
        """Commands to help with testing the bot."""

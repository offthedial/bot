"""$test"""

from offthedialbot import utils


class TestHelp(utils.Command, hidden=True):
    """Commands to help with testing the bot."""

    @classmethod
    async def main(cls, ctx):
        """Commands to help with testing the bot."""
        await utils.Alert(ctx, utils.Alert.Style.INFO,
            title="Having trouble with the bot?",
            description="\n".join([
                "All directions are __in the embed__!",
                "That means, to navigate the commands, simply read the bot message!",
                "If you are still stuck, you can ask for help in #helpdesk."
            ]))

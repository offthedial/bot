"""$test"""
from offthedialbot import utils


async def main(ctx):
    """Commands to help with testing the bot."""
    await utils.Alert(ctx, utils.Alert.Style.INFO,
        title="Having trouble with the bot?",
        description="\n".join([
            "All directions are __in the embed__!",
            "That means, to navigate the commands, simply read the bot message!",
            "If you are still stuck, you can ask for help in #helpdesk."
        ]))

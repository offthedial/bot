import discord

import utils


async def main(ctx):
    """$profile command."""
    profile = utils.dbh.find_profile(id=ctx.author.id)
    if profile is None:
        await utils.Alert(
            ctx, utils.Alert.Colors.DANGER, title="No profile found.", description="You don't have a profile."
        )
        raise utils.exc.CommandCancel


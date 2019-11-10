import discord

import utils


async def main(ctx, arg):
    """$profile command."""
    profile = utils.dbh.find_profile(id=ctx.author.id)
    if profile is None:
        alert = utils.embeds.alert(
            utils.AlertStyle.DANGER, title="No profile found.", description="You don't have a profile."
        )
        await ctx.send(embed=alert)
        raise utils.exc.CommandCancel


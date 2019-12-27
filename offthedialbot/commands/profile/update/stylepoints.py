import discord

import utils
from .. import create, check_for_profile


async def main(ctx):
    """Run command for $profile update."""
    profile = await check_for_profile(ctx)
    ui: utils.CommandUI = await utils.CommandUI(ctx, create.create_stylepoints_embed(ctx))

    profile.set_stylepoints(await create.get_user_stylepoints(ui))

    utils.dbh.update_profile(profile.dict(), ui.ctx.author.id)
    await ui.end(True)

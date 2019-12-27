import utils
from .. import create, check_for_profile


async def main(ctx):
    """Run command for $profile update."""
    profile: utils.Profile = await check_for_profile(ctx)
    ui: utils.CommandUI = await utils.CommandUI(ctx, create.create_cxp_embed(ctx))

    profile.set_cxp(await create.get_user_cxp(ui))

    utils.dbh.update_profile(profile.dict(), ui.ctx.author.id)
    await ui.end(True)

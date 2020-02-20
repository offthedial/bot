"""$profile update cxp"""
from offthedialbot import utils
from .. import create, check_for_profile


async def main(ctx):
    """Update your competitive experience."""
    profile: utils.Profile = await check_for_profile(ctx)
    ui: utils.CommandUI = await utils.CommandUI(ctx, create.create_cxp_embed(ctx))

    profile.set_cxp(await create.get_user_cxp(ui))
    profile.write()
    await ui.end(True)

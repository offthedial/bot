"""$profile update stylepoints"""
from offthedialbot import utils
from .. import create, check_for_profile


async def main(ctx):
    """Update your stylepoints."""
    profile: utils.Profile = await check_for_profile(ctx)
    ui: utils.CommandUI = await utils.CommandUI(ctx, create.create_stylepoints_embed(ctx))

    profile.set_stylepoints(await create.get_user_stylepoints(ui))
    profile.write()
    await ui.end(True)

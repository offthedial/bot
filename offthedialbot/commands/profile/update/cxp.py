"""$profile update cxp"""
from offthedialbot import utils
from .. import create


@utils.deco.profile_required()
async def main(ctx):
    """Update your competitive experience."""
    profile: utils.Profile = utils.Profile(ctx.author.id)
    ui: utils.CommandUI = await utils.CommandUI(ctx, create.create_cxp_embed(ctx))

    profile.set_cxp(await create.get_user_cxp(ui))
    profile.write()
    await ui.end(True)

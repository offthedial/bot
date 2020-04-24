"""$profile update stylepoints"""
from offthedialbot import utils
from .. import create


@utils.deco.profile_required()
async def main(ctx):
    """Update your stylepoints."""
    profile: utils.Profile = utils.Profile(ctx.author.id)
    ui: utils.CommandUI = await utils.CommandUI(ctx, create.create_stylepoints_embed(ctx))

    profile.set_stylepoints(await create.get_user_stylepoints(ui, profile.get_stylepoints()))
    profile.write()
    await ui.end(True)

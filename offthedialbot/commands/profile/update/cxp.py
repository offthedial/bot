"""$profile update cxp"""
from offthedialbot import utils
from ..create import ProfileCreate


class ProfileUpdateCxp(utils.Command):
    """Update your competitive experience."""

    @classmethod
    @utils.deco.profile_required()
    async def main(cls, ctx):
        """Update your competitive experience."""
        profile: utils.Profile = utils.Profile(ctx.author.id)
        ui: utils.CommandUI = await utils.CommandUI(ctx, ProfileCreate.create_cxp_embed())

        profile.set_cxp(await ProfileCreate.get_user_cxp(ui))
        profile.write()
        await ui.end(True)

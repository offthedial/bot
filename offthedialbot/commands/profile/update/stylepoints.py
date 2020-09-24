"""$profile update stylepoints"""

from offthedialbot import utils
from ..create import ProfileCreate


class ProfileUpdateStylepoints(utils.Command):
    """Update your stylepoints."""

    @classmethod
    @utils.deco.profile_required()
    async def main(cls, ctx):
        """Update your stylepoints."""
        profile: utils.Profile = utils.Profile(ctx.author.id)
        ui: utils.CommandUI = await utils.CommandUI(ctx, ProfileCreate.create_stylepoints_embed())

        profile.set_stylepoints(await ProfileCreate.get_user_stylepoints(ui, profile.get_stylepoints()))
        profile.write()
        await ui.end(True)

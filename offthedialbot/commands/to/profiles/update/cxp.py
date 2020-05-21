"""$to profiles update cxp"""
from offthedialbot import utils
from offthedialbot.commands.profile.create import ProfileCreate
from . import update_profile_key


class ToProfilesUpdateCxp(utils.Command):
    """Update user's competitive experience."""

    @classmethod
    @utils.deco.require_role("Organiser")
    async def main(cls, ctx):
        """Update user's competitive experience."""
        await update_profile_key(ctx, cls.update_cxp)

    @classmethod
    async def update_cxp(cls, ctx, profile, username):
        """Modified $profile update cxp command."""
        ui: utils.CommandUI = await utils.CommandUI(ctx, ProfileCreate.create_cxp_embed())
        ui.embed.description = f"{username}'s Competitive Experience"

        profile.set_cxp(await ProfileCreate.get_user_cxp(ui))
        profile.write()
        await ui.end(True)

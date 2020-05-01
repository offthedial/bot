"""$to profiles update stylepoints"""
from offthedialbot import utils
from offthedialbot.commands.profile.create import ProfileCreate
from . import update_profile_key


class ToProfilesUpdateStylepoints(utils.Command):
    """Update user's stylepoints."""

    @classmethod
    @utils.deco.require_role("Organiser")
    async def main(cls, ctx):
        """Update user's stylepoints."""
        await update_profile_key(ctx, cls.update_stylepoints)

    @classmethod
    async def update_stylepoints(cls, ctx, profile, username):
        """Modified $profile update stylepoints command."""
        ui: utils.CommandUI = await utils.CommandUI(ctx, ProfileCreate.create_stylepoints_embed(ctx))
        ui.embed.description = f"{username}'s Stylepoints"

        profile.set_stylepoints(await ProfileCreate.get_user_stylepoints(ui))
        profile.write()
        await ui.end(True)

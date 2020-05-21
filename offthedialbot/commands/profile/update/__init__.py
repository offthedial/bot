"""$profile update"""
from offthedialbot import utils
from .. import Profile
from ..create import ProfileCreate


class ProfileUpdate(utils.Command):
    """Update your profile."""

    @classmethod
    @utils.deco.profile_required()
    async def main(cls, ctx):
        """Update your profile."""
        profile: utils.Profile = utils.Profile(ctx.author.id)
        await cls.update_profile(ctx, profile)

    @classmethod
    async def update_profile(cls, ctx, profile, title=None):
        """Update profile given profile."""
        embed, emojis = cls.create_update_embed(ctx, profile)
        if title:
            embed.title = title
        ui: utils.CommandUI = await utils.CommandUI(ctx, embed)

        reply = await ui.get_valid_reaction(emojis)
        index: int = emojis.index(reply.emoji)
        field = ProfileCreate.clean_status_key(profile, ['IGN', 'SW', 'Ranks'][index])
        await cls.wait_profile_field(ui, profile, index, field)

    @classmethod
    async def wait_profile_field(cls, ui: utils.CommandUI, profile: utils.Profile, index, field) -> None:
        """wait for reply and write updated field."""
        ui.embed.clear_fields()
        ui.embed.add_field(name=field[0], value=Profile.display_field(*field))

        await cls.set_field(ui, profile, index)

        # Confirm profile and save it
        if await ProfileCreate.confirm_profile(ui):
            profile.write()
            await ui.end(True)
        else:
            ui.embed, _ = cls.create_update_embed(ui.ctx, profile)
            await cls.wait_profile_field(ui, profile, index, field)

    @classmethod
    async def set_field(cls, ui: utils.CommandUI, profile: utils.Profile, index: int) -> None:
        """Wait for user to type whichever field they want to update."""
        await [
            lambda: ProfileCreate.set_status_field(ui, profile, "IGN", 0),
            lambda: ProfileCreate.set_status_field(ui, profile, "SW", 0),
            lambda: ProfileCreate.set_rank_field(ui, profile, 0),
        ][index]()

    @classmethod
    def create_update_embed(cls, ctx, profile: utils.Profile):
        """Create status embed, with some adjustments."""
        embed = Profile.create_status_embed(ctx.author.display_name, profile)
        emojis: list = []
        for (index, field), emoji in zip(enumerate(embed.fields), utils.emojis.digits):
            embed.set_field_at(index,
                name=(f"{emoji} " + field.name),
                value=field.value,
                inline=field.name != "Ranks")
            emojis.append(emoji)
        embed.title = "React with the field you would like to change."
        return embed, emojis

from commands.profile import check_for_profile, display_field
import utils
from discord.ext import commands


class GetField(commands.Cog, command_attrs=dict(hidden=True)):
    """Cog containing comands to easily get profile fields."""

    @commands.command(aliases=["fc"])
    async def sw(self, ctx):
        """Quickly gets SW profile field."""
        profile = await check_for_profile(ctx)
        await utils.Alert(ctx, utils.Alert.Style.INFO, title=f"**{ctx.author.display_name}'s Friend-Code:**", description=f"`{display_field('SW', profile['status']['SW'])}`")

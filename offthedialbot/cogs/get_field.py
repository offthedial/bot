from commands.profile import check_for_profile, display_field
import utils
from discord.ext import commands


class GetField(commands.Cog, command_attrs=dict(hidden=True)):
    """Cog containing comands to easily get profile fields."""

    @commands.command(aliases=["fc"])
    async def sw(self, ctx):
        """Quickly gets SW profile field."""
        try:
            profile = await check_for_profile(ctx)
        except utils.exc.CommandCancel:
            return
        await utils.Alert(ctx, utils.Alert.Style.INFO, title=f"`{profile['status']['IGN']}`'s Friend Code:", description=f"`{display_field('SW', profile['status']['SW'])}`")

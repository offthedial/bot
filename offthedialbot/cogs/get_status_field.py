from commands.profile import check_for_profile, display_field
import utils
from discord.ext import commands


class GetStatusField(commands.Cog, command_attrs=dict(hidden=True)):
    """Cog containing comands to easily get profile fields."""

    @commands.command(aliases=["fc"])
    async def sw(self, ctx):
        """Quickly gets SW status field."""
        try:
            profile = await check_for_profile(ctx)
        except utils.exc.CommandCancel:
            return
        await utils.Alert(ctx, utils.Alert.Style.INFO, title=f"`{profile['status']['IGN']}`'s Friend Code:", description=f"{display_field('SW', profile['status']['SW'])}")

    @commands.command()
    async def ign(self, ctx):
        """Quickly gets IGN status field."""
        try:
            profile = await check_for_profile(ctx)
        except utils.exc.CommandCancel:
            return
        await utils.Alert(ctx, utils.Alert.Style.INFO, title=f"{ctx.author.display_name}'s IGN:", description=f"{display_field('IGN', profile['status']['IGN'])}")

    @commands.command()
    async def ranks(self, ctx):
        """Quickly gets SW status field."""
        try:
            profile = await check_for_profile(ctx)
        except utils.exc.CommandCancel:
            return

        await utils.Alert(
            ctx, utils.Alert.Style.INFO,
            title=f"`{profile['status']['IGN']}`'s Ranks:",
            description=f"{display_field('Ranks', profile['status']['Ranks'])}"
        )

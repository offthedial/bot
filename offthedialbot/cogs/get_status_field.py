"""cogs.GetStatusField"""
from discord.ext import commands

from offthedialbot import utils
from offthedialbot.commands.profile import check_for_profile, display_field


class GetStatusField(commands.Cog, command_attrs={'hidden': True}):
    """Quickly fetch the value of one of your status fields."""

    @commands.command(aliases=["fc"])
    async def sw(self, ctx: commands.Context):
        """Quickly sends your friend-code."""
        try:
            profile: utils.Profile = await check_for_profile(ctx)
        except utils.exc.CommandCancel:
            return
        await utils.Alert(ctx, utils.Alert.Style.INFO, title=f"`{profile.get_status()['IGN']}`'s Friend Code:",
                          description=f"{display_field('SW', profile.get_status()['SW'])}")

    @commands.command()
    async def ign(self, ctx: commands.Context):
        """Quickly sends your IGN."""
        try:
            profile: utils.Profile = await check_for_profile(ctx)
        except utils.exc.CommandCancel:
            return
        await utils.Alert(ctx, utils.Alert.Style.INFO, title=f"{ctx.author.display_name}'s IGN:",
                          description=f"{display_field('IGN', profile.get_status()['IGN'])}")

    @commands.command()
    async def ranks(self, ctx: commands.Context):
        """Quickly sends your ranks."""
        try:
            profile: utils.Profile = await check_for_profile(ctx)
        except utils.exc.CommandCancel:
            return

        await utils.Alert(
            ctx, utils.Alert.Style.INFO,
            title=f"`{profile.get_status()['IGN']}`'s Ranks:",
            description=f"{display_field('Ranks', profile.get_status()['Ranks'])}"
        )

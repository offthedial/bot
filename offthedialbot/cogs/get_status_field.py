"""cogs.GetStatusField"""
from discord.ext import commands

from offthedialbot import utils
from offthedialbot.commands.profile import display_field


class GetStatusField(commands.Cog, command_attrs={'hidden': True}):
    """Quickly fetch the value of one of your status fields."""

    @commands.command(aliases=["fc"])
    @utils.deco.profile_required()
    async def sw(self, ctx: commands.Context):
        """Quickly sends your friend-code."""
        try:
            profile: utils.Profile = utils.Profile(ctx.author.id)
        except utils.exc.CommandCancel:
            return
        await utils.Alert(
            ctx, utils.Alert.Style.INFO,
            title=f"`{profile.get_status()['IGN']}`'s Friend Code:",
            description=f"{display_field('SW', profile.get_status()['SW'])}"
        )

    @commands.command()
    @utils.deco.profile_required()
    async def ign(self, ctx: commands.Context):
        """Quickly sends your IGN."""
        try:
            profile: utils.Profile = utils.Profile(ctx.author.id)
        except utils.exc.CommandCancel:
            return
        await utils.Alert(
            ctx, utils.Alert.Style.INFO,
            title=f"{ctx.author.display_name}'s IGN:",
            description=f"{display_field('IGN', profile.get_status()['IGN'])}"
        )

    @commands.command()
    @utils.deco.profile_required()
    async def ranks(self, ctx: commands.Context):
        """Quickly sends your ranks."""
        try:
            profile: utils.Profile = utils.Profile(ctx.author.id)
        except utils.exc.CommandCancel:
            return

        await utils.Alert(
            ctx, utils.Alert.Style.INFO,
            title=f"`{profile.get_status()['IGN']}`'s Ranks:",
            description=f"{display_field('Ranks', profile.get_status()['Ranks'])}"
        )

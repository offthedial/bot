"""cogs.GetStatusField"""
from discord.ext import commands

from offthedialbot import utils
from offthedialbot.commands.profile import Profile


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
        await utils.Alert(ctx, utils.Alert.Style.INFO,
            title=f"`{profile.get_ign()}`'s Friend Code:",
            description=f"{Profile.display_field('SW', profile.get_sw())}")

    @commands.command()
    @utils.deco.profile_required()
    async def ign(self, ctx: commands.Context):
        """Quickly sends your IGN."""
        try:
            profile: utils.Profile = utils.Profile(ctx.author.id)
        except utils.exc.CommandCancel:
            return
        await utils.Alert(ctx, utils.Alert.Style.INFO,
            title=f"{ctx.author.display_name}'s IGN:",
            description=f"{Profile.display_field('IGN', profile.get_ign())}")

    @commands.command()
    @utils.deco.profile_required()
    async def ranks(self, ctx: commands.Context):
        """Quickly sends your ranks."""
        try:
            profile: utils.Profile = utils.Profile(ctx.author.id)
        except utils.exc.CommandCancel:
            return
        await utils.Alert(ctx, utils.Alert.Style.INFO,
            title=f"`{profile.get_ign()}`'s Ranks:",
            description=f"{Profile.display_field('Ranks', profile.get_ranks())}")

import discord
from discord.ext import commands

from offthedialbot import utils
from offthedialbot.commands.profile import create, update


class Checkin(commands.Cog, command_attrs={'hidden': True}):
    """Quickly fetch the value of one of your status fields."""

    @commands.command(enabled=False)
    # @utils.deco.otd_only
    @utils.deco.tourney(open=False)
    @utils.deco.profile_required(competing=True)
    async def checkin(self, ctx: commands.Context):
        """Check in."""
        # Get Checked In role, or create it.
        if not (role := discord.utils.get(ctx.guild.roles, name='Checked In')):
            role = await ctx.guild.create_role(name="Checked In")
        
        # Check the attendee in
        await ctx.author.add_roles(role)
        await utils.Alert(ctx, utils.Alert.Style.SUCCESS,
            title="Check-in Complete",
            description="You are all set! Good luck in the tournament!"
        )
    
    @checkin.error
    async def checkin_error(self, ctx, error):
        if isinstance(error, commands.errors.DisabledCommand):
            await utils.Alert(ctx, utils.Alert.Style.DANGER,
                title="Command Disabled",
                description="You can't use this command right now."
            )
        else:
            raise error
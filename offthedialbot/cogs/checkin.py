"""cogs.Checkin"""
import discord
from discord.ext import commands

from offthedialbot import utils
from offthedialbot.commands.signup import profile_updated


class Checkin(commands.Cog, command_attrs={'hidden': True}):
    """Cog holding check-in command for easy disabling."""

    @commands.command(enabled=False)
    @utils.deco.otd_only
    @utils.deco.tourney(open=False)
    @utils.deco.profile_required(competing=True)
    async def checkin(self, ctx: commands.Context):
        """Check in."""
        # Get Checked In role, or create it.
        ui: utils.CommandUI = await utils.CommandUI(ctx, discord.Embed(title="Check-in Form", color=utils.colors.COMPETING))
        await profile_updated(ui, True)
        if not (role := utils.roles.get(ctx, "Checked In")):
            role = await ui.ctx.guild.create_role(name="Checked In")
        
        # Check the attendee in
        await ui.ctx.author.add_roles(role)  # Add roles
        await utils.time.Timer.delete(destination=ctx.author.id, author=ctx.me.id)  # Remove warning
        
        await ui.end(True)
    
    @checkin.error
    async def checkin_error(self, ctx, error):
        if isinstance(error, commands.errors.DisabledCommand):
            await utils.Alert(ctx, utils.Alert.Style.DANGER,
                title="Command Disabled",
                description="You can't use this command right now."
            )
        else:
            raise error

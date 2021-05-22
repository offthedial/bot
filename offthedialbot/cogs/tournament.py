"""cogs.Tournament"""

import discord
from discord.ext import tasks, commands

from offthedialbot import utils
from offthedialbot.commands.to.sync import ToSync


class Tournament(commands.Cog, command_attrs={'hidden': True}):
    """Cog holding tournament-related misc commands."""
    def __init__(self, bot):
        self.bot = bot
        self.sync.start()

    @tasks.loop(hours=1)
    async def sync(self):
        """Task loop that assigns roles."""
        await ToSync.sync(self.bot)

    @sync.before_loop
    async def before_loop(self):
        await self.bot.wait_until_ready()

    @commands.command()
    async def checkin(self, ctx: commands.Context):
        """Check in for the tournament."""
        # Return if the user isn't competing or the command isn't run in Off the Dial
        if not (role := discord.utils.get(ctx.guild.roles, name="Signed Up!")) or not ctx.guild.id == ctx.bot.OTD.id:
            raise utils.exc.CommandCancel(title="Access Denied.", description="You don't have permission to run this command.")

        # Get Checked In role, or create it.
        if role := discord.utils.get(ctx.guild.roles, name="Checked In"):
            # Check the attendee in
            await ctx.author.add_roles(role)  # Add roles
            await ctx.message.add_reaction('✅')
        else:
            raise utils.exc.CommandCancel(title="Access Denied.", description="Check-in is currently not open.")

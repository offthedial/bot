"""cogs.Tournament"""

from discord.ext import tasks, commands

from offthedialbot import utils
from offthedialbot.commands.to.sync import ToSync


class Tournament(commands.Cog, command_attrs={'hidden': True}):
    """Cog holding tournament-related misc commands."""
    def __init__(self, bot):
        self.bot = bot

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
        if not (role := utils.roles.get(ctx, "Competing")) or not ctx.guild.id == ctx.bot.OTD.id:
            return

        # Get Checked In role, or create it.
        if not (role := utils.roles.get(ctx, "Checked In")):
            role = await ctx.guild.create_role(name="Checked In")

        # Check the attendee in
        await ctx.author.add_roles(role)  # Add roles
        await ctx.message.add_reaction('✅')

"""cogs.Flairme"""
from discord.ext import commands

from offthedialbot import utils


class Flairme(commands.Cog):
    """Contains flairme command group."""

    @commands.group(invoke_without_command=True)
    async def flairme(self, ctx):
        """Give yourself applicable flairs."""
        raise commands.TooManyArguments

    @flairme.command()
    async def alerts(self, ctx):
        """Flair or unflair the Off the Dial Alerts role."""
        await self.give_flair(ctx, "Off the Dial Alerts")

    @flairme.command()
    async def detective(self, ctx):
        """Flair or unflair the Detective role."""
        await self.give_flair(ctx, "Detective")

    @flairme.command()
    async def pickup(self, ctx):
        """Flair or unflair the LF: Pickup Scrim role."""
        await self.give_flair(ctx, "LF: Pickup Scrim")

    @flairme.command()
    async def league(self, ctx):
        """Flair or unflair the LF: League role."""
        await self.give_flair(ctx, "LF: League")

    @flairme.command()
    async def lf(self, ctx):
        """Flair or unflair the LF: role."""
        await self.give_flair(ctx, "LF:")

    async def give_flair(self, ctx, flair_name):
        flair = utils.roles.get(ctx, flair_name)
        if not flair:
            await utils.Alert(ctx, utils.Alert.Style.DANGER, title="Role not found", description="I can't seem to find that role...")
        else:
            if flair_name in [role.name for role in ctx.author.roles]:
                await ctx.author.remove_roles(flair)
                title = "Removed Flair"
                description = f"You no longer have the {flair_name} flair"
            else:
                await ctx.author.add_roles(flair)
                title = "Given Flair"
                description = f"You have been given the {flair_name} flair"
            await utils.Alert(ctx, utils.Alert.Style.SUCCESS, title=title, description=description)

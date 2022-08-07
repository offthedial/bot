"""$playing"""

from offthedialbot import utils


class playing(utils.Command):
    """Command to toggle the LF: role."""

    @classmethod
    async def main(cls, ctx):
        playing_role = ctx.guild.get_role(562646704017506321)

        if playing_role in ctx.author.roles:
            # Remove role
            await ctx.author.remove_roles(playing_role)
            await ctx.message.add_reaction('❎')
        else:
            # Add role
            await ctx.author.add_roles(playing_role)
            await ctx.message.add_reaction('✅')

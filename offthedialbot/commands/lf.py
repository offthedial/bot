"""$lf"""

from offthedialbot import utils


class Lf(utils.Command):
    """Command to toggle the LF: role."""

    @classmethod
    async def main(cls, ctx):
        lf_role = ctx.guild.get_role(562646704017506321)

        if lf_role in ctx.author.roles:
            # Remove role
            await ctx.author.remove_roles(lf_role)
            await ctx.message.add_reaction('❎')
        else:
            # Add role
            await ctx.author.add_roles(lf_role)
            await ctx.message.add_reaction('✅')

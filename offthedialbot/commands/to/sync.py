"""$to sync"""

import discord

from offthedialbot import utils


class ToSync(utils.Command):
    """Command to directly sync tournament data."""

    @classmethod
    @utils.deco.require_role("Staff")
    async def main(cls, ctx):
        """Sync tournament."""
        await cls.sync(ctx.bot)
        await ctx.message.add_reaction('♻️')

    @staticmethod
    async def sync(bot, smashgg=True):
        """Synchronize smash.gg tournament data and competing roles."""
        tourney = utils.Tournament()
        if smashgg:
            await tourney.sync_smashgg()

        # Sync competing roles
        if not (docs := tourney.signups()):
            return

        ids = [int(doc.id) for doc in docs]
        guild = bot.get_guild(374715620052172800)
        role = guild.get_role(415767083691802624)

        for sign in role.members:
            if not sign.id in ids:
                await sign.remove_roles(role)
        for id in ids:
            user = guild.get_member(id)
            await user.add_roles(role)

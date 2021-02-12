"""$to sync"""

import discord

from offthedialbot import utils


class ToSync(utils.Command):

    @classmethod
    @utils.deco.require_role("Staff")
    async def main(cls, ctx):
        """Synchronize smash.gg tournament data and competing roles."""
        await cls.sync(ctx.bot)
        await ctx.message.add_reaction('♻️')

    @classmethod
    async def sync(cls, bot, smashgg=True):
        tourney = await cls.sync_tournament(smashgg)
        guild = await cls.sync_competing(bot, tourney)
        await cls.sync_signal_strength(guild)

    @staticmethod
    async def sync_tournament(smashgg):
        tourney = utils.Tournament()
        if smashgg:
            await tourney.sync_smashgg()
        return tourney

    @staticmethod
    async def sync_competing(bot, tourney):
        """Sync competing roles."""
        if docs := tourney.signups():
            ids = [int(doc.id) for doc in docs]
        else:
            ids = []

        guild = bot.get_guild(374715620052172800)
        role = guild.get_role(415767083691802624)

        for sign in role.members:
            if not sign.id in ids:
                await sign.remove_roles(role)
        for id in ids:
            user = guild.get_member(id)
            await user.add_roles(role)

        return guild

    @staticmethod
    async def sync_signal_strength(guild):
        """Add signal strength roles to users."""
        users = utils.db.collection(u'users').where(u'meta.signal', u'>', 999).stream()
        role_1k = guild.get_role(809674067380666400)
        role_5k = guild.get_role(809674415867428936)
        # Loop over users
        for user in users:
            user = utils.User(user.id)
            discord = await user.discord(guild)
            signal = user.dict["meta"]["signal"]
            # Add roles depending on milestones
            if signal >= 1000:
                await discord.add_roles(role_1k)
            if signal >= 5000:
                await discord.add_roles(role_5k)

"""$to sync"""

import discord

from offthedialbot import utils


class ToSync(utils.Command):

    @classmethod
    @utils.deco.require_role("Staff")
    async def main(cls, ctx):
        """Synchronize sendou.ink tournament data and competing roles."""
        await cls.sync(ctx.bot)
        await ctx.message.add_reaction('♻️')

    @classmethod
    async def sync(cls, bot, sendou=True):
        tourney = await cls.sync_tournament(sendou)
        guild = await cls.sync_competing(bot, tourney)
        await cls.sync_teams(guild, tourney)
        await cls.sync_signal_strength(guild)

    @staticmethod
    async def sync_tournament(sendou):
        tourney = utils.Tournament()
        if sendou:
            await tourney.sync_sendou()
        return tourney

    @staticmethod
    async def sync_teams(guild, tourney):
        teams = await utils.sendou.teams(tourney.dict["sendouId"])
        if not teams:
            # No teams registered yet. Don't read that as "delete every role".
            return

        color = discord.Color(utils.colors.COMPETING)
        stale = {
            role.name: role for role in guild.roles
            if role.color == color and role.name != "Signed Up!"
        }

        for team in teams:
            role = stale.pop(team["name"], None)
            if role is None:
                role = await guild.create_role(name=team["name"], color=color)

            wanted = {
                member for m in team["members"]
                if (member := guild.get_member(int(m["discordId"])))
            }
            for member in set(role.members) - wanted:
                await member.remove_roles(role)
            for member in wanted - set(role.members):
                await member.add_roles(role)

        # Whatever is left has no matching team on sendou anymore
        for role in stale.values():
            await role.delete()

    @staticmethod
    async def sync_competing(bot, tourney):
        """Sync competing roles."""
        guild = bot.OTD
        if docs := tourney.signups():
            ids = [int(doc.id) for doc in docs]
        else:
            checkin_role = discord.utils.get(guild.roles, name="Checked In")
            if checkin_role:
                await checkin_role.delete()
            ids = []

        role = discord.utils.get(guild.roles, name="Signed Up!")

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
            user_discord = user.discord(guild)
            if not user_discord:
                continue

            # Add roles depending on milestones
            signal = user.dict["meta"]["signal"]
            if signal >= 1000:
                await user_discord.add_roles(role_1k)
            if signal >= 5000:
                await user_discord.add_roles(role_5k)

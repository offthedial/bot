"""$to rosters"""
import asyncio

import discord

from offthedialbot import utils


class ToRosters(utils.Command):

    @classmethod
    @utils.deco.require_role("Staff")
    async def main(cls, ctx):
        """Send a roster message for every team, pinging the team and its players."""
        tourney = utils.Tournament()
        async with ctx.typing():
            teams = await utils.sendou.teams(tourney.dict["sendouId"], ctx=ctx)
        if not teams:
            raise utils.exc.CommandCancel(
                title="No teams detected",
                description=f"No teams are registered on {tourney.sendou_link} yet.")

        for team in teams:
            await ctx.send(cls.roster(ctx, team))
            await asyncio.sleep(0.2)

    @staticmethod
    def roster(ctx, team):
        """Build the `@team - @player @player` message for a single team."""
        color = discord.Color(utils.colors.COMPETING)
        role = discord.utils.find(
            lambda r: r.name == team["name"] and r.color == color, ctx.guild.roles)
        members = " ".join(
            member.mention for m in team["members"]
            if (member := ctx.guild.get_member(int(m["discordId"])))
        )
        return f"{role.mention if role else ''} - {members}"

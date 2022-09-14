"""$to signal"""
import math
import discord
import numpy as np

from offthedialbot import utils


class ToSignal(utils.Command):

    @classmethod
    @utils.deco.require_role("Staff")
    async def main(cls, ctx):
        """Distribute signal strength for all of the teams of the tournament."""
        async with ctx.typing():
            tourney = utils.Tournament()
            members_list = []
            # Create a :list: of brackets (:list:) of tuples (<Team Name>, <Signal Strength>)
            all_standings = await tourney.get_standings()
            for total, teams in all_standings:
                # Loop over each bracket individually
                team_ss = [
                    (team["name"], cls.calculate_gain(total, team["placement"]))
                    for team in teams
                ]
                # Parse into member_ss and distribute
                member_ss = cls.get_member_ss(ctx, team_ss)
                cls.distribute_ss(member_ss)
                members_list.extend(cls.list_members(member_ss))
        await utils.Alert(ctx, utils.Alert.Style.SUCCESS,
            title="Signal strength has been distributed:",
            description="\n".join(members_list[0]))
        if len(members_list) > 1:
                for chunk in members_list[1:]:
                    await ctx.send(embed=discord.Embed(description="\n".join(chunk), color=utils.Alert.Style.SUCCESS))

    @classmethod
    def get_member_ss(cls, ctx, team_ss):
        """Return a :list: of tuples of (<discord.Member>: <Signal Strength>) from Team SS."""

        member_ss = []
        for team, signal in team_ss:
            role = discord.utils.get(ctx.guild.roles, name=team)
            if not role:
                raise utils.exc.CommandCancel(
                    title=f"Unable to get role for team: `{team}`",
                    description=f"Make sure the team name and role name match")
            # Append (member, signal) for each member in the team role
            for member in role.members:
                member_ss.append((member, signal))

        return member_ss

    @classmethod
    def distribute_ss(cls, member_ss):
        for member, signal in member_ss:
            user = utils.User(member.id)
            user.increment_ss(signal)

    @staticmethod
    def calculate_gain(total, placement):
        """Calculate the total signal strength to add based on the total teams and placement."""
        return round(100 + ((total - (placement - 1)) * (100 / (total))), 1)

    @classmethod
    def list_members(cls, member_ss):
        """Return a list of chunks of members."""
        full_members_list = "".join(cls.format_members(member_ss))
        chunks = math.ceil(len(full_members_list) / 2000)
        return [
            cls.format_members(chunk)
            for chunk in np.array_split(member_ss, chunks)
        ]

    @staticmethod
    def format_members(member_ss):
        return [f"{member.mention}: `+{signal}`" for member, signal in member_ss]

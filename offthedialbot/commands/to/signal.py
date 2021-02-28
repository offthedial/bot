"""$to signal"""
import discord

from offthedialbot import utils


class ToSignal(utils.Command):

    @classmethod
    @utils.deco.require_role("Staff")
    async def main(cls, ctx):
        """Distribute signal strength for all of the teams of the tournament."""
        async with ctx.typing():
            tourney = utils.Tournament()
            # Create a :list: of tuples of (<Team Name>, <Signal Strength>)
            total, teams = await tourney.get_standings()
            team_ss = [
                (team["name"], cls.calculate_gain(total, team["placement"]))
                for team in teams
            ]
            # Parse into member_ss and distribute
            member_ss = cls.get_member_ss(ctx, team_ss)
            cls.distribute_ss(member_ss)
        await utils.Alert(ctx, utils.Alert.Style.SUCCESS,
            title="Signal strength has been distributed:",
            description="\n".join([f"<@{id}>: `+{signal}`" for id, signal in member_ss]))

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
                member_ss.append((member.id, signal))

        return member_ss

    @classmethod
    def distribute_ss(cls, member_ss):
        for id, signal in member_ss:
            user = utils.User(id)
            user.increment_ss(signal)

    @staticmethod
    def calculate_gain(total, placement):
        """Calculate the total signal strength to add based on the total teams and placement."""
        return round(100 + ((total - (placement - 1)) * (100 / (total))), 1)

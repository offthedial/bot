"""$to signal"""
import math
import discord
import numpy as np

from offthedialbot import utils


class ToSignal(utils.Command):

    # Flat bonus on top of the swiss score, by top cut placement
    TOP_CUT = {1: 100, 2: 50, 3: 25}

    @classmethod
    @utils.deco.require_role("Staff")
    async def main(cls, ctx):
        """Distribute signal strength for all of the teams of the tournament."""
        async with ctx.typing():
            tourney = utils.Tournament()
            sendou_id = tourney.dict["sendouId"]

            teams = {
                team["id"]: team
                for team in await utils.sendou.teams(sendou_id, ctx=ctx)
            }

            # Total each team's gain across their division's brackets.
            gains: dict[int, float] = {}
            for idx, bracket in enumerate(tourney.brackets()):
                result = await utils.sendou.standings(sendou_id, idx, ctx=ctx)
                total = len(result["standings"])
                for standing in result["standings"]:
                    gain = (
                        cls.calculate_gain(total=total, placement=standing["placement"])
                        if bracket["type"] == "swiss"
                        else cls.TOP_CUT.get(standing["placement"], 0))
                    gains[standing["tournamentTeamId"]] = gains.get(standing["tournamentTeamId"], 0) + gain

            # Distribute signal strength for each team
            members_list: list[tuple] = []
            missing: list[str] = []
            for team_id, gain in gains.items():
                if not (team := teams.get(team_id)):
                    continue
                for member, name in cls.get_team_members(ctx, team):
                    if member is None:
                        missing.append(f'`{name}` ({team["name"]})')
                        continue
                    members_list.append((member, round(gain, 1)))
            cls.distribute_ss(members_list)

        if not members_list:
            raise utils.exc.CommandCancel(
                title="No signal strength to distribute",
                description="No standings were found, or none of the placed players are in the server.")

        formatted = cls.format_members(members_list)
        await utils.Alert(ctx, utils.Alert.Style.SUCCESS,
            title="Signal strength has been distributed:",
            description="\n".join(formatted[0]))
        if len(formatted) > 1:
                for chunk in formatted[1:]:
                    await ctx.send(embed=discord.Embed(description="\n".join(chunk), color=utils.Alert.Style.SUCCESS))
        if missing:
            await utils.Alert(ctx, utils.Alert.Style.WARNING,
                title="Skipped - not in the server:",
                description="\n".join(f"`-` {entry}" for entry in missing))

    @staticmethod
    def calculate_gain(total, placement):
        """Calculate the total signal strength to add based on the total teams and placement. Final multiplier is the additional signal strength multiplier. For regular season, set to 1"""
        return round((100 + ((total - (placement - 1)) * (100 / (total))))*1, 1)

    @classmethod
    def get_team_members(cls, ctx, team):
        return [
            (ctx.guild.get_member(int(member["discordId"])), member["name"])
            for member in team["members"]
        ]

    @classmethod
    def distribute_ss(cls, members_list):
        for member, signal in members_list:
            user = utils.User(member.id)
            user.increment_ss(signal)

    @classmethod
    def format_members(cls, members_list):
        """Return a list of chunks of members from members_list."""
        total_chars = len("".join([f"{member.mention}: `+{signal}`" for member, signal in members_list]))
        num_chunks = math.ceil(total_chars / 2000)
        return [
            [f"{member.mention}: `+{signal}`" for member, signal in chunk]
            for chunk in np.array_split(members_list, num_chunks)
        ]

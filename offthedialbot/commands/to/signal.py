"""$to signal"""
import math
import discord
import numpy as np

from offthedialbot import utils


class ToSignal(utils.Command):

    @classmethod
    @utils.deco.require_role("Staff")
    async def main(cls, ctx, event_name: str = None):
        """Distribute signal strength for all of the teams of the tournament."""
        async with ctx.typing():
            tourney = utils.Tournament()

            # Create a :list: of brackets (:list:) of tuples (<Team Name>, <Signal Strength>)
            q = """
            events {
              name
              numEntrants
              standings(query: {perPage: 500}) {
                nodes {
                  placement
                  entrant {
                    name
                  }
                }
              }
            }
            """
            data = await tourney.query_smashgg(tourney.dict["slug"], q)
            events = [{
                "event": event["name"],
                "total": event["numEntrants"],
                "standings": [{
                    "team": node["entrant"]["name"],
                    "placement": node["placement"],
                } for node in event["standings"]["nodes"]]
            } for event in data["events"]]

            # If event if specified, filter to event
            if event_name:
                selected = list(filter(lambda s: s["event"] == event_name, events))
                if not len(selected):
                    raise utils.exc.CommandCancel(
                        title="Invalid event name",
                        description=
                            "Make sure the event name matches exactly. If it has spaces, make sure that you wrap the name in quotations.\n\n" +
                            "**Events:**\n" +
                            "\n".join(list(map(lambda e: f'> - `"{e["event"]}"`', events))))
                events = selected

            # Distribute signal strength for each standing
            members_list: list[tuple] = []
            for event in events:
                for standing in event["standings"]:
                    gain = cls.calculate_gain(total=event["total"], placement=standing["placement"])
                    members = cls.get_team_members(ctx, standing["team"])
                    for member in members:
                        members_list.append((member, gain))
            cls.distribute_ss(members_list)

        formatted = cls.format_members(members_list)
        await utils.Alert(ctx, utils.Alert.Style.SUCCESS,
            title="Signal strength has been distributed:",
            description="\n".join(formatted[0]))
        if len(formatted) > 1:
                for chunk in formatted[1:]:
                    await ctx.send(embed=discord.Embed(description="\n".join(chunk), color=utils.Alert.Style.SUCCESS))

    @staticmethod
    def calculate_gain(total, placement):
        """Calculate the total signal strength to add based on the total teams and placement."""
        return round(100 + ((total - (placement - 1)) * (100 / (total))), 1)

    @classmethod
    def get_team_members(cls, ctx, team):
        """Return a list of members for a team."""
        team_role = discord.utils.get(ctx.guild.roles, name=team)
        if not team_role:
            raise utils.exc.CommandCancel(
                title=f"Unable to get role for team: `{team}`",
                description=f"Make sure the team name and role name match")
        return team_role.members

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

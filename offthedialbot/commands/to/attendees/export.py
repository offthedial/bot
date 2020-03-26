"""$to attendees export"""
import csv
from io import StringIO

import discord

from offthedialbot import utils
from . import attendee_and_profile


@utils.deco.require_role("Organiser")
@utils.deco.tourney()
async def main(ctx):
    """Export attendee profiles to a csv."""
    await ctx.trigger_typing()
    await export_attendees(ctx, attendee_and_profile(ctx))


async def export_attendees(ctx, rows):
    """Create and send attendees csv."""
    file = create_file(ctx, rows)
    await send_file(ctx, file)


def create_file(ctx, rows):
    """Create StringIO file."""
    file = StringIO()
    writer: csv.writer = csv.writer(file)
    csv_profiles = []

    for attendee, profile in rows:
        sw = profile.get_sw()
        csv_profiles.append([
            f'@{attendee.name}#{attendee.discriminator}' if attendee else "NOT-FOUND",
            profile.get_ign(),
            f"SW-{sw[:4]}-{sw[4:8]}-{sw[8:]}",
            *[profile.convert_rank_power(rank) for rank in profile.get_ranks().values()],
            profile.calculate_elo(),
            profile.get_stylepoints(),
            profile.get_cxp(),
            profile.get_ss(),
            profile.get_banned(),
            profile.get_reg(),
            profile.get_reg('code'),
            f"<@{profile.get_id()}>"
        ])
    csv_profiles.sort(key=lambda row: row[7])

    writer.writerows([["Discord Mention", "IGN", "SW", "SZ", "TC", "RM", "CB", "Cumulative ELO", "Stylepoints", "CXP",
                       "Signal Strength", "Banned", "Competing", "Confirmation Code", "Discord ID"], []] + csv_profiles)
    file.seek(0)
    return discord.File(file, filename="profiles.csv")


async def send_file(ctx, file):
    """Send an alert and upload the file to discord."""
    await utils.Alert(ctx, utils.Alert.Style.SUCCESS,
        title=":incoming_envelope: *Exporting attendees complete!*",
        description="Download the spreadsheet below. \U0001f4e5")
    await ctx.send(file=file)

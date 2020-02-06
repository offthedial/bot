"""$to profiles"""
import csv
from io import StringIO

import discord

from offthedialbot import utils


async def main(ctx):
    """Export user profiles to a csv."""
    ui: utils.CommandUI = await utils.CommandUI(ctx, create_embed(), moderator=True)
    reply, _ = await ui.get_reply("reaction_add", valid_reactions=['\U0001f4e9', '\U0001f3c5'])

    profiles: list = {
        '\U0001f4e9': lambda: utils.dbh.find_many_profiles({}),
        '\U0001f3c5': lambda: utils.dbh.find_many_profiles({"meta.competing": True})
    }[reply.emoji]()

    await ui.ctx.trigger_typing()

    file = create_file(ui, profiles)
    await upload_file(ui, file)

    await ui.end(status=None)


def create_embed():
    """Create embed."""
    return discord.Embed(
        title="Do you want all profiles or just those competing?",
        description="Select \U0001f4e9 for all, and \U0001f3c5 for just those competing."
    )


def create_file(ui: utils.CommandUI, profiles: list):
    """Create StringIO file."""
    file = StringIO()
    writer: csv.writer = csv.writer(file)
    csv_profiles = []

    for profile in profiles:
        profile = utils.Profile(profile)
        user = ui.ctx.bot.get_user(profile.get_id())

        csv_profiles.append([
            f'@{user.name}#{user.discriminator}',
            profile.get_status("IGN"),
            profile.get_status("SW"),
            *[profile.convert_rank_power(rank) for rank in profile.get_ranks().values()],
            profile.calculate_elo(),
            profile.get_stylepoints(),
            profile.get_cxp(),
            profile.is_competing(),
            profile.get_signal_strength(),
            profile.is_banned(),
            str(profile.get_id())
        ])

    writer.writerows([["Discord Mention", "IGN", "SW", "SZ", "RM", "TC", "CB", "Cumulative ELO", "Stylepoints", "CXP",
                       "Competing", "Signal Strength", "Droppout Ban", "Discord ID"], []] + csv_profiles)

    file.seek(0)
    return file


async def upload_file(ui: utils.CommandUI, file: StringIO):
    """Upload csv file to discord."""
    await ui.ctx.send(embed=utils.Alert.create_embed(
        utils.Alert.Style.SUCCESS,
        title=":incoming_envelope: *Exporting profiles complete!*",
        description="Download the spreadsheet below. \U0001f4e5"
    ))
    await ui.ctx.send(file=discord.File(file, filename="profiles.csv"))

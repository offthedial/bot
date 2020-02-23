"""$to attendees export"""
import csv
from io import StringIO

import discord

from offthedialbot import utils


@utils.deco.require_role("Organiser")
@utils.deco.tourney()
async def main(ctx):
    """Export user profiles to a csv."""
    ui: utils.CommandUI = await utils.CommandUI(ctx, create_embed())
    reply = await ui.get_reply("reaction_add", valid_reactions=['\U0001f4e9', '\U0001f3c5'])
    query = {
        '\U0001f4e9': {},
        '\U0001f3c5': {"meta.competing": True}
    }[reply.emoji]

    await export_profiles(ui, query)


async def export_profiles(ui, query):
    """Export user profiles."""
    profiles: list = utils.dbh.profiles.find(query, {"_id": True})
    await ui.ctx.trigger_typing()
    file = create_file(ui, profiles)
    await upload_file(ui, file)


def create_embed():
    """Create embed."""
    return discord.Embed(
        title="Do you want all profiles or just those competing?",
        description="Select \U0001f4e9 for all, and \U0001f3c5 for just those competing.",
        color=utils.colors.Roles.COMPETING
    )


def create_file(ui: utils.CommandUI, profiles: list):
    """Create StringIO file."""
    file = StringIO()
    writer: csv.writer = csv.writer(file)
    csv_profiles = []

    for profile in profiles:
        user = ui.ctx.bot.get_user(profile["_id"])
        profile = utils.Profile(profile["_id"])

        csv_profiles.append([
            f'@{user.name}#{user.discriminator}',
            profile.get_status()["IGN"],
            f"'{profile.get_status()['SW']}'",
            *[profile.convert_rank_power(rank) for rank in profile.get_ranks().values()],
            profile.calculate_elo(),
            profile.get_stylepoints(),
            profile.get_cxp(),
            profile.get_competing(),
            profile.get_ss(),
            profile.get_banned(),
            f"'{user.id}'"
        ])

    writer.writerows([["Discord Mention", "IGN", "SW", "SZ", "RM", "TC", "CB", "Cumulative ELO", "Stylepoints", "CXP",
                       "Competing", "Signal Strength", "Droppout Ban", "Discord ID"], []] + csv_profiles)
    file.seek(0)
    return file


async def upload_file(ui: utils.CommandUI, file: StringIO):
    """Upload csv file to discord."""
    alert = utils.Alert.create_embed(
        utils.Alert.Style.SUCCESS,
        title=":incoming_envelope: *Exporting profiles complete!*",
        description="Download the spreadsheet below. \U0001f4e5"
    )
    ui.embed.title, ui.embed.description, ui.embed.color = alert.title, alert.description, alert.color
    await ui.ctx.send(file=discord.File(file, filename="profiles.csv"))
    await ui.ui.clear_reactions()
    await ui.update()

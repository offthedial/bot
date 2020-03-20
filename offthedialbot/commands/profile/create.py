"""$profile create"""
import asyncio
import re

import discord

from offthedialbot import utils
from . import create_status_embed, display_field


@utils.deco.profile_required(reverse=True)
async def main(ctx):
    """Create your profile."""
    profile: utils.Profile = utils.Profile(ctx.author.id, new=True)

    embed: discord.Embed = create_status_embed(ctx.author.display_name, profile)
    ui: utils.CommandUI = await utils.CommandUI(ctx, embed)

    profile = await set_user_status(ui, profile)
    ui.embed = create_stylepoints_embed(ui.ctx)
    profile.set_stylepoints(await get_user_stylepoints(ui))
    ui.embed = create_cxp_embed(ui.ctx)
    profile.set_cxp(await get_user_cxp(ui))
    profile.write()
    await ui.end(True)


async def set_user_status(ui: utils.CommandUI, profile: utils.Profile) -> utils.Profile:
    """Get valid message for each rank."""
    for index, key in enumerate(profile.get_status().keys()):
        clean_status_key(profile, key)

        if key != "Ranks":
            await set_status_field(ui, profile, key, index)
        else:
            await set_rank_field(ui, profile, index)

    if not await confirm_profile(ui):
        profile: utils.Profile = utils.Profile(ui.ctx.author.id, new=True)
        ui.embed = create_status_embed(ui.ctx.author.display_name, profile)
        profile: utils.Profile = await set_user_status(ui, profile)

    return profile


async def set_status_field(ui, profile, key, field_index) -> None:
    """Prompt the user for a standard user profile field."""
    instructions = {"IGN": 'Enter your **IGN**, `(WP*Zada, Lepto)`', "SW": 'Enter your **SW**, `(SW-0000-0000-0000)`'}
    ui.embed.title = instructions[key]
    reply = await ui.get_valid_message(
        valid=lambda m: parse_reply(key, m.content), error_fields={
            "title": f"Invalid {key}",
            "description": instructions[key]
        })
    field_value: str = parse_reply(key, reply.content)
    profile.set_status(key, field_value)
    ui.embed.set_field_at(field_index, name=key, value=display_field(key, field_value))


async def set_rank_field(ui: utils.CommandUI, profile: utils.Profile, field_index: int) -> None:
    """Prompt the user for each of the rank fields."""
    instructions = lambda k: f'Enter your **__{k}__ Rank**, `(C, A-, S+0, X2350.0)`'
    for key in profile.get_ranks().keys():
        ui.embed.title = instructions(key)
        reply: discord.Message = await ui.get_valid_message(
            valid=lambda m: parse_reply("Ranks", m.content),
            error_fields={
                "title": "Invalid Rank",
                "description": instructions(key)
            })
        profile.set_rank(key, parse_reply("Ranks", reply.content))
        ui.embed.set_field_at(field_index,
            name="Ranks",
            value=display_field("Ranks", profile.get_ranks()), inline=False)


def clean_status_key(profile: utils.Profile, key: str) -> tuple:
    """Clean status at key, return new value."""
    clean_status = {
        "IGN": None,
        "SW": None,
        "Ranks": {
            "Splat Zones": None,
            "Rainmaker": None,
            "Tower Control": None,
            "Clam Blitz": None,
        },
    }
    profile.set_status(key, clean_status[key])
    return key, profile.get_status()[key]


async def get_user_stylepoints(ui: utils.CommandUI) -> list:
    """Get the user's playstyle and calculate their, style points."""
    user_playstyles: list = []
    create_tasks = (
        lambda: asyncio.create_task(ui.get_valid_message(
            lambda m: m.content.lower() in utils.Profile.playstyles.keys(),
            {"title": "Invalid Playstyle.", "description": "Please enter a valid playstyle."}, cancel=False)),
        lambda: asyncio.create_task(ui.get_valid_reaction(['\u23ed\ufe0f'], cancel=False)),
        lambda: ui.create_cancel_task()
    )
    while True:
        tasks = [task() for task in create_tasks]
        ui.embed.set_field_at(0, name="Playstyles", value=create_playstyle_list(user_playstyles))
        task, reply = await ui.wait_tasks(tasks)
        await ui.delete_alert()

        if task == tasks[0]:
            content: str = reply.content.lower()
            user_playstyles.remove(content) if content in user_playstyles else user_playstyles.append(content)
        elif task == tasks[1]:
            if not user_playstyles:
                await ui.create_alert(utils.Alert.Style.DANGER,
                    title="No Playstyles Selected",
                    description="You did not select any playstyles.")
            else:
                break
        else:
            await ui.end(False)

    return user_playstyles


async def get_user_cxp(ui: utils.CommandUI) -> int:
    """Get the user's playstyle and calculate their, style points."""
    reply: discord.Message = await ui.get_valid_message(r'^\d+$',
        {"title": "Invalid number.", "description": "Please enter a valid number of tournaments."})
    return int(reply.content)


def create_stylepoints_embed(ctx) -> discord.Embed:
    """Create embed for asking stylepoints."""
    embed: discord.Embed = discord.Embed(color=utils.colors.DIALER,
        title="Enter all of the playstyles below that apply to you",
        description=f"Re-enter a playstyle to remove it. Click the \u23ed\ufe0f when done.")
    embed.add_field(name="Playstyles", value=create_playstyle_list())
    return embed


def create_cxp_embed(ctx) -> discord.Embed:
    """Create embed for asking competitive experience."""
    return discord.Embed(color=utils.colors.DIALER,
        title=f"How many tournaments, with at-least 16 teams, have your competed in?")


async def confirm_profile(ui) -> bool:
    """Confirms user profile and returns status."""
    alert_embed: discord.Embed = utils.Alert.create_embed(utils.Alert.Style.WARNING,
        title="Confirm?",
        description="To confirm your profile, react with \u2611\ufe0f. To reenter your profile, react with \u23ea.")
    ui.embed.title, ui.embed.description, ui.embed.color = alert_embed.title, alert_embed.description, alert_embed.color
    reply = await ui.get_valid_reaction(['\u2611\ufe0f', '\u23ea'])
    return reply.emoji == '\u2611\ufe0f'


def parse_reply(key, value):
    """Check if reply is valid for the key, return cleaned reply, or false in invalid."""
    if key == "IGN":
        return value if 1 <= len(value) <= 10 else False
    elif key == "SW":
        value: str = re.sub(r"[\D]", "", value)
        return value if len(value) == 12 else False
    elif key == "Ranks":
        value = value.upper()
        if value in {"C-", "C", "C+", "B-", "B", "B+", "A-", "A", "A+", "S", "X"}:  # Standard rank, or default X
            return utils.Profile.convert_rank_power(value) if value != "X" else 2000.0
        elif re.search(r"(^S\+\d$)|(^X[1-9]\d{3}(\.\d)?$)", value.upper()):  # S+ or X(power)
            return utils.Profile.convert_rank_power(value)

    return False


def create_playstyle_list(profile_playstyles=()) -> str:
    """Create the list of playstyles based on the current profiles."""
    set_checkmark = lambda p: '\u2705' if p in profile_playstyles else '\U0001f7e9'
    return "\n".join([f'{set_checkmark(playstyle)} {playstyle.capitalize()}' for playstyle in utils.Profile.playstyles])

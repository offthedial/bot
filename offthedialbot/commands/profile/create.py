import asyncio
import re

import discord

import utils
from . import create_status_embed, check_for_profile, display_field


async def main(ctx):
    """Run command for $profile create."""
    await check_for_profile(ctx, reverse=True)
    profile: utils.Profile = utils.Profile()

    embed: discord.Embed = create_status_embed(ctx.author.display_name, profile)
    ui: utils.CommandUI = await utils.CommandUI(ctx, embed)

    profile = await set_user_status(ui, profile)
    profile.set_stylepoints(await get_user_stylepoints(ui))
    profile.set_cxp(await get_user_cxp(ui))
    utils.dbh.new_profile(profile.dict(), ui.ctx.author.id)
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
        profile: utils.Profile = utils.Profile()
        ui.embed = create_status_embed(ui.ctx.author.display_name, profile)
        profile: utils.Profile = await set_user_status(ui, profile)

    return profile


async def get_user_stylepoints(ui: utils.CommandUI) -> list:
    """Get the user's playstyle and calculate their, style points."""
    ui.embed = create_stylepoints_embed(ui.ctx)
    error_fields: dict = {"title": "Invalid Playstyle.", "description": "Please enter a valid playstyle."}

    coros: list = [
        lambda: ui.get_valid_message(lambda r: r.lower() in utils.Profile.playstyles.keys(), error_fields),
        lambda: ui.get_reply('reaction_add', valid_reactions=['\u23ed\ufe0f'], cancel=False)
    ]
    return await wait_user_playstyles(ui, coros)  # Check if user has selected atleast 1 of the 3


def create_stylepoints_embed(ctx):
    """Create embed for asking stylepoints."""
    embed: discord.Embed = discord.Embed(
        title=f"{ctx.author.display_name}'s Style Points",
        description=
        f"Type all of the playstyles below that apply to you, Type it again to remove it.\nClick the \u23ed\ufe0f when done.",
        color=utils.colors.Roles.DIALER
    )
    embed.add_field(name="Playstyles", value=create_playstyle_list())
    return embed


async def get_user_cxp(ui: utils.CommandUI) -> int:
    """Get the user's playstyle and calculate their, style points."""
    ui.embed = create_cxp_embed(ui.ctx)
    error_fields: dict = {"title": "Invalid number.", "description": "Please enter a valid number of tournaments."}
    reply: discord.Message = await ui.get_valid_message(r'^\d+$', error_fields)
    return int(reply.content)


def create_cxp_embed(ctx) -> discord.Embed:
    """Create embed for asking competitive experience."""
    return discord.Embed(
        title=f"{ctx.author.display_name}'s Competitive Experience",
        description=f"How many tournaments with >= 16 teams have your competed in?",
        color=utils.colors.Roles.DIALER
    )


async def set_status_field(ui, profile, key, field_index) -> None:
    """Prompt the user for a standard user profile field."""
    instructions = {
        "IGN": 'Please type a valid **IGN**, `(WP*Zada, Lepto)`',
        "SW": 'Please type a valid **SW**, `(SW-1111-1111-1111)`',
    }
    ui.embed.description = instructions[key]
    reply = await ui.get_valid_message(
        valid=lambda r: parse_reply(key, r), error_fields={
            "title": f"Invalid {key}",
            "description": instructions[key]
        }
    )
    field_value: str = profile.set_status_key(key, parse_reply(key, reply.content))
    ui.embed.set_field_at(field_index, name=key, value=display_field(key, field_value))


async def set_rank_field(ui: utils.CommandUI, profile: utils.Profile, field_index: int) -> None:
    """Prompt the user for each of the rank fields."""
    create_instructions = lambda k: f'Please type a valid **__{k}__ Rank**, `(C, A-, S+0, X2350.0)`'
    for key in profile.get_ranks().keys():
        ui.embed.description = create_instructions(key)
        reply: discord.Message = await ui.get_valid_message(
            valid=lambda r: parse_reply("Ranks", r),
            error_fields={
                "title": "Invalid Rank",
                "description": create_instructions(key)
            }
        )
        profile.set_rank(key, parse_reply("Ranks", reply.content))
        ui.embed.set_field_at(
            field_index,
            name="Ranks",
            value=display_field("Ranks", profile.get_ranks()),
            inline=False
        )


def clean_status_key(profile: utils.Profile, key: str):
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
    value = profile.set_status_key(key, clean_status[key])
    return key, value


def parse_reply(key, value):
    """Check if reply is valid for the key, return cleaned reply, or false in invalid."""
    if key == "IGN":
        return value if 1 <= len(value) <= 10 else False
    elif key == "SW":
        value: str = re.sub(r"[\D]", "", value)
        return int(value) if len(value) == 12 and value[0] != "0" else False
    elif key == "Ranks":
        value = value.upper()
        if value in {"C-", "C", "C+", "B-", "B", "B+", "A-", "A", "A+", "S", "X"}:  # Standard rank, or default X
            return utils.Profile.convert_rank_power(value) if value != "X" else 2000.0
        elif re.search(r"(^S\+\d$)|(^X[1-9]\d{3}(\.\d)?$)", value.upper()):  # S+ or X(power)
            return utils.Profile.convert_rank_power(value)

    return False


async def wait_user_playstyles(ui, coros) -> list:
    """Constantly wait for the user to input playstyles."""
    user_playstyles: list = []

    complete = False
    while not complete:
        tasks: list = [asyncio.create_task(coro()) for coro in coros]
        task, reply = await ui.wait_tasks(tasks)

        if task == tasks[0]:
            content: str = reply.content.lower()

            if content not in user_playstyles:
                user_playstyles.append(content)
            else:
                user_playstyles.remove(content)
        else:
            complete: bool = True
        ui.embed.set_field_at(0, name="Playstyles", value=create_playstyle_list(user_playstyles))

    return user_playstyles


async def confirm_profile(ui) -> bool:
    """Confirms user profile and returns status."""
    alert_embed: discord.Embed = utils.Alert.create_embed(utils.Alert.Style.WARNING, title="Confirm?", description="To confirm your profile, react with \u2611\ufe0f. To reenter your profile, react with \u23ea.")
    ui.embed.title, ui.embed.description, ui.embed.color = alert_embed.title, alert_embed.description, alert_embed.color
    reply = await ui.get_reply("reaction_add", valid_reactions=['\u2611\ufe0f', '\u23ea'])
    return reply[0].emoji == '\u2611\ufe0f'


def create_playstyle_list(profile_playstyles=()) -> str:
    """Create the list of playstyles based on the current profiles."""
    set_checkmark = lambda p: '\u2705' if p in profile_playstyles else '\U0001f7e9'
    return "\n".join([f'{set_checkmark(playstyle)} {playstyle.capitalize()}' for playstyle in utils.Profile.playstyles])

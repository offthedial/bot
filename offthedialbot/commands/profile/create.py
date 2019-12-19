import asyncio
import re

import discord

import utils
from . import convert_rank_power


async def main(ctx):
    """Run command for $profile create."""
    if utils.dbh.find_profile(id=ctx.author.id):  # If profile already exists
        await utils.Alert(
            ctx,
            utils.Alert.Style.DANGER,
            title="Existing profile found.",
            description="You have already created a profile!"
        )
        raise utils.exc.CommandCancel

    profile = {
        "status": {
            "IGN": None,
            "SW": None,
            "Ranks": {
                "Splat Zones": None,
                "Rainmaker": None,
                "Tower Control": None,
                "Clam Blitz": None,
            },
        },
        "style_points": [],  # Groups A, B, and C.
        "cxp": 0,
        "meta": {
            "currently_competing": False,
            "previous_tourneys": [],
            # "dropout_ban": None,
        }
    }

    embed = create_embed(ctx.author.display_name, profile)
    ui = await utils.CommandUI(ctx, embed)

    await set_user_status(ui, profile)
    profile["style_points"] = await get_user_playstyles(ui)
    profile["cxp"] = await get_user_cxp(ui)

    utils.dbh.new_profile(profile, ctx.author.id)
    await ui.end(status=True)


def create_embed(name, profile):
    """Create profile embed to display user profile."""
    embed = discord.Embed(title=f"{name}'s Status", color=utils.colors.Roles.DIALER)

    for key in profile["status"].keys():
        if key != "Ranks":
            value = f"*`pending`*"
        else:  # key == "Ranks":
            value = "\n".join([f'**{subkey}:** *`pending`*' for subkey in profile["status"]["Ranks"].keys()])
        embed.add_field(name=key, value=value, inline=True if key != "Ranks" else False)

    return embed


async def set_user_status(ui, profile):
    """Get valid message for each rank."""
    for key in profile["status"].keys():

        if key != "Ranks":
            await set_status_field(ui, profile, key)
        else:
            await set_rank_field(ui, profile)


async def get_user_playstyles(ui):
    """Get the user's playstyle and calculate their, style points."""
    playstyles = {
        "frontline": (0, 0, 0),
        "midline": (0, 0, 0),
        "backline": (0, 0, 0),
        "flex": (0, 0, 0),
        "slayer": (0, 0, 0),
        "defensive": (0, 0, 0),
        "objective": (0, 0, 0),
        "support": (0, 0, 0),
    }
    ui.embed = discord.Embed(
        title=f"{ui.ctx.author.display_name}'s Style Points",
        description=
        f"Type all of the playstyles below that apply to you, Type it again to remove it.\nClick the \u23ed\ufe0f when done.",
        color=utils.colors.Roles.DIALER
    )
    ui.embed.add_field(name="Playstyles", value=create_playstyle_list(playstyles))
    error_fields = {"title": "Invalid Playstyle.", "description": "Please enter a valid playstyle."}

    coros = [
        lambda: ui.get_valid_message(lambda r: r.lower() in playstyles.keys(), error_fields),
        lambda: ui.get_reply('reaction_add', valid_reactions=['\u23ed\ufe0f'], cancel=False)
    ]
    return await wait_user_playstyles(ui, coros, playstyles)  # Check if user has selected atleast 1 of the 3


async def get_user_cxp(ui):
    """Get the user's playstyle and calculate their, style points."""
    ui.embed = discord.Embed(
        title=f"{ui.ctx.author.display_name}'s Competitive Experience",
        description=f"How many tournaments with >= 16 teams have your competed in?",
        color=utils.colors.Roles.DIALER
    )
    error_fields = {"title": "Invalid number.", "description": "Please enter a valid number of tournaments."}
    reply = await ui.get_valid_message(r'^\d+$', error_fields)
    return int(reply.content)


async def set_status_field(ui, profile, key):
    """Prompt the user for a standard user profile field."""
    instructions = {
        "IGN": 'Please type a valid **IGN**, `(WP*Zada, Lepto)`',
        "SW": 'Please type a valid **SW**, `(0000-0000-0000)`',
    }
    field_index = {"IGN": 0, "SW": 1}
    ui.embed.description = instructions[key]
    reply = await ui.get_valid_message(
        valid=lambda r: parse_reply(key, r), error_fields={
            "title": f"Invalid {key}",
            "description": instructions[key]
        }
    )
    profile["status"][key] = parse_reply(key, reply.content)
    ui.embed.set_field_at(field_index[key], name=key, value=f'`{profile["status"][key]}`')


async def set_rank_field(ui, profile):
    """Prompt the user for each of the rank fields."""
    create_instructions = lambda k: f'Please type a valid **__{k}__ Rank**, `(C, A-, S+0, X2350.0)`'
    for key in profile["status"]["Ranks"].keys():
        ui.embed.description = create_instructions(key)
        reply = await ui.get_valid_message(
            valid=lambda r: parse_reply("Ranks", r),
            error_fields={
                "title": "Invalid Rank",
                "description": create_instructions(key)
            }
        )
        profile["status"]["Ranks"][key] = parse_reply("Ranks", reply.content)
        ui.embed.set_field_at(
            2,
            name="Ranks",
            value="\n".join(
                [
                    f"**{subkey}:** {(f'`{convert_rank_power(subvalue)}`' if subvalue else '*`pending`*')}"
                    for subkey, subvalue in profile["status"]["Ranks"].items()
                ]
            ),
            inline=False
        )


def create_playstyle_list(playstyles, profile_playstyles=()):
    """Create the list of playstyles based on the current profiles."""
    _ = lambda p: '\u2705' if p in profile_playstyles else '\U0001f7e9'
    return "\n".join([f'{_(playstyle)} {playstyle.capitalize()}' for playstyle in playstyles])


async def wait_user_playstyles(ui, coros, playstyles):
    """Constantly wait for the user to input playstyles."""
    user_playstyles = []

    complete = False
    while not complete:
        tasks = [asyncio.create_task(coro()) for coro in coros]
        task, reply = await ui.wait_tasks(tasks)

        if task == tasks[0]:
            content = reply.content.lower()

            if content not in user_playstyles:
                user_playstyles.append(content)
            else:
                user_playstyles.remove(content)
        else:
            complete = True
        ui.embed.set_field_at(0, name="Playstyles", value=create_playstyle_list(playstyles, user_playstyles))

    return user_playstyles


def parse_reply(key, value):
    """Check if reply is valid for the key, return cleaned reply, or false in invalid."""
    if key == "IGN":
        return value if 1 <= len(value) <= 10 else False
    elif key == "SW":
        value = re.sub(r"[\D]", "", value)
        return value if len(value) == 12 else False
    elif key == "Ranks":
        value = value.upper()
        if value in {"C-", "C", "C+", "B-", "B", "B+", "A-", "A", "A+", "S", "X"}:  # Standard rank, or default X
            return convert_rank_power(value) if value != "X" else 2000.0
        elif re.search(r"(^S\+\d$)|(^X[1-9]\d{3}$)", value.upper()):  # S+ or X(power)
            return convert_rank_power(value)

    return False

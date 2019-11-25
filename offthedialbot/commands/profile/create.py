import asyncio
import re

import discord

import utils


async def main(ctx, arg):
    """This is all a test."""
    if utils.dbh.find_profile(id=ctx.author.id):  # If profile already exists
        await utils.Alert(
            ctx,
            utils.Alert.Colors.DANGER,
            title="Existing profile found.",
            description="You have already created a profile!"
        )
        raise utils.exc.CommandCancel

    profile = utils.dbh.empty_profile.copy()
    embed = create_status_embed(ctx, profile)

    ui = await utils.CommandUI(ctx, embed)

    await get_user_status(ctx, ui, profile)
    await get_user_playstyles(ctx, ui, profile)

    # utils.dbh.new_profile(profile, ctx.author.id)
    await ui.end(status=True)


async def get_user_status(ctx, ui, profile):
    """Get valid message for each rank."""
    for key in profile["status"].keys():

        if key != "Ranks":
            await get_profile_field(ui, profile, key)
        else:
            await get_rank_field(ui, profile)


async def get_user_playstyles(ctx, ui, profile):
    """Get the user's playstyle and calculate their, style points."""
    playstyles = {
        "frontline": (9, 0, 0),
        "midline": (0, 9, 0),
        "backline": (0, 0, 9),
        "aggressive/slayer": (2, 0, 0),
        "defensive": (0, 1, 2),
        "objective": (1, 1, 0),
        "support": (9, 1, 1),
        "flex": (1, 1, 1),
    }
    ui.embed = discord.Embed(
        title=f"{ctx.author.display_name}'s Style Points",
        description=f"Please type all of the playstyles that apply to you, click the \u2705 when done."
    )
    ui.embed.add_field(name="Playstyles", value="\n".join([playstyle.capitalize() for playstyle in playstyles]))
    error_fields = {"title": "Invalid Playstyle.", "description": "Please enter a valid playstyle."}

    coros = [
        lambda: ui.get_valid_message(lambda r: r.lower() in playstyles.keys(), error_fields),
        lambda: ui.get_reply('reaction_add', valid_reactions='\u2705', cancel=False)
    ]
    user_playstyles = await wait_user_playstyles(ctx, ui, coros)
    profile["style_points"] = calculate_style_points(user_playstyles, playstyles)


async def get_profile_field(ui, profile, key):
    """Prompt the user for a standard user profile field."""
    instructions = {
        "IGN": 'Please type a valid **IGN**, `(WP*Zada, Lepto)`',
        "SW": 'Please type a valid **SW**, `(0000-0000-0000)`',
    }
    ui.embed.description = instructions[key]
    reply = await ui.get_valid_message(
        valid=lambda r: parse_reply(key, r), error_fields={
            "title": f"Invalid {key}",
            "description": instructions[key]
        }
    )
    profile["status"][key] = parse_reply(key, reply.content)
    ui.embed.add_field(name=key, value=f'`{profile["status"][key]}`', inline=True)


async def get_rank_field(ui, profile):
    """Prompt the user for each of the rank fields."""
    create_instructions = lambda k: f'Please type a valid **__{k}__ Rank**, `(C, A-, S+0, X2350)`'

    ui.embed.add_field(name="Ranks", value="-------", inline=False)
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
        ui.embed.add_field(name=key, value=f'`{profile["status"]["Ranks"][key]}`', inline=True)


async def wait_user_playstyles(ctx, ui, coros):
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

    return user_playstyles


def calculate_style_points(user_playstyles, playstyles):
    """Calculate a user's style points given their playstyles."""
    style_points = [0, 0, 0]
    for playstyle in user_playstyles:
        style_points += [*playstyles[playstyle]]
        style_points = list(map(int.__add__, playstyles[playstyle], style_points))

    return style_points


def create_status_embed(ctx, profile):
    """Create embed for displaying user profile."""
    embed = discord.Embed(title=f"{ctx.author.display_name}'s Status:")
    return embed


def parse_reply(key, value):
    """Check if reply is valid for the key, return cleaned reply, or false in invalid."""
    if key == "IGN":
        return value if 1 <= len(value) <= 10 else False
    elif key == "SW":
        value = re.sub(r"[\D]", "", value)
        return value if len(value) == 12 else False
    elif key == "Ranks":
        # Standard rank, or default X
        if value.upper() in {"C-", "C", "C+", "B-", "B", "B+", "A-", "A", "A+", "S", "X"}:
            if value.upper() == "X":
                value = "X2000"
            return value.upper()
        # S+ or X(power)
        elif re.search(r"(^S\+\d$)|(^X[1-9]\d{3}$)", value.upper()):
            return value.upper()

    return False

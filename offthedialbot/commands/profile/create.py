import discord

import utils
import re


async def main(ctx, arg):
    """This is all a test."""
    if utils.dbh.find_profile(id=ctx.author.id):  # If profile already exists
        alert = utils.embeds.alert(
            utils.AlertStyle.DANGER, "Profile already exists", "Your profile already exists you dumb fuck"
        )
        await ctx.send(embed=alert)
        raise utils.exc.CommandCancel

    profile = utils.dbh.empty_profile.copy()
    embed = create_profile_embed(ctx, profile)

    ui = await utils.CommandUI(ctx, embed)

    await get_user_profile(ctx, ui, profile)
    await ui.end(status=True)


async def get_user_profile(ctx, ui, profile):
    """Get valid message for each rank."""
    for key in profile["status"].keys():

        if key != "Ranks":
            await get_standard_field(ui, profile, key)
        else:
            await get_rank_field(ui, profile)


async def get_standard_field(ui, profile, key):
    """Prompt the user for a the standard field."""
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
    ui.embed.add_field(name=key, value=f'`{profile["status"][key]}`')


async def get_rank_field(ui, profile):
    """Prompt the user for each of the rank fields."""
    create_instructions = lambda k: f'Please type a valid **__{k}__ Rank**, `(C, A-, S+0, X2350)`'

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
        ui.embed.add_field(name=key, value=f'`{profile["status"]["Ranks"][key]}`')


def create_profile_embed(ctx, profile):
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

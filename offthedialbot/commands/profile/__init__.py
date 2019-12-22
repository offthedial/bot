import discord

import utils


async def main(ctx):
    """Run command for $profile."""
    profile = await check_for_profile(ctx)
    embed = create_status_embed(ctx.author.display_name, profile)
    await ctx.send(embed=embed)


async def check_for_profile(ctx, reverse=False):
    """Returns profile if it exists, otherwise cancels command."""
    profile = utils.dbh.find_profile(id=ctx.author.id)
    if (result := {
        False: lambda p: (p is None, {"title": "No profile found.", "description": "You can create one using `$profile create`."}),
        True: lambda p: (p, {"title": "Existing profile found.", "description": "You can view your profile with `$profile`."}),
    }[reverse](profile))[0]:
        await utils.Alert(ctx, utils.Alert.Style.DANGER, **result[1])
        raise utils.exc.CommandCancel
    return profile


def create_status_embed(name, profile):
    """Create profile embed to display user profile."""
    embed = discord.Embed(title=f"{name}'s Status", color=utils.colors.Roles.DIALER)

    for key, value in profile["status"].items():
        value = display_field(key, value)
        embed.add_field(name=key, value=value, inline=True if key != "Ranks" else False)

    return embed


def display_field(key, field):
    """Displays each field in displayable format."""
    return {
        "IGN": lambda: f'`{field}`' if field else '*`pending`*',
        "SW": lambda: f"`SW-{str(field)[:4]}-{str(field)[4:8]}-{str(field)[8:]}`" if field is not None else '*`pending`*',
        "Ranks": lambda: "\n".join([f"**{k}:** {(f'`{convert_rank_power(v)}`' if v else '*`pending`*')}" for k, v in field.items()])
    }[key]()


def convert_rank_power(value):
    """Convert ranks to corresponding powers, and vice versa."""
    ranks = {
        "C-": 1000,
        "C": 1100,
        "C+": 1200,
        "B-": 1250,
        "B": 1450,
        "B+": 1550,
        "A-": 1650,
        "A": 1700,
        "A+": 1800,
        "S": 1900,
        "S+0": 2000,
        "S+1": 2080,
        "S+2": 2120,
        "S+3": 2160,
        "S+4": 2200,
        "S+5": 2230,
        "S+6": 2260,
        "S+7": 2290,
        "S+8": 2320,
        "S+9": 2350,
    }
    ranks.update({v: k for k, v in ranks.items()})

    if isinstance(value, float):
        return "X" + str(value)
    elif rank := ranks.get(value, None):
        return rank
    elif isinstance(value, str):
        return float(value[1:])

import discord

import utils


async def main(ctx):
    """Run command for $profile."""
    profile = utils.dbh.find_profile(id=ctx.author.id)
    if profile is None:
        await utils.Alert(
            ctx, utils.Alert.Style.DANGER, title="No profile found.", description="You don't have a profile."
        )
        raise utils.exc.CommandCancel

    embed = create_status_embed(ctx.author.display_name, profile)
    await ctx.send(embed=embed)


def create_status_embed(name, profile):
    """Create profile embed to display user profile."""
    embed = discord.Embed(title=f"{name}'s Status", color=utils.colors.Roles.DIALER)

    for key, value in profile["status"].items():
        if key != "Ranks":
            value = f'`{(value if key != "SW" else display_sw(value))}`'
        else:  # key == "Ranks":
            value = "\n".join(
                [f'**{subkey}:** `{convert_rank_power(subvalue)}`' for subkey, subvalue in
                 profile["status"]["Ranks"].items()]
            )
        embed.add_field(name=key, value=value, inline=True if key != "Ranks" else False)

    return embed


def display_sw(sw):
    """Displays 12-digit integer in neat SW format."""
    return f"SW-{sw[:4]}-{sw[4:8]}-{sw[8:]}"


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

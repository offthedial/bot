import discord

import utils


async def main(ctx):
    """$profile status command."""
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
            value = f"`{value}`"
        else:  # key == "Ranks":
            value = "\n".join(
                [f'**{subkey}:** `{subvalue}`' for subkey, subvalue in profile["status"]["Ranks"].items()]
            )
        embed.add_field(name=key, value=value, inline=True if key != "Ranks" else False)

    return embed

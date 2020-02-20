"""$profile"""
import discord

from offthedialbot import utils


async def main(ctx):
    """View your profile."""
    profile: utils.Profile = await check_for_profile(ctx)
    embed: discord.Embed = create_status_embed(ctx.author.display_name, profile)
    await ctx.send(embed=embed)


async def check_for_profile(ctx, reverse=False) -> utils.Profile:
    """Returns profile if it exists, otherwise cancels command."""
    try:
        profile = utils.Profile(ctx.author.id)
    except utils.Profile.NotFound:
        profile = None
    if (result := {
        False: lambda p: (p is None, {"title": "No profile found.", "description": "You can create one using `$profile create`."}),
        True: lambda p: (p, {"title": "Existing profile found.", "description": "You can view your profile with `$profile`."}),
    }[reverse](profile))[0]:
        await utils.Alert(ctx, utils.Alert.Style.DANGER, **result[1])
        raise utils.exc.CommandCancel
    return profile


def create_status_embed(name, profile) -> discord.Embed:
    """Create profile embed to display user profile."""
    embed: discord.Embed = discord.Embed(
        title=f"{name}'s Status",
        description=f"**\U0001f4f6 Signal Strength:** `{profile.get_ss()}`",
        color=utils.colors.Roles.DIALER
    )
    for key, value in profile.get_status().items():
        value: str = display_field(key, value)
        embed.add_field(name=key, value=value, inline=True if key != "Ranks" else False)

    return embed


def display_field(key, field) -> str:
    """Displays each field in displayable format."""
    return {
        "IGN": lambda: f'`{field}`' if field else '*`pending`*',
        "SW": lambda: f"`SW-{str(field)[:4]}-{str(field)[4:8]}-{str(field)[8:]}`" if field is not None else '*`pending`*',
        "Ranks": lambda: "\n".join(
            [f"**{k}:** {(f'`{utils.Profile.convert_rank_power(v)}`' if v else '*`pending`*')}" for k, v in
             field.items()])
    }[key]()

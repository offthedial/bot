"""$profile"""
import discord

from offthedialbot import utils


@utils.deco.profile_required()
async def main(ctx):
    """View your profile."""
    profile: utils.Profile = utils.Profile(ctx.author.id)
    embed: discord.Embed = create_status_embed(ctx.author.display_name, profile)
    await ctx.send(embed=embed)


def create_status_embed(name, profile) -> discord.Embed:
    """Create profile embed to display user profile."""
    embed: discord.Embed = discord.Embed(
        title=f"{name}'s Status",
        description=f"**\U0001f4f6 Signal Strength:** `{profile.get_ss() if profile.get_ss() != -1 else 'MAX'}`",
        color=utils.colors.DIALER if not profile.get_competing() else utils.colors.COMPETING
    )
    for key, value in profile.get_status().items():
        value: str = display_field(key, value)
        embed.add_field(name=key, value=value, inline=True if key != "Ranks" else False)

    return embed


def display_field(key, field) -> str:
    """Displays each field in displayable format."""
    return {
        "IGN": lambda: f'`{field}`' if field else '*`pending`*',
        "SW": lambda: f"`SW-{field[:4]}-{field[4:8]}-{field[8:]}`" if field is not None else '*`pending`*',
        "Ranks": lambda: "\n".join(
            [f"**{k}:** {(f'`{utils.Profile.convert_rank_power(v)}`' if v else '*`pending`*')}" for k, v in
             field.items()])
    }[key]()

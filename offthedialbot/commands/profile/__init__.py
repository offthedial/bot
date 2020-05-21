"""$profile"""
import discord

from offthedialbot import utils


class Profile(utils.Command):
    """View your profile."""

    @classmethod
    @utils.deco.profile_required()
    async def main(cls, ctx):
        """View your profile."""
        profile: utils.Profile = utils.Profile(ctx.author.id)
        embed: discord.Embed = cls.create_status_embed(ctx.author.display_name, profile, True)
        await ctx.send(embed=embed)

    @classmethod
    def create_status_embed(cls, name, profile, ss=False) -> discord.Embed:
        """Create profile embed to display user profile."""
        embed: discord.Embed = discord.Embed(
            title=f"{name}'s Status",
            color=utils.colors.DIALER if not profile.get_reg() else utils.colors.COMPETING
        )
        if ss:
            embed.description = f"\U0001f4f6 Signal Strength: `{profile.get_ss() if profile.get_ss() != -1 else 'MAX'}`"
        for key, value in [('IGN', profile.get_ign()), ('SW', profile.get_sw()), ('Ranks', profile.get_ranks())]:
            value: str = cls.display_field(key, value)
            embed.add_field(name=key, value=value, inline=key != "Ranks")

        return embed

    @classmethod
    def display_field(cls, key, field) -> str:
        """Displays each field in displayable format."""
        return {
            "IGN": lambda: f'`{field}`' if field else '*`pending`*',
            "SW": lambda: f"`SW-{field[:4]}-{field[4:8]}-{field[8:]}`" if field is not None else '*`pending`*',
            "Ranks": lambda: "\n".join(
                [f"{k}: {(f'`{utils.Profile.convert_rank_power(v)}`' if v else '*`pending`*')}" for k, v in
                 field.items()])
        }[key]()

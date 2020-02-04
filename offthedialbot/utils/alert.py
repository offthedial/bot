"""Contains the Alert class."""
from typing import Optional

import discord


class Alert:
    """Custom polished alerts."""

    class Style:
        """Alert styles and their colors."""
        DANGER = 0xf50206
        WARNING = 0xffbe00
        SUCCESS = 0x63ae33
        INFO = 0x0082ef

    def __init__(self, ctx, style: Style, *, title: str, description: str):
        """Create alert embed."""
        self.ctx = ctx
        self.embed: discord.Embed = self.create_embed(style, title, description)
        self.alert: Optional[discord.Message] = None

    async def __new__(cls, *args, **kwargs):
        """Create message on class creation using async."""
        self = super().__new__(cls)
        self.__init__(*args, **kwargs)

        self.alert = await self.ctx.send(embed=self.embed)
        return self

    @classmethod
    def create_embed(cls, style, title: str, description: str = None) -> discord.Embed:
        """Create alert embed."""
        title_key = {
            cls.Style.DANGER: lambda t: f'\U0001f6ab Error: **{t}**',
            cls.Style.WARNING: lambda t: f'\u26a0 Warning: **{t}**',
            cls.Style.INFO: lambda t: f'\u2139 Info: **{t}**',
            cls.Style.SUCCESS: lambda t: f'\u2705 Success: **{t}**',
        }
        return discord.Embed(title=title_key[style](title), description=description, color=style)

    async def delete(self) -> None:
        """Remove alert."""
        if self.alert:
            await self.alert.delete()
            self.alert = None

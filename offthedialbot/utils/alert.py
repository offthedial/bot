import discord


class Alert:
    """An alert API."""

    class Style:
        """Class holding specifically alert styles and their colors."""
        DANGER = 0xf50206
        WARNING = 0xffbe00
        SUCCESS = 0x63ae33
        INFO = 0x0082ef

    def __init__(self, ctx, style, *, title, description):
        """Create alert embed."""
        self.ctx = ctx
        self.embed = self.create_embed(style, title, description)
        self.alert = None

    async def __new__(cls, *args, **kwargs):
        """Use async to create message on class creation."""
        self = super().__new__(cls)
        self.__init__(*args, **kwargs)

        self.alert = await self.ctx.send(embed=self.embed)
        return self

    @classmethod
    def create_embed(cls, style, title: str, description: str = None):
        """Creates alert embed."""
        title_key = {
            cls.Style.DANGER: lambda t: f'\U0001f6ab Error: **{t}**',
            cls.Style.WARNING: lambda t: f'\u26a0 Warning: **{t}**',
            cls.Style.INFO: lambda t: f'\u2139 Info: **{t}**',
            cls.Style.SUCCESS: lambda t: f'\u2705 Success: **{t}**',
        }
        return discord.Embed(title=title_key[style](title), description=description, color=style)

    async def delete(self):
        """Remove alert."""
        if self.alert:
            await self.alert.delete()
            self.alert = None

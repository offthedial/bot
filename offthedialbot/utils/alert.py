import discord


class Alert:
    """An alert API."""

    class Style:
        """Class holding specifically alert style colors."""
        DANGER = 0xf50206
        WARNING = 0xffbe00
        SUCCESS = 0x63ae33
        INFO = 0x0082ef

    def __init__(self, ctx, style, *, title, description):
        """Create alert embed."""
        title_key = {
            self.Style.DANGER: lambda t: f'\U0001f6ab Error: **{t}**',
            self.Style.WARNING: lambda t: f'\u26a0 Warning: **{t}**',
            self.Style.INFO: lambda t: f'\u2139 Info: **{t}**',
            self.Style.SUCCESS: lambda t: f'\u2705 Success: **{t}**',
        }
        self.ctx = ctx
        self.embed = discord.Embed(title=title_key[style](title), description=description, color=style)
        self.alert = None

    async def __new__(cls, *args, **kwargs):
        """Use async to create message on class creation."""
        self = super().__new__(cls)
        self.__init__(*args, **kwargs)

        self.alert = await self.ctx.send(embed=self.embed)
        return self

    async def delete(self):
        """Remove alert."""
        if self.alert:
            await self.alert.delete()
            self.alert = None

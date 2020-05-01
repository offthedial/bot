"""Contains the Command class."""
from discord.ext.commands import Context


class Command:
    """Base command class."""

    ctx: Context = None
    command_attrs: dict = {}

    def __init_subclass__(cls, **kwargs):
        cls.command_attrs = kwargs

    @classmethod
    async def get_ctx(cls, ctx):
        """Set the class context variable."""
        cls.ctx = ctx

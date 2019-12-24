"""Holds client subclass of discord.ext.Bot, and registers listeners, commands, and cogs."""

from discord.ext.commands import Bot

from offthedialbot import listeners
from offthedialbot import commands
from offthedialbot import cogs


class Client(Bot):
    """commands.Bot subclass containing helpful constants."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.OTD = self.get_guild(374715620052172800)

        class Channels:
            """Class containing channel objects."""
            GENERAL = self.get_channel(374715620052172802)

        class Roles:
            """Class containing role objects."""
            try:
                DIALER = self.OTD.get_role(427710343616397322)
            except AttributeError:
                DIALER = None

        self.Channels = Channels
        self.Roles = Roles


client = Client(command_prefix='$')

listeners.register_listeners(client)
commands.register_commands(client)
cogs.register_cogs(client)

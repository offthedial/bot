"""Contains on_ready listener."""
from collections import defaultdict


async def on_ready(self):
    """When the bot is ready."""
    self.OTD = self.get_guild(374715620052172800)
    self.ongoing_commands = defaultdict(set)
    self.logger.info(f'Logged in as: {self.user.name}')

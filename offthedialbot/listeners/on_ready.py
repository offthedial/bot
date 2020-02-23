"""Contains on_ready listener."""
from collections import defaultdict


async def on_ready(client):
    """When the bot is ready."""
    client.OTD = client.get_guild(374715620052172800)
    client.ongoing_commands = defaultdict(set)
    client.logger.info(f'Logged in as: {client.user.name}')

"""Contains commonly used roles."""
import discord

from offthedialbot import logger


def dialer(client):
    """Dialer role."""
    try:
        return client.OTD.get_role(427710343616397322)
    except AttributeError:
        logger.warn("Could not get 'Dialer' role object, possibly not in Off the Dial.")


def alerts(client):
    """Off the Dial Alerts role."""
    try:
        return client.OTD.get_role(479793360530440192)
    except AttributeError:
        logger.warn("Could not get 'Alerts' role object, possibly not in Off the Dial.")


def get(ctx, name=None, /, **kwargs):
    if name:
        kwargs["name"] = name
    return discord.utils.get(ctx.guild.roles, **kwargs)

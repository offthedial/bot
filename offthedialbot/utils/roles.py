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
    """Get the role object given their name, or other attribute."""
    if name:
        kwargs["name"] = name
    roles = getattr(getattr(ctx, "guild", None), "roles", [])
    return discord.utils.get(roles, **kwargs)


def has(member, name=None, /, **kwargs):
    """Check if a member has a given role by their name, or other attribute."""
    role = get(member, name, **kwargs)
    return role in member.roles

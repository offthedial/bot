"""Holds the static embeds used."""

import discord

import utils

SUCCESS = discord.Embed(title="Success!", color=utils.AlertStyle.SUCCESS)
CANCELED = discord.Embed(title="Canceled.", color=utils.AlertStyle.DANGER)


def alert(style, title, description):
    """Create alert embed."""
    title_key = {
        utils.AlertStyle.DANGER: lambda t: f'\U0001f6ab Error: **{t}**',
        utils.AlertStyle.WARNING: lambda t: f'\u26a0 Warning: **{t}**',
        utils.AlertStyle.INFO: lambda t: f'\u2139 Info: **{t}**',
        utils.AlertStyle.SUCCESS: lambda t: f'\u2705 Success: **{t}**',
    }
    return discord.Embed(title=title_key[style](title), description=description, color=style)

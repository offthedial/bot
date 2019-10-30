"""Holds the static embeds used."""

import discord

import utils

SUCCESS = discord.Embed(title="Success!", color=utils.colors.GOOD)
CANCELED = discord.Embed(title="Canceled.", color=utils.colors.ALERT)


def create_error_embed(error: str, description: str):
    embed = discord.Embed(title=f"\U0001f6ab Error: **{error}**", description=description, color=utils.colors.ALERT)
    return embed

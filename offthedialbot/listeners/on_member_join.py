"""Contains on_member_join listener."""

import asyncio

from offthedialbot import utils


async def on_member_join(client, member):
    """When a new member joins Off the Dial."""
    if member.guild != client.OTD:  # Check if it's the correct the server
        return

    await add_roles(client, member)  # Add roles


async def add_roles(client, member):
    """Add roles to the user."""
    role = member.guild.get_role(427710343616397322)
    await member.add_roles(role)

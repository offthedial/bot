"""Contains on_member_join listener."""
import asyncio

from offthedialbot import utils


async def on_member_join(client, member):
    """When a new member joins Off the Dial."""
    if member.guild != client.OTD:  # Check if it's the correct the server
        return

    await add_roles(client, member)  # Add roles
    welcome = await send_welcome(client, member)  # Create welcome message

    # Incase they leave immediately
    await member_leave(client, member, welcome)


async def add_roles(client, member):
    """Add roles to the user."""
    try:
        profile = utils.Profile(member.id)
    except utils.Profile.NotFound:
        profile = utils.ProfileMeta(member.id)

    roles = [
        utils.roles.dialer(client),
        utils.roles.alerts(client)
    ]
    if profile.get_reg():
        roles.append(utils.roles.get(member, "Competing"))

    await member.add_roles(*roles)


async def send_welcome(client, member):
    """Send welcome message."""
    channel = utils.channels.general(client)
    welcome = await channel.send(f"Let's welcome {member.mention} to __Off the Dial__! :wave:")
    await welcome.add_reaction("\U0001f44b")
    return welcome


async def member_leave(client, member, welcome):
    """Delete the welcome message because the user left less than 5 minutes after."""
    try:
        await client.wait_for('member_remove', check=utils.checks.member(member), timeout=300)
    except asyncio.TimeoutError:
        pass
    else:
        await welcome.delete()

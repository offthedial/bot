"""Contains on_member_join listener."""
from offthedialbot import utils


async def on_member_join(client, member):
    """When a new member joins Off the Dial."""
    # Check if it's the correct the server
    if member.guild != client.OTD:
        return
    
    # Add roles
    await add_roles(client, member)
    # Create welcome message
    welcome = await send_welcome(client, member)
    # Incase they leave immediately
    await member_leave(client, member, welcome)


async def add_roles(client, member):
    try:
        profile = utils.Profile(member.id)
    except utils.Profile.NotFound:
        profile = None

    roles = [
        utils.roles.dialer(client),
        utils.roles.alerts(client)
    ]
    if profile and profile.get_competing():
        roles.append(utils.roles.get(member, "Competing"))

    await member.add_roles(*roles)


async def send_welcome(client, member):
    channel = utils.channels.general(client)
    welcome = await channel.send(f"Let's welcome {member.mention} to __Off the Dial__! :wave:")
    await welcome.add_reaction("\U0001f44b")
    return welcome


async def member_leave(client, member, welcome):
    try:
        await client.wait_for('member_remove', check=utils.checks.member(member), timeout=300)
    except TimeoutError:
        pass
    else:
        await welcome.delete()

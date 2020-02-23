"""Contains on_member_join listener."""
from offthedialbot import utils


async def on_member_join(client, member):
    """When a new member joins Off the Dial."""
    # Check if it's the correct the server
    if member.guild != client.OTD:
        return
    # Check if they have a profile
    try:
        profile = utils.Profile(member.id)
    except utils.Profile.NotFound:
        profile = None
    # Get channel and roles
    channel = utils.channels.general(self)
    roles = [
        utils.roles.dialer(self),
        utils.roles.alerts(self)]
    if profile and profile.get_competing():
        roles.append(utils.roles.competing(self))
    # Add roles
    member.add_roles(*roles)
    # Create welcome message
    welcome = await channel.send(f"Let's welcome {member.mention} to __Off the Dial__! :wave:")
    await welcome.add_reaction("\U0001f44b")
    return welcome


async def member_leave(client, member, welcome):
    try:
        await client.wait_for('member_remove', check=utils.checks.join_or_leave(member), timeout=300)
    except TimeoutError:
        pass
    else:
        await welcome.delete()

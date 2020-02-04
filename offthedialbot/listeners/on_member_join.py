"""Contains on_member_join listener."""


async def on_member_join(self, member):
    """When a new member joins Off the Dial."""
    if member.guild != self.get_guild(self.OTD):
        return
    # Get channel and role
    channel = self.get_channel(self.Channels.GENERAL)
    dialer = self.get_role(self.Roles.DIALER)
    # Add role
    await member.add_roles(dialer)
    # Create welcome message
    welcome = await channel.send(f"Let's welcome {member.mention} to __Off the Dial__! :wave:")
    await welcome.add_reaction("\U0001f44b")

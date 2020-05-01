"""$to profiles get"""
import discord

from offthedialbot import utils
from offthedialbot.commands.profile import Profile


@utils.deco.require_role("Organiser")
async def main(ctx):
    """Get a specific profile."""
    ui: utils.CommandUI = await utils.CommandUI(ctx, embed=discord.Embed())
    for profile, member in await get_profiles(ui):
        await ctx.send(embed=Profile.create_status_embed(member.display_name, profile, True))

    await ui.end(None)


async def get_profiles(ui, meta=False):
    """Return a list of profile, member tuples that the user specifies."""
    ui.embed = discord.Embed(
        title="Mention each user you want to get.",
        color=utils.colors.DIALER
    )
    reply = await ui.get_valid_message(lambda m: len(m.mentions),
        {"title": "Invalid Mention", "description": "Make sure to **mention** each user."})

    profiles = await create_profiles_list(ui.ctx, reply.mentions, meta)
    return profiles


async def get_role_profiles(ui, meta=False):
    """ Get all the profiles within each role specifiecd

        :return: {discord.Role: [(utils.Profile, discord.Member), ]}
    """
    ui.embed = discord.Embed(
        title="Mention each role you want to get.",
        color=utils.colors.DIALER
    )
    reply = await ui.get_valid_message(lambda m: len(m.role_mentions),
        {"title": "Invalid Mention", "description": "Make sure to **mention** each role."})

    roles_profiles = {}
    for role in reply.role_mentions:
        profiles = await create_profiles_list(ui.ctx, role.members, meta)
        roles_profiles[role] = profiles
    return roles_profiles


async def create_profiles_list(ctx, members, meta=False):
    """Create a list of profile tuples."""
    profiles = []
    for member in members:
        if profile := (await get_profile_member(ctx, member, meta)):
            profiles.append(profile)
    return profiles


async def get_profile_member(ctx, member, meta=False):
    """Return a tuple containing a utils.Profile object and a discord.Member object."""
    if not meta:
        try:
            return utils.Profile(member.id), member
        except utils.Profile.NotFound:
            await utils.Alert(ctx, utils.Alert.Style.DANGER,
                title="Invalid User", description=f"{member.display_name} doesn't have a profile.")
            return False
    else:
        return utils.ProfileMeta(member.id), member

"""Contains on_member_remove listener."""
from offthedialbot import utils


async def on_member_remove(client, member):
    """When a new member leaves Off the Dial."""
    # Check if it's the correct the server
    if member.guild != client.OTD:
        return

    await warn_if_competing(member)


async def warn_if_competing(member):
    """Warn the user if they are still registered."""
    profile = utils.ProfileMeta(member.id)

    if not (profile.get_reg() and not profile.get_banned()):
        return
    if not ((tourney := utils.dbh.get_tourney()) and tourney["reg"]):
        return

    # Member should be warned
    alert = utils.Alert.create_embed(
        utils.Alert.Style.WARNING,
        title="You are still registered for the upcoming tournament!",
        description="Make sure to rejoin the server immediately or you will be disqualified. If you were intending to droppout, make sure you let the TO's know so they can remove you from the smash.gg page")
    await member.send(embed=alert)

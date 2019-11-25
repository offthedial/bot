import discord

import utils


async def main(ctx):
    """Test command to test each of the alerts."""
    embed = discord.Embed(title="Testing: Alerts")
    ui = await utils.CommandUI(ctx, embed)

    alert_styles = (
        utils.Alert.Colors.DANGER, utils.Alert.Colors.WARNING, utils.Alert.Colors.INFO, utils.Alert.Colors.SUCCESS
    )

    for style in alert_styles:
        await ui.create_alert(style, title="This is a test alert", description="Check it out!")
        await ui.get_reply('reaction_add', valid_reactions=['\U0001f44c'])
        await ui.delete_alert()

    await ui.end(status=True)

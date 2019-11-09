import utils
import discord


async def main(ctx, arg):
    """Test command to test each of the alerts."""
    embed = discord.Embed(title="Testing: Alerts")
    ui = utils.CommandUI(ctx, embed)

    alert_styles = (utils.AlertStyle.DANGER, utils.AlertStyle.WARNING, utils.AlertStyle.INFO, utils.AlertStyle.SUCCESS)

    for style in alert_styles:
        await ui.create_alert(style, title="This is a test alert", description="Check it out!")
        await ui.get_reply('reaction_add', valid_reactions=['\U0001f44c'])

    await ui.end(status=True)

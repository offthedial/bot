"""$test alerts"""
import discord

from offthedialbot import utils


class TestAlerts(utils.Command):
    """Cycle through each of the different alert types."""

    @classmethod
    async def main(cls, ctx):
        """Cycle through each of the different alert types."""
        embed: discord.Embed = discord.Embed(title="Testing: Alerts")
        ui: utils.CommandUI = await utils.CommandUI(ctx, embed)

        alert_styles: tuple = (
            utils.Alert.Style.DANGER, utils.Alert.Style.WARNING, utils.Alert.Style.INFO, utils.Alert.Style.SUCCESS
        )

        for style in alert_styles:
            await ui.create_alert(style, title="This is a test alert", description="Check it out!")

        await ui.get_valid_reaction(['\U0001f44c'])
        await ui.end(status=True)

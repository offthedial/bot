"""$to"""

import discord

from offthedialbot import utils
from offthedialbot.commands.to.sync import ToSync


class To(utils.Command, hidden=True):

    @classmethod
    @utils.deco.require_role("Staff")
    async def main(cls, ctx):
        """ Special commands to help with organizing tournaments.

            Displays a dashboard showing the current tournament status, with a built-in sync button.
        """
        options = {
            "sync": '♻️',
            "done": '☑️'
        }
        tourney = utils.Tournament()
        # Create embed
        embed = discord.Embed(
            title=f"Welcome, {ctx.author.name} to your Tourney Dashboard",
            color=utils.colors.COMPETING)
        cls.update_embed(ctx, embed, tourney)
        # Create UI
        ui = await utils.CommandUI(ctx, embed)
        # Set up operator
        while True:
            reply = await ui.get_valid_reaction(list(options.values()), cancel=False)
            await cls.operator(ui, reply.emoji, options)
            await tourney.sync_smashgg()
            cls.update_embed(ui.ctx, embed, tourney)
            await ui.update()

    @classmethod
    async def operator(cls, ui, option, options):
        """Route reply option to command."""
        if option == options['done']:
            await ui.end(True)
        elif option == options['sync']:
            await ToSync.sync(ui.ctx.bot, smashgg=False)


    @classmethod
    def update_embed(cls, ctx, embed, tourney):
        embed.description="\n".join([
            f"Name: `{tourney.dict['smashgg']['name']}`",
            f"Slug: `{tourney.dict['slug']}`",
            f"Type: `{tourney.dict['type']}`",
            f"Start Date: `{tourney.date()}`",
            f"Close Date: `{tourney.reg_closes_at()}`",
            f"End Date: `{tourney.ends_at()}`",
            *([f"🔒 Whitelist: `{str(len(tourney.dict['whitelist']))} Players`"] if tourney.dict.get("whitelist") else [])
        ])
        embed.clear_fields()
        embed.add_field(name="`Current Status:`", value=f"{tourney.status()}")

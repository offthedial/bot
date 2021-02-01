"""$to"""

import discord

from offthedialbot import utils
from offthedialbot.commands.to.sync import ToSync


class To(utils.Command, hidden=True):

    @classmethod
    @utils.deco.require_role("Staff")
    async def main(cls, ctx):
        """ Special commands to help with organizing tournaments.

        Display a dashboard displaying the current tournament status.
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
            f"**`name:     `** `{tourney.dict['smashgg']['name']}`",
            f"**`slug:     `** `{tourney.dict['slug']}`",
            f"**`type:     `** `{tourney.dict['type']}`",
            f"**`date:     `** `{tourney.date()}`",
            f"**`reg close:`** `{tourney.reg_closes_at()}`",
            f"**`end date: `** `{tourney.ends_at()}`",
        ])
        embed.clear_fields()
        embed.add_field(name="`Current Status:`", value=f"{tourney.status()}")

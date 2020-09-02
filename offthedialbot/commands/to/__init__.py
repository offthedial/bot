"""$to"""
import discord

from offthedialbot import utils
from .open import ToOpen
from .start import ToStart
from .close import ToClose
from .end import ToEnd


class To(utils.Command, hidden=True):
    """ Special commands for tournament organisers!

    Shows a dashboard when run on it's own.
    """

    @classmethod
    @utils.deco.require_role("Organiser")
    async def main(cls, ctx):
        """Special commands for tournament organisers, shows dashboard."""
        ui: utils.CommandUI = await utils.CommandUI(ctx, discord.Embed(
            title=f"Welcome {ctx.author.display_name}, to your TO dashboard!",
            color=utils.colors.ORGANISER))
        while True:

            ui.embed.clear_fields()
            options = {'done': '\u2611'}
            if not (tourney := utils.tourney.get()):
                options.update({"new": '\u270f'})
                ui.embed.description = f"You currently don't have a tournament running. Open one with `$to open` or select {options['new']}."
            else:
                options.update({'next': '\u23ed'})
                await cls.show_dashboard(ui, tourney, options)

            reply = await ui.get_valid_reaction(list(options.values()), cancel=False)
            await cls.operator(ui, reply.emoji, options)

    @classmethod
    async def operator(cls, ui, option, options):
        """Route reply option to command."""
        if option == options['done']:
            await ui.end(True)
        elif option == options.get('new'):
            await ui.run_command(ToOpen.main)
        elif option == options.get('next'):
            await ui.run_command([
                ToOpen,
                ToStart,
                ToClose,
                ToEnd
            ][utils.tourney.current_step()].main)

    @classmethod
    async def show_dashboard(cls, ui, tourney, options):
        """Show TO dashboard when there is an ongoing tournament."""
        ui.embed.description = f"To proceed to the next step, select {options['next']}."
        ui.embed.add_field(name="Current Tournament Status:", value="\n".join([
            f"**Type:** `{utils.tourney.Type(tourney['type']).name}`", ""
            f"**Registration:** {utils.emojis.lock[tourney['reg']]}",
            f"**Check-in:** {utils.emojis.lock[tourney['checkin']]}"
        ]))
        ui.embed.add_field(name="Checklist:", value="\n".join([
            f"{utils.emojis.checklist[i < utils.tourney.current_step()]} {value}" for i, value in enumerate([
                "`$to open ` Open registration.",
                "`$to start` Start check-in.",
                "`$to close` Close registration and end check-in.",
                "`$to end  ` End the tournament."]
            )
        ]))

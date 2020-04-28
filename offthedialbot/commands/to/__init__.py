"""$to"""
import discord

from offthedialbot import utils
from . import open as to_open
from . import start as to_start
from . import close as to_close
from . import end as to_end


@utils.deco.require_role("Organiser")
async def main(ctx):
    """Command tools for managing tournaments."""
    ui: utils.CommandUI = await utils.CommandUI(ctx, discord.Embed(
        title=f"Welcome {ctx.author.display_name}, to your TO dashboard!",
        color=0xdc6e00))
    while True:

        ui.embed.clear_fields()
        options = {'done': '\u2611'}
        if not (tourney := utils.tourney.get()):
            options.update({"new": '\u270f'})
            ui.embed.description = f"You currently don't have a tournament running. Open one with `$to open` or select {options['new']}."
        else:
            options.update({'next': '\u23ed'})
            await show_dashboard(ui, tourney, options)

        reply = await ui.get_valid_reaction(list(options.values()), cancel=False)
        await operator(ui, reply.emoji, options)


async def operator(ui, option, options):
    """Route reply option to command."""
    if option == options['done']:
        await ui.end(True)
    elif option == options.get('new'):
        await ui.run_command(to_open.main)
    elif option == options.get('next'):
        await ui.run_command([
            to_open,
            to_start,
            to_close,
            to_end
        ][utils.tourney.current_step()].main)


async def show_dashboard(ui, tourney, options):
    """Show TO dashboard when there is an ongoing tournament."""
    ui.embed.description = f"To proceed to the next step, select {options['next']}."
    emoji = {
        "lock": {True: '\U0001f513', False: '\U0001f512'},
        "check": {True: '\u2705', False: '\u23f9'}
    }
    ui.embed.add_field(name="Current Tournament Status:", value="\n".join([
        f"**Type:** `{utils.tourney.Type(tourney['type']).name}`", ""
        f"**Registration:** {emoji['lock'][tourney['reg']]}",
        f"**Check-in:** {emoji['lock'][tourney['checkin']]}"
    ]))
    ui.embed.add_field(name="Checklist:", value="\n".join([
        f"{emoji['check'][i < utils.tourney.current_step()]} {value}" for i, value in enumerate([
            "`$to open ` Open registration.",
            "`$to start` Start check-in.",
            "`$to close` Close registration and end check-in.",
            "`$to end  ` End the tournament."]
        )
    ]))

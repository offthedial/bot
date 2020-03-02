"""$to attendees ban"""
import discord
from dateutil.relativedelta import relativedelta

from offthedialbot import utils, log
from . import remove


@utils.deco.require_role("Organiser")
async def main(ctx):
    """Ban an attendee from the tournament."""
    ui: utils.CommandUI = await utils.CommandUI(ctx, discord.Embed(title="Ban attendees.", description="Mention each attendee you want to ban.", color=utils.Alert.Style.DANGER))
    reply = await ui.get_valid_message(lambda m: len(m.mentions) == 1, {"title": "Invalid Message", "description": "Make sure to send a **mention** of the attendee."})

    for attendee in reply.mentions:

        # Check to make sure the attendee is valid
        if not (profile := await remove.check_valid_attendee(ctx, attendee, competing=False)):
            continue
        
        await remove_smashgg(ui, attendee)
        await set_ban_length(ui, attendee, profile)
        await remove.remove_attendee(ctx, attendee, profile, reason=f"attendee manually banned by {ctx.author.display_name}.")

        # Complete ban
        profile.write()
        await utils.Alert(ctx, utils.Alert.Style.SUCCESS, title="Ban attendee complete", description=f"`{attendee.display_name}` is now banned.")

    await ui.end(None)


async def remove_smashgg(ui, attendee):
    """Remove attendee from smash.gg if applicable."""
    try:
        await remove.remove_smashgg(ui, attendee)
    except TypeError:
        pass


async def set_ban_length(ui: utils.CommandUI, attendee, profile):
    """Get ban length and set it inside of the profile."""
    ui.embed.description = f"Specify the length of the ban."
    ui.embed.add_field(name="Supported symbols:", value="\n".join([
        "- years: `Y`, `y`, `yrs`, `year`, `years`",
        "- months: `m`, `mon`, `month`, `months`",
        "- weeks: `w`, `W`, `week`, `weeks`",
        "- days: `d`, `D`, `day`, `days`",
        "- hours: `H`, `h`, `hrs`, `hour`, `hours`",
        "- minutes: `M`, `min`, `minute`, `minutes`",
        "- seconds: `S`, `s`, `sec`, `second`, `seconds`", "",
        "Units must be provided in descending order of magnitude."
    ]))
    reply = await ui.get_valid_message(lambda m: utils.time.Parse.user(m.content), {"title": "Invalid Length", "description": "Please check the `Supported symbols` and make sure your input is correct."})
    banned = utils.time.Parse.user(duration=reply.content)
    profile.set_banned(banned)  # + relativedelta(weeks=2))
    ui.embed.remove_field(0)

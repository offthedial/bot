import utils
from .. import create, check_for_profile, display_field, create_status_embed


async def main(ctx):
    """Run command for $profile update."""
    profile = await check_for_profile(ctx)
    embed, emojis = create_update_embed(ctx, profile)

    ui: utils.CommandUI = await utils.CommandUI(ctx, embed)

    reply = await ui.get_reply("reaction_add", valid_reactions=emojis)
    field = create.clean_status_key(profile, list(profile.get_status().keys())[emojis.index(reply[0].emoji)])

    # Set up update field
    embed.clear_fields()
    embed.add_field(name=field[0], value=display_field(*field))

    # Wait for user to type whichever field they want to update
    await [
        lambda: create.set_status_field(ui, profile, "IGN", 0),
        lambda: create.set_status_field(ui, profile, "SW", 0),
        lambda: create.set_rank_field(ui, profile, 0),
    ][emojis.index(reply[0].emoji)]()

    # Confirm profile and save it
    if await create.confirm_profile(ui):
        utils.dbh.update_profile(profile.dict(), ui.ctx.author.id)
        await ui.end(True)


def create_update_embed(ctx, profile):
    """Create status embed, with some adjustments."""
    embed = create_status_embed(ctx.author.display_name, profile)
    emojis = []
    for (index, field), emoji in zip(enumerate(embed.fields), utils.emojis.digits()):
        embed.set_field_at(index, name=(f"{emoji} " + field.name), value=field.value, inline=True if field.name != "Ranks" else False)
        emojis.append(emoji)
    embed.description = "React with the field you would like to change."
    return embed, emojis

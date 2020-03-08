"""$profile update"""
from offthedialbot import utils
from .. import create, display_field, create_status_embed


@utils.deco.profile_required()
async def main(ctx):
    """Update your profile."""
    profile: utils.Profile = utils.Profile(ctx.author.id)
    embed, emojis = create_update_embed(ctx, profile)

    ui: utils.CommandUI = await utils.CommandUI(ctx, embed)

    reply = await ui.get_valid_reaction(emojis)
    index: int = emojis.index(reply.emoji)
    field = create.clean_status_key(profile, list(profile.get_status().keys())[index])
    await wait_profile_field(ui, profile, index, field)


async def wait_profile_field(ui: utils.CommandUI, profile: utils.Profile, index, field) -> None:
    """wait for reply and write updated field."""
    ui.embed.clear_fields()
    ui.embed.add_field(name=field[0], value=display_field(*field))

    await set_field(ui, profile, index)

    # Confirm profile and save it
    if await create.confirm_profile(ui):
        profile.write()
        await ui.end(True)
    else:
        ui.embed, _ = create_update_embed(ui.ctx, profile)
        await wait_profile_field(ui, profile, index, field)


async def set_field(ui: utils.CommandUI, profile: utils.Profile, index: int) -> None:
    """Wait for user to type whichever field they want to update."""
    await [
        lambda: create.set_status_field(ui, profile, "IGN", 0),
        lambda: create.set_status_field(ui, profile, "SW", 0),
        lambda: create.set_rank_field(ui, profile, 0),
    ][index]()


def create_update_embed(ctx, profile: utils.Profile):
    """Create status embed, with some adjustments."""
    embed = create_status_embed(ctx.author.display_name, profile)
    emojis: list = []
    for (index, field), emoji in zip(enumerate(embed.fields), utils.emojis.digits):
        embed.set_field_at(index, name=(f"{emoji} " + field.name), value=field.value,
                           inline=True if field.name != "Ranks" else False)
        emojis.append(emoji)
    embed.description = "React with the field you would like to change."
    return embed, emojis

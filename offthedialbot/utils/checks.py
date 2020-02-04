"""Contains checks used for filtering replies."""


def msg(m, ctx) -> bool:
    """Check if the message is in the same channel, and is by the same author."""
    return m.channel == ctx.channel and m.author == ctx.author


def react(r, ctx, ui, valids=None) -> bool:
    """Check if the reaction is on the correct message, and is by the same author."""
    return (r[0].message.id, r[1]) == (ui.id, ctx.author) and (valids is None or r[0].emoji in valids)

"""Holds checks used for filtering replies."""


def msg(m, ctx):
    """Check if the message is in the same channel, and is by the same author."""
    return m.channel == ctx.channel and m.author == ctx.author


def react(r, ctx, valids=None):
    """Check if the reaction is on the correct message, and is by the same author."""
    return (r[0].message.id, r[1]) == (ctx.ui.id, ctx.ui.author) and (valids is None or r[0].emoji in valids)

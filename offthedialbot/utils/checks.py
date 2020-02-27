"""Contains checks used for filtering replies."""


def msg(ctx):
    """Check if the message is in the same channel, and is by the same author."""
    return lambda m: m.channel == ctx.channel and m.author == ctx.author and not m.content.startswith("\\")


def react(ctx, message, valids=None):
    """Check if the reaction is on the correct message, and is by the same author."""
    return lambda r, u: (r.message.id, u) == (message.id, ctx.author) and (valids is None or r.emoji in valids)


def member(mem):
    """Check if the member who joined or leaved is the same as the member specified."""
    return  lambda m: m.id == mem.id
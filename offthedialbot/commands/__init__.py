import sys
from offthedialbot import client


@client.command()
async def ping(ctx, *, arg=None):
    from .ping import main
    await main(ctx, arg)

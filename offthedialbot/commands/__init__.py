from discord.ext import commands
from offthedialbot import client


@client.command()
async def ping(ctx, *, arg):
    from . import ping
    await ping.main(ctx, arg)

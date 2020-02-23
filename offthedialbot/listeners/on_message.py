"""Contains on_message listener."""


async def on_message(client, message):
    """When a new message is sent."""
    if message.author.id in client.ongoing_commands[message.channel.id]:
        return
    await client.process_commands(message)

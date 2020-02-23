"""Contains on_message listener."""


async def on_message(client, message):
    """When a new message is sent."""
    if locked(client, message):
        return

    await client.process_commands(message)


def locked(client, message):
    """Check if the user has been command-locked."""
    return message.author.id in client.ongoing_commands[message.channel.id]
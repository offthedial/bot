"""Contains on_message listener."""


async def on_message(client, message):
    """When a new message is sent."""
    if any({
        locked(client, message),
        override_commands(client, message)
    }):
        return

    await client.process_commands(message)


def locked(client, message):
    """Check if the user has been command-locked."""
    if getattr(client, 'ongoing_commands', False) is not False:
        return message.author.id in client.ongoing_commands[message.channel.id]
    else:
        return True


def override_commands(client, message):
    """Check if the user wants to send a message without it being seen by the bot."""
    if message.content.startswith("\\"):
        return True

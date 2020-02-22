"""Contains commonly used roles."""
from offthedialbot import log


def dialer(client):
    """Dialer role."""
    try:
        return client.OTD.get_role(427710343616397322)
    except AttributeError:
        log.logger.warn("Could not get 'Dialer' role object, possibly not in Off the Dial.")


def alerts(client):
    """Off the Dial Alerts role."""
    try:
        return client.OTD.get_role(479793360530440192)
    except AttributeError:
        log.logger.warn("Could not get 'Alerts' role object, possibly not in Off the Dial.")


def competing(client):
    """Competing role."""
    try:
        return client.OTD.get_role(415767083691802624)
    except AttributeError:
        log.logger.warn("Could not get 'Competing' role object, possibly not in Off the Dial.")

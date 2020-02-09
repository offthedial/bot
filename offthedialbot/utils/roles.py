"""Contains commonly used roles."""


def dialer(client):
    """Dialer role."""
    client.OTD.get_role(427710343616397322)


def alerts(client):
    """Off the Dial Alerts role."""
    client.OTD.get_role(479793360530440192)


def competing(client):
    """Competing role."""
    client.OTD.get_role(415767083691802624)

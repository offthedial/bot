"""Get enviroment from the bot."""

import yaml

try:
    with open('config.yml') as file:
        env = yaml.safe_load(file)

except FileNotFoundError:
    raise EnvironmentError("Cannot find 'config.yml' in root, have you created one?")

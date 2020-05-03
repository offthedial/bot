"""Get enviroment from the bot."""
import yaml

try:
    with open('config.yml') as file:
        env = yaml.load(file, Loader=yaml.FullLoader)
except FileNotFoundError:
    raise EnvironmentError("Cannot find 'config.yml' in root, have you created one?")

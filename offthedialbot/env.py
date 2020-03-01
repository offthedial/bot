import yaml


with open('config.yml') as file:
    env = yaml.load(file, Loader=yaml.FullLoader)

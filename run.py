"""Script to run Off the Dial bot."""
from offthedialbot import env, client


def main():
    """Run Off the Dial Bot."""
    client.run(env['token'])


if __name__ == '__main__':
    main()

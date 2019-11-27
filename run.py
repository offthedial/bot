"""Script to run Off the Dial bot."""
from offthedialbot import client
from dotenv import load_dotenv
import os


def main():
    """Run Off the Dial Bot."""
    load_dotenv()
    client.run(os.getenv("TOKEN"))


if __name__ == '__main__':
    main()

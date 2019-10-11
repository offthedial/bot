from offthedialbot import client
from dotenv import load_dotenv
import os


def main():
    load_dotenv()
    token = os.getenv("TOKEN")
    client.run(token)


if __name__ == '__main__':
    main()

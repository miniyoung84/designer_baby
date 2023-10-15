import discord
import os
import pkg_resources
from dotenv import load_dotenv

def main():
  load_dotenv()
  discord_version = pkg_resources.get_distribution("discord[voice]").version
  print(f"discord[voice]=={discord_version}")

  token = os.getenv("TOKEN")
  print(f"token = {token}")


if __name__ == '__main__':
  main()

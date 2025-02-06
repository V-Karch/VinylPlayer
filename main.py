import discord
from discord.ext import commands

def get_token():
    with open("token.txt", "r") as f:
        return f.read()

def main():
    client = commands.Bot(
        command_prefix="?",
        intents=discord.Intents.all(),
        help_command=None,
        description="Plays some records",
    )

    client.run(get_token())

if __name__ == "__main__":
    main()

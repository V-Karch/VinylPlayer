import os
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

    @client.event
    async def setup_hook():
        for cog in os.listdir("cogs"):
            await client.load_extension(f"cogs.{cog[:-3]}")
            print(f"Loaded {cog}")  # simple debug print

        print(f"{client.user.name} has logged in.")

    client.run(get_token())


if __name__ == "__main__":
    main()

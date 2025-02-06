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
            if not cog.endswith(".py"):
                continue  # Skip if not cog

            await client.load_extension(f"cogs.{cog[:-3]}")
            print(f"Loaded {cog}")  # simple debug print

        print(f"{client.user.name} has logged in.")

    @client.command(name="sync")
    async def sync(context: commands.Context):
        if context.author.id == 923600698967461898:
            await client.tree.sync()
            await context.send("Syncing...")

    @client.tree.command(name="ping", description="Simple testing command")
    async def ping(interaction: discord.Interaction):
        await interaction.response.send_message("Pong!", ephemeral=True)

    client.run(get_token())


if __name__ == "__main__":
    main()

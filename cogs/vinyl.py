import discord
from discord.ext import commands


class Vinyl(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client


async def setup(client: commands.Bot):
    await client.add_cog(Vinyl(client))

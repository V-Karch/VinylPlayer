import yt_dlp
import discord
import asyncio
from discord import app_commands
from discord.ext import commands


class Vinyl(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.voice_clients = {}
        self.ytdl = yt_dlp.YoutubeDL({"format": "bestaudio/best"})

    @app_commands.command(name="play", description="Play a record")
    async def play(self, interaction: discord.Interaction, record: str):
        await interaction.response.defer()

        try:
            voice_client = await interaction.user.voice.channel.connect()
            self.voice_clients[voice_client.guild.id] = voice_client
        except Exception as e:
            print(e)

        try:
            event_loop = asyncio.get_event_loop()
            data = await event_loop.run_in_executor(
                None, lambda: self.ytdl.extract_info(record, download=False)
            )

            song = data.get("url")
            player = discord.FFmpegPCMAudio(song, options="-vn")

            await interaction.followup.send(f"Now playing: {data.get('title')}")

            self.voice_clients[interaction.guild.id].play(player)
        except Exception as e:
            print(e)

    @app_commands.command(name="stop", description="Stops a playing record")
    async def stop(self, interaction: discord.Interaction):
        await interaction.response.defer()

        # Implement this

        await interaction.followup.send("Not implemented yet.")


async def setup(client: commands.Bot):
    await client.add_cog(Vinyl(client))

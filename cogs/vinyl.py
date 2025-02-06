import json
import yt_dlp
import discord
import asyncio
from discord import app_commands
from discord.ext import commands
from youtube_search import YoutubeSearch


class Vinyl(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.voice_clients = {}
        self.ytdl = yt_dlp.YoutubeDL({"format": "bestaudio/best"})

    @staticmethod
    def get_url_from_search_terms(search_terms: str) -> str:
        results = YoutubeSearch(search_terms, max_results=1).to_json()
        results = json.loads(results)
        return "https://youtube.com/watch?v=" + results.get("videos")[0].get("id")

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

            if not "https" in record:
                song_url = Vinyl.get_url_from_search_terms(record)
            else:
                song_url = record

            song_data = await event_loop.run_in_executor(
                None,
                lambda: self.ytdl.extract_info(song_url, download=False),
            )  # Get the rest of the data about the song

            player = discord.FFmpegPCMAudio(song_data.get("url"), options="-vn")

            embed = discord.Embed(
                color=0x337AFF, title=f"Now Playing: {song_data.get('title')}"
            )
            embed.set_image(url=song_data.get("thumbnail"))
            embed.set_footer(
                text="Requested By: @" + interaction.user.name,
                icon_url=(
                    interaction.user.avatar.url if interaction.user.avatar else None
                ),
            )

            await interaction.followup.send(embed=embed)

            self.voice_clients[interaction.guild.id].play(player)
        except Exception as e:
            print(e)


async def setup(client: commands.Bot):
    await client.add_cog(Vinyl(client))

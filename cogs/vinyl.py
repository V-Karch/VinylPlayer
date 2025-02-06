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
        self.queues = {}  # Dictionary to store per-guild queues
        self.ytdl = yt_dlp.YoutubeDL({"format": "bestaudio/best"})
        self.text_channels = {}  # Store the text channel where play was used
        self.currently_playing = {}  # Store the currently playing song per guild

    @staticmethod
    def get_url_from_search_terms(search_terms: str) -> str:
        results = YoutubeSearch(search_terms, max_results=1).to_json()
        results = json.loads(results)
        return "https://youtube.com/watch?v=" + results.get("videos")[0].get("id")

    async def play_next(self, guild_id: int):
        if self.queues[guild_id]:
            next_song = self.queues[guild_id].pop(0)
            song_url = next_song["url"]
            user = next_song["user"]
            channel = self.text_channels.get(guild_id)

            song_data = await asyncio.get_event_loop().run_in_executor(
                None, lambda: self.ytdl.extract_info(song_url, download=False)
            )

            player = discord.FFmpegPCMAudio(song_data.get("url"), options="-vn")
            self.currently_playing[guild_id] = next_song

            embed = discord.Embed(
                color=0x337AFF, title=f"Now Playing: {song_data.get('title')}"
            )
            embed.set_image(url=song_data.get("thumbnail"))
            embed.set_footer(
                text=f"Requested By: @{user.name}",
                icon_url=(user.avatar.url if user.avatar else None),
            )

            if channel:
                await channel.send(embed=embed)

            self.voice_clients[guild_id].play(
                player,
                after=lambda e: asyncio.run_coroutine_threadsafe(
                    self.play_next(guild_id), self.client.loop
                ),
            )

    @app_commands.command(name="play", description="Play a record")
    async def play(self, interaction: discord.Interaction, record: str):
        if not interaction.user.voice or not interaction.user.voice.channel:
            await interaction.response.send_message(
                "You must be in a voice channel to play music.", ephemeral=True
            )
            return

        await interaction.response.defer()
        guild_id = interaction.guild.id
        self.text_channels[guild_id] = interaction.channel

        if guild_id not in self.queues:
            self.queues[guild_id] = []

        try:
            if (
                guild_id not in self.voice_clients
                or not self.voice_clients[guild_id].is_connected()
            ):
                voice_client = await interaction.user.voice.channel.connect()
                self.voice_clients[guild_id] = voice_client

            if not "https" in record:
                song_url = Vinyl.get_url_from_search_terms(record)
            else:
                song_url = record

            self.queues[guild_id].append({"url": song_url, "user": interaction.user})

            if not self.voice_clients[guild_id].is_playing():
                await self.play_next(guild_id)
            await interaction.followup.send(f"Added to queue: {record}")
        except Exception as e:
            print(e)

    @app_commands.command(name="skip", description="Skip the current song")
    async def skip(self, interaction: discord.Interaction):
        guild_id = interaction.guild.id

        if guild_id in self.voice_clients and self.voice_clients[guild_id].is_playing():
            self.voice_clients[guild_id].stop()
            await interaction.response.send_message("Skipped the current song.")
            await self.play_next(guild_id)
        else:
            await interaction.response.send_message("No song is currently playing.")

    @app_commands.command(name="remove", description="Remove a song from the queue")
    async def remove(self, interaction: discord.Interaction, index: int):
        guild_id = interaction.guild.id

        if guild_id in self.queues and 0 <= index < len(self.queues[guild_id]):
            song = self.queues[guild_id][index]
            if song["user"].id == interaction.user.id:
                del self.queues[guild_id][index]
                await interaction.response.send_message(
                    "Removed your song from the queue."
                )
            else:
                await interaction.response.send_message(
                    "You can only remove songs you added."
                )
        else:
            await interaction.response.send_message("Invalid song index.")

    @app_commands.command(name="queue", description="Show the current queue")
    async def queue(self, interaction: discord.Interaction):
        guild_id = interaction.guild.id
        embed = discord.Embed(title="Current Queue", color=0x337AFF)

        if guild_id in self.currently_playing:
            embed.add_field(
                name="Now Playing:",
                value=f"🎵 {self.currently_playing[guild_id]['url']} (Requested by {self.currently_playing[guild_id]['user'].name})",
                inline=False,
            )

        if guild_id in self.queues and self.queues[guild_id]:
            for i, song in enumerate(self.queues[guild_id]):
                embed.add_field(
                    name=f"{i + 1}. {song['user'].name}",
                    value=song["url"],
                    inline=False,
                )
        else:
            embed.add_field(name="Queue", value="No upcoming songs.", inline=False)

        await interaction.response.send_message(embed=embed)


async def setup(client: commands.Bot):
    await client.add_cog(Vinyl(client))

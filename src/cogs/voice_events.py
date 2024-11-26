import asyncio
import discord
from discord.ext import commands

class VoiceEvents(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.Cog.listener()
  async def on_voice_state_update(self, member, before, after):
    # Check if the user joined a voice channel
    if before.channel is None and after.channel is not None:
      if not (member.guild.voice_client is None):
        await member.guild.voice_client.disconnect()
      voice_channel = after.channel
      vc = await voice_channel.connect()
      vc.play(discord.FFmpegPCMAudio('assets/sounds/intros/generic/whatsup.m4a'))
      # Wait for the audio to finish playing
      while vc.is_playing():
        await asyncio.sleep(1)

async def setup(bot):
  await bot.add_cog(VoiceEvents(bot))
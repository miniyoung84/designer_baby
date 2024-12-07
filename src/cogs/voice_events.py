import asyncio
import discord
from discord.ext import commands

class VoiceEvents(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  async def get_oldest_intro_sound(self, discord_id):
    """
    Fetch the oldest unplayed intro sound for the user,
    falling back to a generic sound if no user-specific sound is found.
    """
    query = """
      SELECT id, file_name 
      FROM yourapp_introsound 
      WHERE user_id = (SELECT id FROM yourapp_discorduser WHERE discord_id = %s)
      ORDER BY last_played ASC LIMIT 1
    """
    params = (discord_id,)
    sound = await self.bot.db_manager.execute_with_retries(query, params, fetchone=True)

    if not sound:
      # If no user-specific intro sound, fetch the oldest generic sound
      query = """
        SELECT id, file_name 
        FROM yourapp_introsound 
        WHERE generic = true
        ORDER BY last_played ASC LIMIT 1
      """
      sound = await self.bot.db_manager.execute_with_retries(query, fetchone=True)
    
    return sound  # Returns (id, file_name) or None

  async def update_last_played(self, intro_sound_id):
    """
    Update the last_played timestamp for the intro sound.
    """
    query = """
      UPDATE yourapp_introsound 
      SET last_played = NOW() 
      WHERE id = %s
    """
    params = (intro_sound_id,)
    await self.bot.db_manager.execute_with_retries(query, params)

  @commands.Cog.listener()
  async def on_voice_state_update(self, member, before, after):
    # Check if the user joined a voice channel
    if member.id == 448359829132804100:
      return
    if before.channel != after.channel:
      print("Ok here we go")
      if not (member.guild.voice_client is None):
        await member.guild.voice_client.disconnect()

      intro_sound = await self.get_oldest_intro_sound(member.id)

      if intro_sound:
        intro_sound_id, file_name = intro_sound

        await self.update_last_played(intro_sound_id)

        voice_channel = after.channel
        vc = await voice_channel.connect()
        vc.play(discord.FFmpegPCMAudio(f'assets/sounds/{file_name}'))

        while vc.is_playing():
          await asyncio.sleep(1)
      else:
        print("No intro sound available.")

async def setup(bot):
  await bot.add_cog(VoiceEvents(bot))
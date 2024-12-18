import asyncio
import discord
import json
from discord.ext import commands
import datetime
from zoneinfo import ZoneInfo

class VoiceEvents(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  async def get_oldest_intro_sound(self, discord_id, max_length=None):
    """
    Fetch the oldest unplayed intro sound for the user,
    considering the max_length restriction and conditions.
    Falls back to a generic sound if no user-specific sound is found.
    """
    today = datetime.datetime.now(ZoneInfo("America/Chicago")).date()
    weekday = today.weekday()  # Monday = 0, Sunday = 6

    query = """
        SELECT id, file_name, length, condition, generic
        FROM bakery_introsound 
        WHERE user_id = (SELECT id FROM bakery_discorduser WHERE discord_id = %s)
    """
    params = [discord_id]

    # Apply max length restriction if provided
    if max_length is not None:
      query += " AND length <= %s"
      params.append(max_length)

    query += " ORDER BY last_played ASC"

    sounds = await self.bot.db_manager.execute_with_retries(query, params, fetchall=True)
    for sound in sounds:
      sound_id, file_name, length, condition = sound

      # Check the condition field
      if condition:
        condition_data = json.loads(condition)  # Ensure condition is parsed
        if "weekday" in condition_data:
          required_weekday = condition_data["weekday"].lower()[:3]  # Normalize to "mon", "tue", etc.
          current_weekday = today.strftime("%a").lower()
          if required_weekday != current_weekday:
            # Skip this sound if it doesn't match today's weekday
            continue

      # Return the first valid sound
      return sound

    # If no user-specific intro sound, fetch the oldest generic sound
    query = """
        SELECT id, file_name, length, condition, generic
        FROM bakery_introsound
        WHERE generic = true
    """
    params = []
    if max_length is not None:
      query += " AND length <= %s"
      params.append(max_length)

    query += " ORDER BY last_played ASC"

    sounds = await self.bot.db_manager.execute_with_retries(query, params, fetchall=True)
    for sound in sounds:
      sound_id, file_name, length, condition = sound

      # Check the condition field
      if condition:
        condition_data = json.loads(condition)  # Ensure condition is parsed
        if "weekday" in condition_data:
          required_weekday = condition_data["weekday"].lower()[:3]  # Normalize to "mon", "tue", etc.
          current_weekday = today.strftime("%a").lower()
          if required_weekday != current_weekday:
            # Skip this sound if it doesn't match today's weekday
            continue

      # Return the first valid generic sound
      return sound

    # No valid intro sound found
    return None

  async def update_last_played(self, intro_sound_id):
    """
    Update the last_played timestamp for the intro sound.
    """
    query = """
      UPDATE bakery_introsound 
      SET last_played = NOW() 
      WHERE id = %s
    """
    params = (intro_sound_id,)
    await self.bot.db_manager.execute_with_retries(query, params)

  @commands.Cog.listener()
  async def on_voice_state_update(self, member, before, after):
    try:
      # Check if the user joined a new voice channel
      if before.channel == after.channel or after.channel is None:
        return

      # Check if the bot should ignore specific user IDs
      if member.id in [448359829132804100, 1161869786020597781]:
        return

      # Fetch the max length for the voice channel
      query = """
          SELECT max_length 
          FROM bakery_discordchannel 
          WHERE discord_id = %s
      """
      params = (after.channel.id,)
      channel_info = await self.bot.db_manager.execute_with_retries(query, params, fetchall=False)
      max_length = channel_info[0] if channel_info else None

      # Fetch an intro sound that fits the max length (if applicable)
      intro_sound = await self.get_oldest_intro_sound(member.id, max_length)
      if intro_sound:
        intro_sound_id, file_name, _, _, generic = intro_sound

        # Update the last played timestamp
        await self.update_last_played(intro_sound_id)

        voice_client = member.guild.voice_client
        if voice_client and voice_client.is_connected():
          await voice_client.disconnect()

        # Connect to the voice channel and play the intro sound
        try:
          voice_channel = after.channel
          vc = await voice_channel.connect()
          if generic:
            vc.play(discord.FFmpegPCMAudio(f'./assets/sounds/intros/generic/{file_name}'))
          else:
            vc.play(discord.FFmpegPCMAudio(f'./assets/sounds/intros/{member.id}/{file_name}'))

        except Exception as e:
            print(f"Error playing intro sound for {member.id}: {e}")
      else:
        print("No intro sound available or it exceeds the max length.")
    except Exception as e:
      print(f"Error in voice state update: {e}")

async def setup(bot):
  await bot.add_cog(VoiceEvents(bot))
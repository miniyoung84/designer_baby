from discord.ext import commands
from discord.ext.commands import Context, Cog
from discord import app_commands, Game

IS_ENABLED = True

class CommsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_check(self, ctx: Context):
        if (not IS_ENABLED):
            await ctx.send('This Cog is disabled')
        return IS_ENABLED
    
    @Cog.listener("on_message")
    async def ping(self, message):
        if message.author == self.bot.user:
            return
        print("message", message.content)
        channel_id = message.channel.id
        print("hi")
        await self.bot.cursor.execute("""SELECT dc.id, dc.discord_id 
        FROM bakery_discordchannel dc 
        JOIN ramen_player rp on dc.discord_id = rp.discord_channel_id
        WHERE dc.discord_id = %s;
        """, (channel_id,))
        print("oof")
        exists = await self.bot.cursor.fetchone()
        print("exists", exists)
        pings = ["p", "ping"]
        if message.content.lower() in pings and exists:
            await message.channel.send('Hello again')
        await self.client.process_commands(message)

async def setup(bot):
    await bot.add_cog(CommsCog(bot))
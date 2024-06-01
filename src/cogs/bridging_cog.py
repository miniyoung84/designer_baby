from discord.ext import commands
from discord import app_commands
from discord.ext.commands import Context, Cog
from discord import Interaction

IS_ENABLED = True

class BridgingCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.pid = '<@&1240595913261711391>'

    async def cog_check(self, ctx: Context):
        if (not IS_ENABLED):
            await ctx.send('This Cog is disabled')
        return IS_ENABLED

    @Cog.listener("on_message")
    async def ping(self, message):
        
        if message.author == self.bot.user:
            if message.content.lower() in ["p", "ping", ";p", "mp", "mping", ";mp", "aa", ";a", "maa", ";ma"]:
                await message.channel.send(f"[Awaiting Player... | {self.pid}]")

        if message.author == self.bot.user:
            pass
        
        await self.bot.process_commands(message)

    @app_commands.command()
    async def bridge(self, ctx: Interaction):
        
        await ctx.response.send_message('A Two-Way Connection has been established with ')

    @app_commands.command()
    @commands.has_role("IC6 Moderator")
    async def unbridge(self, ctx: Interaction):
        
        await ctx.response.send_message('A Two-Way Connection has been de-established with ')

async def setup(bot):
    await bot.add_cog(BridgingCog(bot))
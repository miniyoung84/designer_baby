from discord.ext import commands
from discord import app_commands
from discord.ext.commands import Context
from discord import Interaction

IS_ENABLED = True

class CustomCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        fp = open('connections.txt', 'w+')

    async def cog_check(self, ctx: Context):
        if (not IS_ENABLED):
            await ctx.send('This Cog is disabled')
        return IS_ENABLED

    @Cog.listener("on_message")
    async def ping(self, message):
        if self.connections == {}:
            return

    @app_commands.command()
    async def bridge(self, ctx: Interaction):
        
        await ctx.response.send_message('A Two-Way Connection has been established with ')

async def setup(bot):
    await bot.add_cog(CustomCog(bot))
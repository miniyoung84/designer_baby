from discord.ext import commands
from discord import app_commands
from discord.ext.commands import Context
from discord import Interaction

IS_ENABLED = True

class CustomCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_check(self, ctx: Context):
        if (not IS_ENABLED):
            await ctx.send('This Cog is disabled')
        return IS_ENABLED

    @app_commands.command()
    async def something(self, ctx: Interaction):
        await ctx.response.send_message('Testing changes 3')

    @commands.command()
    async def test_something(self, ctx: Context):
        await ctx.send('Testing something')

async def setup(bot):
    await bot.add_cog(CustomCog(bot))

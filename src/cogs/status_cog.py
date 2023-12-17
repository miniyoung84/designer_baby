from discord.ext import commands
from discord import app_commands
from discord.ext.commands import Context
from discord import Interaction
from discord import Client
from discord import Game
from discord import Status

IS_ENABLED = True

class StatusCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_check(self, ctx: Context):
        if (not IS_ENABLED):
            await ctx.send('This Cog is disabled')
        return IS_ENABLED

    @app_commands.command()
    async def status(self, ctx, status: str):
        game = Game(status)
        await self.bot.change_presence(status=Status.idle, activity=game)
        await ctx.response.send_message('Status updated to: ' + status)

async def setup(bot):
    await bot.add_cog(StatusCog(bot))
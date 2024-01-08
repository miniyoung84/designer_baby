from discord.ext import commands
from discord import app_commands, File
from discord.ext.commands import Context

IS_ENABLED = True

class MapCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_check(self, ctx: Context):
        if (not IS_ENABLED):
            await ctx.send('This Cog is disabled')
        return IS_ENABLED

    @app_commands.command()
    async def map(self, ctx, map_type: str):
        region=str(region)
        region=region.upper()
        if region=="KURU":
            await ctx.send(file=File("./Content/Kuru.JPG"))
        else:
            await ctx.send(file=File("./Content/Mars2.png"))

async def setup(bot):
    await bot.add_cog(MapCog(bot))
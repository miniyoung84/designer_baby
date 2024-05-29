from discord.ext import commands
from discord.ext.commands import Context, Cog
from discord import app_commands, Game, Status

IS_ENABLED = True

class CommsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_check(self, ctx: Context):
        if (not IS_ENABLED):
            await ctx.send('This Cog is disabled')
        return IS_ENABLED
    
    @Cog.listener("on_message")
    async def greet(self,message):
        Cheers= ["Hi", "hi", "Hello", "hello"]
        if message.content in Cheers:
            await message.channel.send('Hello again')
            await self.client.process_commands(message)

    @app_commands.command()
    async def status(self, ctx, status: str):
        game = Game(status)
        await self.bot.change_presence(status=Status.idle, activity=game)
        await ctx.response.send_message('Status updated to: ' + status)

async def setup(bot):
    await bot.add_cog(CommsCog(bot))
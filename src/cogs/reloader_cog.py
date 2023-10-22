from discord.ext import commands
from discord import app_commands
from discord.ext.commands import Context
from discord import Interaction

IS_ENABLED = False

# For some reason using os.listdir breaks the entire module
class ReloaderCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_check(self, ctx: Context):
        if (not IS_ENABLED):
            await ctx.send('This Cog is disabled')
        return IS_ENABLED

    @commands.command()
    async def asomething(self, ctx: Interaction):
        await print('something'.join(os.listdir('src/'), ' '))

    @app_commands.command()
    async def reload(self, ctx: Interaction):
        print('something'.join(os.listdir('src/cogs'), ' '))
        extension_string = ''
        for filename in os.listdir('src/cogs'):
            print('Definitely here')
            if (filename.endswith('.py') and not filename.startswith('reloader_cog')):
                print('Definitely here')
                await self.bot.reload_extension(f'cogs.{filename[:-3]}')
                extension_string = extension_string.join(f'cogs.{filename[:-3]}\n')

        print('reaches here')
        #if (extension_string.equals('')):
        #await ctx.reply('Nothing was reloaded.')
        #else:
        await ctx.response.send_message('Reloaded the following Cogs:\n', hidden=True)
        print('reaches here?')

async def setup(bot):
    await bot.add_cog(ReloaderCog(bot))

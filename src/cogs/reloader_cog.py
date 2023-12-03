import os

from discord.ext import commands
from discord import app_commands
from discord.ext.commands import Context
from discord import Interaction

IS_ENABLED = False

class ReloaderCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_check(self, ctx: Context):
        if (not IS_ENABLED):
            await ctx.send('This Cog is disabled')
        return IS_ENABLED

    @app_commands.command()
    async def reload(self, ctx: Interaction):
        extension_string = ''
        for filename in os.listdir('src/cogs'):
            if (filename.endswith('.py') and not filename.startswith('reloader_cog')):
                await self.bot.reload_extension(f'cogs.{filename[:-3]}')
                extension_string = ''.join(f'\tcogs.{filename[:-3]}\n')


        if (extension_string == ''):
            await ctx.reply('Nothing was reloaded.')
        else:
            await ctx.response.send_message('Reloaded the following Cogs:\n' + extension_string)

async def setup(bot):
    await bot.add_cog(ReloaderCog(bot))

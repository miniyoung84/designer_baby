from discord.ext import commands
from discord import app_commands
from discord.ext.commands import Context
from discord import Interaction
import pickle

IS_ENABLED = True

class NPCCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.model = None

    async def cog_check(self, ctx: Context):
        if (not IS_ENABLED):
            await ctx.send('This Cog is disabled')
        return IS_ENABLED

    async def load_from_file(self):
        self.model = pickle.load(open('../ramen/nn_models/model.p', 'rb'))

    @app_commands.command()
    async def make_npc(self, ctx: Interaction):
        if self.model == None:
            self.load_from_file()
        await ctx.response.send_message('uh')

async def setup(bot):
    await bot.add_cog(NPCCog(bot))
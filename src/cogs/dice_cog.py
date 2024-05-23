from discord import Interaction, Embed, app_commands
from discord.ext import commands
from discord.ext.commands import Context
from discord.ui import View
from typing import Optional

IS_ENABLED = True

class DiceCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_check(self, ctx: Context):
        if (not IS_ENABLED):
            await ctx.send('This Cog is disabled')
        return IS_ENABLED

    def parse_dice_notation(self, notation: str):
        number_of_dice, die_faces = map(int, dice_notation.split('d'))
        return number_of_dice, die_faces

    def build_help_embed(self) -> Embed:
        help_string = (
            '`/roll <dice_notation> [target] [leniency]`\n\n'
            'Rolls a set of dice and evaluates the result based on a target value and leniency.\n\n'
            '**Parameters:**\n'
            '- *dice_notation*: Specifies the number and type of dice to roll, following the format \'NdM\','
            ' where N is the number of dice and M is the number of sides on each die.\n'
            '- *target*: (Optional) Specifies the target value to achieve. If not provided, defaults to 0.\n'
            '- *leniency*: (Optional) Specifies the leniency factor, which determines the range of success or'
            ' failure around the target value. If not provided, defaults to 0.0.\n'
        )

        return Embed(title='Command Info', description=help_string)

    def build_roll_embed(self, roll: int, notation: str) -> Embed:
        description = (
            f'You have rolled a {roll}!'
        )

        return Embed(title=notation, description=description)

    @app_commands.command()
    async def roll(self, ctx, notation: str, target: Optional[int] = None, leniency: float = 0.0):
        if (notation.strip().lower() == 'help'):
            await ctx.response.send_message(embed=self.build_help_embed())
            return

        if (target is not None and target < 0):
            await ctx.response.send_message('Please choose a target.')
            return

        await ctx.response.send_message(embed=self.build_roll_embed(69, notation))
        return

        

async def setup(bot):
    await bot.add_cog(DiceCog(bot))

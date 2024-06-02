from discord import Interaction, Embed, app_commands
from discord.ext import commands
from discord.ext.commands import Context
from discord.ui import View
from typing import Optional
from random import randint
from enum import Enum, auto

IS_ENABLED = True

class Outcome(Enum):
    CRITICAL_FAILURE = auto()
    FAILURE = auto()
    PARTIAL_SUCCESS = auto()
    SUCCESS = auto()
    GREATER_SUCCESS = auto()
    CRITICAL_SUCCESS = auto()
    INVALID_ROLL_PING_MODERATOR = auto()

OUTCOME_COLORS = {
    Outcome.CRITICAL_FAILURE: '#FF0000',  # Red
    Outcome.FAILURE: '#FF4500',           # Orange-Red
    Outcome.PARTIAL_SUCCESS: '#FFA500',   # Orange
    Outcome.SUCCESS: '#008000',           # Green
    Outcome.GREATER_SUCCESS: '#00C000',   # Brighter Green
    Outcome.CRITICAL_SUCCESS: '#00FF00',  # Brightest Green
    Outcome.INVALID_ROLL_PING_MODERATOR: '#000000'  # Black
}

class DiceCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_check(self, ctx: Context):
        if (not IS_ENABLED):
            await ctx.send('This Cog is disabled')
        return IS_ENABLED

    def parse_dice_notation(self, notation: str):
        number_of_dice, die_faces = map(int, notation.split('d'))
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
            ' failure around the target value. If not provided, defaults to 0.0. Internally capped at 1.0\n'
        )

        return Embed(title='Command Info', description=help_string)

    def build_roll_embed(self, roll: int, notation: str, target: Optional[int] = None, leniency: float = 0.0, outcome: Outcome = None) -> Embed:
        description = (
            (f'Target: {target}\n' if target is not None else '') +
            (f'Leniency: {leniency}\n\n' if leniency else '') +
            (f'You have rolled a {roll}!\n\n') +
            (f'Outcome: {outcome.name}\n' if outcome else '')
        )

        hex_color = OUTCOME_COLORS.get(outcome, "#000000")
        color = int(hex_color.lstrip('#'), 16)

        return Embed(title=notation, description=description, color=color)

    def determine_outcome(self, roll: int, notation: str, target: Optional[int] = None, leniency: float = 0.0) -> Outcome:
        number_of_dice, die_faces = self.parse_dice_notation(notation)
        minimum_roll = number_of_dice
        maximum_roll = number_of_dice * die_faces

        critical_failure_value = minimum_roll
        failure_upper_threshold = target - (target - number_of_dice) * leniency
        partial_success_upper_threshold = target
        normal_success_upper_threshold = target + (maximum_roll - target) * leniency
        greater_success_upper_threshold = maximum_roll
        critical_success_value = maximum_roll

        if (roll == critical_success_value):
            return Outcome.CRITICAL_SUCCESS
        elif (roll == critical_failure_value):
            return Outcome.CRITICAL_FAILURE
        elif (roll < failure_upper_threshold):
            return Outcome.FAILURE
        elif (roll < partial_success_upper_threshold):
            return Outcome.PARTIAL_SUCCESS
        elif (roll < normal_success_upper_threshold):
            return Outcome.SUCCESS
        elif (roll < greater_success_upper_threshold):
            return Outcome.GREATER_SUCCESS
        else:
            return Outcome.INVALID_ROLL_PING_MODERATOR
        

    @app_commands.command()
    async def roll(self, ctx, notation: str, target: Optional[int] = None, leniency: float = 0.0):
        if (notation.strip().lower() == 'help'):
            await ctx.response.send_message(embed=self.build_help_embed())
            return

        number_of_dice, die_faces = self.parse_dice_notation(notation)
        minimum_roll = number_of_dice
        maximum_roll = number_of_dice * die_faces
        capped_leniency = min(leniency, 1.0)

        if (number_of_dice > 100 or number_of_dice < 1):
            await ctx.response.send_message('Please choose a valid number of dice (1-100).')
            return

        if (die_faces > 1000000 or die_faces < 4):
            await ctx.response.send_message('Please choose a valid number of die faces (4-1000000)')
            return

        if (target is None):
            random_roll_total = sum(randint(1, die_faces) for _ in range(number_of_dice))
            await ctx.response.send_message(embed=self.build_roll_embed(random_roll_total, notation, None, 0.0, None))
            return

        if (target < minimum_roll or target > maximum_roll):
            await ctx.response.send_message('Please choose a valid target.')
            return

        random_roll_total = sum(randint(1, die_faces) for _ in range(number_of_dice))
        outcome = self.determine_outcome(random_roll_total, notation, target, capped_leniency)

        await ctx.response.send_message(embed=self.build_roll_embed(random_roll_total, notation, target, capped_leniency, outcome))
        return
        

async def setup(bot):
    await bot.add_cog(DiceCog(bot))

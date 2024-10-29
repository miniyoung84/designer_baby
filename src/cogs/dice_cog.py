import discord
import numpy as np
from discord import app_commands, Interaction, Embed
from discord.ext import commands
from discord.ext.commands import Context
from discord.ui import Button, View
from typing import Optional, Tuple
from random import randint
from enum import Enum

IS_ENABLED = True

class Outcome(Enum):
    CRITICAL_FAILURE = 'CRITICAL FAIL'
    FAILURE = 'FAIL'
    PARTIAL_SUCCESS = 'PARTIAL CREDIT'
    SUCCESS = 'PASS'
    GREATER_SUCCESS = 'ACED'
    CRITICAL_SUCCESS = 'EXTRA CREDIT'
    INVALID_ROLL_PING_MODERATOR = 'Player did not roll'

OUTCOME_COLORS = {
    Outcome.CRITICAL_FAILURE: '#FF0000',
    Outcome.FAILURE: '#FF4500',
    Outcome.PARTIAL_SUCCESS: '#FFA500',
    Outcome.SUCCESS: '#008000',
    Outcome.GREATER_SUCCESS: '#00C000',
    Outcome.CRITICAL_SUCCESS: '#00FF00',
    Outcome.INVALID_ROLL_PING_MODERATOR: '#000000'
}

class RollDeclineView(View):
    def __init__(self, notation: str, target: Optional[int], leniency: float, bot: commands.Bot, ctx: Interaction):
        super().__init__(timeout=None)
        self.notation = notation
        self.target = target
        self.leniency = leniency
        self.bot = bot
        self.ctx = ctx

    @discord.ui.button(label="Roll", style=discord.ButtonStyle.green)
    async def roll(self, interaction: Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        dice_cog = self.bot.get_cog('DiceCog')
        if dice_cog:
            await dice_cog.execute_roll(interaction, self.notation, self.target, self.leniency)
        self.stop()

    @discord.ui.button(label="Decline", style=discord.ButtonStyle.red)
    async def decline(self, interaction: Interaction, button: discord.ui.Button):
        await interaction.response.send_message("You have declined the roll.", ephemeral=False)
        self.stop()

class ForcedRollView(View):
    def __init__(self, notation: str, target: Optional[int], leniency: float, bot: commands.Bot, ctx: Interaction):
        super().__init__(timeout=None)
        self.notation = notation
        self.target = target
        self.leniency = leniency
        self.bot = bot
        self.ctx = ctx

    @discord.ui.button(label="Roll", style=discord.ButtonStyle.green)
    async def roll(self, interaction: Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        dice_cog = self.bot.get_cog('DiceCog')
        if dice_cog:
            await dice_cog.execute_roll(interaction, self.notation, self.target, self.leniency)
        self.stop()

class DiceCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_check(self, ctx: Context):
        if not IS_ENABLED:
            await ctx.send('This Cog is disabled')
        return IS_ENABLED

    def probabilities_ndm(self, N, M):
        single_die_prob = np.full(M, 1 / M)

        # Convolve the single die distribution N times to get the distribution of the sum of N dice
        sum_distribution = single_die_prob
        for _ in range(N - 1):
            sum_distribution = np.convolve(sum_distribution, single_die_prob)

        # Map the result to the possible sum values
        probabilities = {i + N: sum_distribution[i] for i in range(len(sum_distribution))}
        return probabilities

    def build_probabilities_embed(self, notation: str, target: Optional[int] = None, leniency: float = 0.0, title=''):
        number_of_dice, die_faces = self.parse_dice_notation(notation)
        minimum_roll = number_of_dice
        maximum_roll = number_of_dice * die_faces

        critical_failure_value = minimum_roll
        critical_success_value = maximum_roll
        
        outcomes = {}
        probabilities = self.probabilities_ndm(number_of_dice, die_faces)

        if leniency == 0.0:
            outcomes = {
                Outcome.CRITICAL_FAILURE: 0.0,
                Outcome.FAILURE: 0.0,
                Outcome.SUCCESS: 0.0,
                Outcome.CRITICAL_SUCCESS: 0.0,
            }

            for value, probability in probabilities.items():
                if value == critical_success_value:
                    outcomes[Outcome.CRITICAL_SUCCESS] += probability
                elif value == critical_failure_value:
                    outcomes[Outcome.CRITICAL_FAILURE] += probability
                elif value < target:
                    outcomes[Outcome.FAILURE] += probability
                elif value >= target:
                    outcomes[Outcome.SUCCESS] += probability

        else:
            failure_upper_threshold = target - (target - number_of_dice) * leniency
            partial_success_upper_threshold = target
            greater_success_lower_threshold = maximum_roll - (maximum_roll - target) * leniency
            greater_success_upper_threshold = maximum_roll

            outcomes = {
                Outcome.CRITICAL_FAILURE: 0.0,
                Outcome.FAILURE: 0.0,
                Outcome.PARTIAL_SUCCESS: 0.0,
                Outcome.SUCCESS: 0.0,
                Outcome.GREATER_SUCCESS: 0.0,
                Outcome.CRITICAL_SUCCESS: 0.0,
            }

            for value, probability in probabilities.items():
                if value == critical_success_value:
                    outcomes[Outcome.CRITICAL_SUCCESS] += probability
                elif value == critical_failure_value:
                    outcomes[Outcome.CRITICAL_FAILURE] += probability
                elif value < failure_upper_threshold:
                    outcomes[Outcome.FAILURE] += probability
                elif value < partial_success_upper_threshold:
                    outcomes[Outcome.PARTIAL_SUCCESS] += probability
                elif value < greater_success_lower_threshold:
                    outcomes[Outcome.SUCCESS] += probability
                elif value < greater_success_upper_threshold:
                    outcomes[Outcome.GREATER_SUCCESS] += probability

        embed = discord.Embed(title=title)
        description = '\n'.join(f'`{outcome.value:<15}: {probability * 100:>7.2f}%`' for outcome, probability in outcomes.items())
        embed.add_field(name='Probabilities', value=description, inline=False)
        return embed


    def parse_dice_notation(self, notation: str) -> Optional[Tuple[int, int]]:
        try:
            number_of_dice, die_faces = map(int, notation.split('d'))
            return number_of_dice, die_faces
        except ValueError:
            return None

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
            (f'**{notation}**\n') +   
            (f'Leniency: {leniency}\n' if leniency else '') +         
            (f'Target: {target}\n\n' if target is not None else '') +
            (f'You have rolled **{roll}**!')
        )

        hex_color = OUTCOME_COLORS.get(outcome, "#000000")
        color = int(hex_color.lstrip('#'), 16)

        return Embed(title=outcome.value if outcome else notation, description=description, color=color)

    def determine_outcome(self, roll: int, notation: str, target: Optional[int] = None, leniency: float = 0.0) -> Outcome:
        number_of_dice, die_faces = self.parse_dice_notation(notation)
        minimum_roll = number_of_dice
        maximum_roll = number_of_dice * die_faces

        critical_failure_value = minimum_roll
        failure_upper_threshold = target - (target - number_of_dice) * leniency
        normal_success_lower_threshold = target
        greater_success_lower_threshold = maximum_roll - (maximum_roll - target) * leniency
        critical_success_value = maximum_roll

        if leniency == 0.0:
            if roll == critical_success_value:
                return Outcome.CRITICAL_SUCCESS
            elif roll == critical_failure_value:
                return Outcome.CRITICAL_FAILURE
            elif roll < target:
                return Outcome.FAILURE
            elif roll >= target:
                return Outcome.SUCCESS
            else:
                return Outcome.INVALID_ROLL_PING_MODERATOR
        else:
            if roll == critical_success_value:
                return Outcome.CRITICAL_SUCCESS
            elif roll == critical_failure_value:
                return Outcome.CRITICAL_FAILURE
            elif roll < failure_upper_threshold:
                return Outcome.FAILURE
            elif roll < normal_success_lower_threshold:
                return Outcome.PARTIAL_SUCCESS
            elif roll >= normal_success_lower_threshold and roll < greater_success_lower_threshold:
                return Outcome.SUCCESS
            elif roll >= greater_success_lower_threshold:
                return Outcome.GREATER_SUCCESS
            else:
                return Outcome.INVALID_ROLL_PING_MODERATOR

    async def send_message_with_embed(self, ctx: Interaction, content: str, embed: Embed, view: View):
        await ctx.response.send_message(content, embed=embed, view=view)

    @app_commands.command()
    async def roll(self, ctx: Interaction, notation: str, target: Optional[int] = None, leniency: float = 0.0):
        if notation.strip().lower() == 'help':
            await ctx.response.send_message(embed=self.build_help_embed())
            return

        dice_notation = self.parse_dice_notation(notation)
        if dice_notation is None:
            await ctx.response.send_message('Invalid dice notation. Please use the format NdM.')
            return

        view = RollDeclineView(notation, target, leniency, self.bot, ctx)
        embed = self.build_probabilities_embed(notation, target, leniency, 'Do you want to proceed with this roll?')
        await ctx.response.send_message(embed=embed, view=view)

    @app_commands.command()
    async def forced_roll(self, ctx: Interaction, notation: str, target: Optional[int] = None, leniency: float = 0.0):
        if notation.strip().lower() == 'help':
            await ctx.response.send_message(embed=self.build_help_embed())
            return

        dice_notation = self.parse_dice_notation(notation)
        if dice_notation is None:
            await ctx.response.send_message('Invalid dice notation. Please use the format NdM.')
            return

        view = ForcedRollView(notation, target, leniency, self.bot, ctx)
        embed = self.build_probabilities_embed(notation, target, leniency, 'You must proceed with this roll.')
        await ctx.response.send_message(embed=embed, view=view)

    async def execute_roll(self, interaction: Interaction, notation: str, target: Optional[int], leniency: float):
        number_of_dice, die_faces = self.parse_dice_notation(notation)

        capped_leniency = min(leniency, 1.0)

        if number_of_dice > 100 or number_of_dice < 1:
            await interaction.followup.send('Please choose a valid number of dice (1-100).')
            return

        if die_faces > 1000000 or die_faces < 4:
            await interaction.followup.send('Please choose a valid number of die faces (4-1000000)')
            return

        if target is None:
            random_roll_total = sum(randint(1, die_faces) for _ in range(number_of_dice))
            await interaction.followup.send(embed=self.build_roll_embed(random_roll_total, notation, None, 0.0, None))
            return

        minimum_roll = number_of_dice
        maximum_roll = number_of_dice * die_faces
        if target < minimum_roll or target > maximum_roll:
            await interaction.followup.send('Please choose a valid target.')
            return

        random_roll_total = sum(randint(1, die_faces) for _ in range(number_of_dice))
        outcome = self.determine_outcome(random_roll_total, notation, target, capped_leniency)

        await interaction.followup.send(embed=self.build_roll_embed(random_roll_total, notation, target, capped_leniency, outcome))
        return

async def setup(bot):
    await bot.add_cog(DiceCog(bot))


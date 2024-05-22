from discord.ext import commands
from discord import app_commands
from discord.ext.commands import Context
from discord import Interaction
from discord import Embed

import discord

IS_ENABLED = True

class ReportCardCog(commands.Cog):
    grades = {
        0: 'F',
        1: 'D-',
        2: 'D',
        3: 'D+',
        4: 'C-',
        5: 'C',
        6: 'C+',
        7: 'B-',
        8: 'B',
        9: 'B+',
        10: 'A-',
        11: 'A',
        12: 'A+'
    }
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_check(self, ctx: Context):
        if (not IS_ENABLED):
            await ctx.send('This Cog is disabled')
        return IS_ENABLED

    async def get_grade(self, character: str, subject: str) -> str:
        """Pull grade from database"""
        return grades[raw_grade]

    async def build_embed(self, character: str, subjects: list) -> Embed:
        description = ""
        for subject in subjects:
            grade = self.get_grade(character=character, subject=subject)
            description += (subject + ": " + grade + "\n")
        return Embed(title=subject, description=description).set_author(name=character)

    @app_commands.command()
    async def report(self, ctx, character: str):
        # Get the 10 best subjects from the db
        await self.bot.cursor.execute("SELECT * FROM characters LIMIT 10")
        print(await self.bot.cursor.fetchone())
        embed = self.build_embed(character=character, subjects=subjects)
        await ctx.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(ReportCardCog(bot))


class SelectCharacterView(discord.ui.View):
    def __init__(self, characterList: list):
        @discord.ui.select( # the decorator that lets you specify the properties of the select menu
            placeholder = "Select a character", # the placeholder text that will be displayed if nothing is selected
            min_values = 1, # the minimum number of values that must be selected by the users
            max_values = 1, # the maximum number of values that can be selected by the users
            options = [ # the list of options from which users can choose, a required field
                discord.SelectOption(label=character) for character in characterList
            ]
        )
        async def select_callback(self, select, interaction): # the function called when the user is done selecting options
            await interaction.response.send_message(f"Awesome! I like {select.values[0]} too!")

from discord import Interaction, Embed, app_commands, SelectOption
from discord.ext import commands
from discord.ext.commands import Context
from discord.ui import View

IS_ENABLED = True

class ReportCardCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.grades = {
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

    async def cog_check(self, ctx: Context):
        if (not IS_ENABLED):
            await ctx.send('This Cog is disabled')
        return IS_ENABLED

    async def build_embed(self, character: str, subjects: list, grades_value: list) -> Embed:
        description = ""
        grade_iter = 0
        for subject in subjects:
            grade = self.grades[grades_value[grade_iter]]
            description += (subject + ": " + grade + "\n")
            grade_iter += 1
        return Embed(title="Report Card", description=description).set_author(name=character)

    @app_commands.command()
    async def report(self, ctx, character: str):
        # Get the 10 best subjects from the db
        await self.bot.cursor.execute("""SELECT rc.first_name, rc.last_name, rs.name, rg.grade 
            FROM ramen_grade rg 
            JOIN ramen_character rc ON rg.student_id = rc.id
            JOIN ramen_subject rs ON rg.subject_id = rs.id
            WHERE rc.first_name LIKE %s OR rc.last_name LIKE %s OR rc.nick_name LIKE %s;
        """, (character, character, character))
        rows = await self.bot.cursor.fetchall()
        embed = await self.build_embed(character=character, subjects=[row[2] for row in rows], grades_value=[row[3] for row in rows])
        await ctx.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(ReportCardCog(bot))


class SelectCharacterView(View):
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

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

    async def get_gpa(self, grades_value: list) -> int:
        gpa = 0
        for grade in grades_value:
            gpa += (grade/3 + 1/3)
        return gpa / len(grades_value)

    async def build_embed(self, character: str, color: str, subjects: list, grades_value: list) -> Embed:
        grade_iter = 0
        grade_list = ""
        subject_list = ""
        for subject in subjects:
            subject_list += subject + "\n"
            grade = self.grades[grades_value[grade_iter]]
            grade_list += grade + "\n"
            grade_iter += 1
        gpa = await self.get_gpa(grades_value)
        embed = Embed(title="Report Card", description="GPA: " + str(round(gpa, 2)), color=int(color, 16)).set_author(name=character)
        embed.add_field(name="Subject", value=subject_list, inline=True)
        embed.add_field(name="Grade", value=grade_list, inline=True)
        return embed

    @app_commands.command()
    async def report(self, ctx, character: str):
        # Get the 10 best subjects from the db
        await self.bot.cursor.execute("""SELECT rc.first_name, rc.nick_name, rc.last_name, rc.fav_color, rs.name, rg.grade 
            FROM ramen_grade rg 
            JOIN ramen_character rc ON rg.student_id = rc.id
            JOIN ramen_subject rs ON rg.subject_id = rs.id
            WHERE rc.first_name LIKE %s OR rc.last_name LIKE %s OR rc.nick_name LIKE %s;
        """, (character, character, character))
        rows = await self.bot.cursor.fetchall()
        first_name = rows[0][0] if rows[0][0] else ''
        nick_name = '"' + rows[0][1] + '"' if rows[0][1] else ''
        last_name = rows[0][2] if rows[0][2] else ''
        full_character = first_name + ' ' + nick_name + ' ' + last_name
        embed = await self.build_embed(character=full_character, color=rows[0][3], subjects=[row[4] for row in rows], grades_value=[row[5] for row in rows])
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

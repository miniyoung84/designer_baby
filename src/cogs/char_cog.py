from discord import Interaction, Embed, app_commands, SelectOption
from discord.ext import commands
from discord.ext.commands import Context
from discord.ui import View
from datetime import datetime

IS_ENABLED = True

class CharacterCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.status_names = ["Freshman", "Sophomore", "Junior", "Senior"]

    async def cog_check(self, ctx: Context):
        if (not IS_ENABLED):
            await ctx.send('This Cog is disabled')
        return IS_ENABLED

    async def get_gpa(self, grades_value: list) -> int:
        gpa = 0
        for grade in grades_value:
            gpa += (grade/3 + 1/3)
        return gpa / len(grades_value)
    
    async def convert_height(self, height: int) -> str:
      feet = height // 12
      inches = height % 12
      return f"{feet}' {inches}\""
    
    async def convert_date(self, date_str: str) -> str:
      date = datetime.strptime(date_str, "%m-%d")
      month = date.strftime("%B")
      day = date.strftime("%d")
      return f"{month} {day}"

    async def build_embed(self, name: str, pronouns: str, color: str, age: int, birthday: str, 
                          height: str, job: str, year: str, mutations: str, pet:str, major: str,
                          minor: str, primary_weapon: str, secondary_weapon:str, dorm: str) -> Embed:
        embed = Embed(title=name, description=pronouns, color=int(color, 16))
        embed.add_field(name="Age", value=age, inline=True)
        embed.add_field(name="Birthday", value=birthday, inline=True)
        embed.add_field(name="Height", value=height, inline=True)
        embed.add_field(name="Job", value=job, inline=True)
        embed.add_field(name="Year", value=year, inline=True)
        embed.add_field(name="Mutations", value=mutations, inline=True)
        embed.add_field(name="Pet", value=pet, inline=True)
        embed.add_field(name="Major", value=major, inline=True)
        embed.add_field(name="Minor", value=minor, inline=True)
        embed.add_field(name="Primary Weapon", value=primary_weapon, inline=True)
        embed.add_field(name="Secondary Weapon", value=secondary_weapon, inline=True)
        embed.add_field(name="Dorm", value=dorm, inline=True)
        return embed

    @app_commands.command()
    async def char(self, ctx, character: str):
        # Get the 10 best subjects from the db
        character = character.capitalize()
        query = """
            SELECT rc.first_name, rc.nick_name, rc.last_name, rc.pronouns, 
            rc.fav_color, rc.age, rc.birthday, rc.height, rc.job, rc.year, rc.mutations,
            rc.pet, major.name, minor.name, rc.primary_weapon, rc.secondary_weapon, dorm.name
            FROM ramen_character rc 
            JOIN ramen_subject major on rc.major_id = major.id
            JOIN ramen_subject minor on rc.minor_id = minor.id
            JOIN ramen_dorm dorm on rc.dorm_id = dorm.id
            WHERE rc.first_name LIKE %s OR rc.last_name LIKE %s OR rc.nick_name LIKE %s;
        """
        params = (character, character, character)
        rows = await self.bot.db_manager.execute_with_retries(query, params, fetchall=True)
        for row in rows:
            first_name = rows[0][0] if rows[0][0] else ''
            nick_name = f'"{rows[0][1]}"' if rows[0][1] else ''
            last_name = rows[0][2] if rows[0][2] else ''
            full_character = ' '.join(part for part in [first_name, nick_name, last_name] if part)
            height = await self.convert_height(row[7])
            birthday = await self.convert_date(str(row[6])[5:])
            year = self.status_names[int(row[9]) - 1] if row[9] else "Non-Student"
            embed = await self.build_embed(
                name=full_character, pronouns = row[3], color=row[4], 
                age=row[5], birthday=birthday, height=height, job=row[8],
                year=year, mutations=row[10], pet=row[11], major=row[12],
                minor=row[13], primary_weapon=row[14], secondary_weapon=row[15], dorm=row[16]
            )
            await ctx.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(CharacterCog(bot))

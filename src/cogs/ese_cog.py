from discord.ext import commands
from discord import app_commands
from discord.ext.commands import Context
from discord import Interaction

IS_ENABLED = True

class ESECog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_check(self, ctx: Context):
        if (not IS_ENABLED):
            await ctx.send('This Cog is disabled')
        return IS_ENABLED

    @app_commands.command()
    @app_commands.checks.has_role("IC6 Moderator")
    async def ese(self, ctx: Interaction, amount: int):

        await self.bot.cursor.execute("""SELECT rp.id, rp.ese
            FROM ramen_player rp
            JOIN bakery_discordchannel dc on dc.id = rp.channel_id
            WHERE dc.discord_id = %s;
            """, (ctx.channel.id,))
        return_value = await self.bot.cursor.fetchone()

        player_id = return_value[0]
        ese_value = return_value[1]

        await self.bot.cursor.execute("""UPDATE ramen_player
            SET ese = %s
            WHERE id = %s;
            """, (ese_value + amount, player_id))
        await ctx.channel.send('ESE has been updated to ' + str(ese_value + amount))
        await self.bot.db_conn.commit()
        await ctx.response.send_message('Update Successful')

    @app_commands.command()
    async def my_ese(self, ctx: Interaction):

        await self.bot.cursor.execute("""SELECT rp.ese
            FROM ramen_player rp
            JOIN bakery_discordchannel dc on dc.id = rp.channel_id
            WHERE dc.discord_id = %s;
            """, (ctx.channel.id,))
        return_value = await self.bot.cursor.fetchone()

        await ctx.response.send_message('You have ' + str(return_value[0]) + ' ESE value')

async def setup(bot):
    await bot.add_cog(ESECog(bot))
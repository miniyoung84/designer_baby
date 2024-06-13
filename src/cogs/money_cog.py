from discord.ext import commands
from discord import app_commands
from discord.ext.commands import Context
from discord import Interaction

IS_ENABLED = True

class MoneyCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_check(self, ctx: Context):
        if (not IS_ENABLED):
            await ctx.send('This Cog is disabled')
        return IS_ENABLED

    @app_commands.command()
    @app_commands.checks.has_role("IC6 Moderator")
    async def add_income(self, ctx: Interaction):
        await self.bot.cursor.execute("""SELECT rp.id, rp.income, rp.money
            FROM ramen_player rp
            JOIN bakery_discordchannel dc on dc.id = rp.channel_id
            WHERE dc.discord_id = %s;
            """, (ctx.channel.id,))
        return_value = await self.bot.cursor.fetchone()

        player_id = return_value[0]
        income = return_value[1]
        money = return_value[2]

        await self.bot.cursor.execute("""UPDATE ramen_player
            SET money = %s
            WHERE id = %s;
            """, (income + money, player_id))
        await ctx.channel.send('You received $'+ str(income) + ' income and now you have $' + str(income + money))
        await self.bot.db_conn.commit()
        await ctx.response.send_message('Update Successful')

    @app_commands.command()
    @app_commands.checks.has_role("IC6 Moderator")
    async def income(self, ctx: Interaction, amount: int):
        await self.bot.cursor.execute("""SELECT rp.id, rp.income
            FROM ramen_player rp
            JOIN bakery_discordchannel dc on dc.id = rp.channel_id
            WHERE dc.discord_id = %s;
            """, (ctx.channel.id,))
        return_value = await self.bot.cursor.fetchone()

        player_id = return_value[0]
        income = return_value[1]

        await self.bot.cursor.execute("""UPDATE ramen_player
            SET income = %s
            WHERE id = %s;
            """, (income + amount, player_id))
        await ctx.channel.send('Your income is set as $' + str(income + amount))
        await self.bot.db_conn.commit()
        await ctx.response.send_message('Update Successful')

    @app_commands.command()
    @app_commands.checks.has_role("IC6 Moderator")
    async def money(self, ctx: Interaction, amount: int):

        await self.bot.cursor.execute("""SELECT rp.id, rp.money
            FROM ramen_player rp
            JOIN bakery_discordchannel dc on dc.id = rp.channel_id
            WHERE dc.discord_id = %s;
            """, (ctx.channel.id,))
        return_value = await self.bot.cursor.fetchone()

        player_id = return_value[0]
        money = return_value[1]

        await self.bot.cursor.execute("""UPDATE ramen_player
            SET money = %s
            WHERE id = %s;
            """, (money + amount, player_id))
        await ctx.channel.send('You now have $' + str(money + amount))
        await self.bot.db_conn.commit()
        await ctx.response.send_message('Update Successful')

    @app_commands.command()
    async def my_money(self, ctx: Interaction):

        await self.bot.cursor.execute("""SELECT rp.money
            FROM ramen_player rp
            JOIN bakery_discordchannel dc on dc.id = rp.channel_id
            WHERE dc.discord_id = %s;
            """, (ctx.channel.id,))
        return_value = await self.bot.cursor.fetchone()

        await ctx.response.send_message('You have $' + str(return_value[0]))

async def setup(bot):
    await bot.add_cog(MoneyCog(bot))
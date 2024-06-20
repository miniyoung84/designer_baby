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
        query1 = """SELECT rp.id, rp.ese
            FROM ramen_player rp
            JOIN bakery_discordchannel dc on dc.id = rp.channel_id
            WHERE dc.discord_id = %s;
        """
        params1 = (ctx.channel.id,)
        return_value = await self.bot.db_manager.execute_with_retries(query1, params1)

        player_id = return_value[0]
        ese_value = return_value[1]
        new_ese_value = ese_value + amount

        query2 = """UPDATE ramen_player
            SET ese = %s
            WHERE id = %s;
        """
        params2 = (new_ese_value, player_id)

        await self.bot.db_manager.execute_with_retries(query2, params2)
        await ctx.channel.send(f'ESE has changed by {str(amount)} to {str(new_ese_value)}')
        await self.bot.db_manager.commit()
        await ctx.response.send_message('Update Successful')

    @app_commands.command()
    async def my_ese(self, ctx: Interaction):
        query = """SELECT rp.ese
            FROM ramen_player rp
            JOIN bakery_discordchannel dc on dc.id = rp.channel_id
            WHERE dc.discord_id = %s;
        """
        params = (ctx.channel.id,)
        return_value = await self.bot.db_manager.execute_with_retries(query, params)

        await ctx.response.send_message('Your ESE is ' + str(return_value[0]))

async def setup(bot):
    await bot.add_cog(ESECog(bot))

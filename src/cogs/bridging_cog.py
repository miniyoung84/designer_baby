from discord.ext import commands
from discord import app_commands
from discord.ext.commands import Context, Cog
from discord import Interaction

IS_ENABLED = True

class BridgingCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.pid = '<@&1240595913261711391>'

    async def cog_check(self, ctx: Context):
        if (not IS_ENABLED):
            await ctx.send('This Cog is disabled')
        return IS_ENABLED

    @Cog.listener("on_message")
    async def message_forward(self, message):
        
        if message.author == self.bot.user:
            return
        
        await self.bot.cursor.execute("""SELECT rpc.to_player_id 
            FROM ramen_player_connections rpc
            JOIN ramen_player rp on rpc.from_player_id = rp.id
            WHERE rp.discord_user_id = %s;
            """, (message.author.id,))
        conn_ids = await self.bot.cursor.fetchall()
        if not conn_ids:
            return
        
        for player_id in conn_ids:



    @app_commands.command()
    async def bridge(self, ctx: Interaction, player: int):
        
        await self.bot.cursor.execute("""SELECT rp.player_id, rp.name 
            FROM ramen_player rp
            WHERE rp.channel_id = %s;
            """, (ctx.channel_id,))
        player_parts = await self.bot.cursor.fetchone()
        (player_id, name) = player_parts

        await self.bot.cursor.execute("""SELECT rpc.to_player_id 
            FROM ramen_player_connections rpc
            JOIN ramen_player rp on rpc.from_player_id = rp.id
            WHERE rp.discord_user_id = %s;
            """, (message.author.id,))

        await self.bot.cursor.execute("INSERT INTO ramen_player_connections VALUES (%s, %s);", (player, player_id))
        await self.bot.cursor.execute("INSERT INTO ramen_player_connections VALUES (%s, %s);", (player_id, player))

        await ctx.response.send_message('A Multi-Way Connection has been established with ')

    @app_commands.command()
    @commands.has_role("IC6 Moderator")
    async def unbridge(self, ctx: Interaction):
        
        await ctx.response.send_message('A Two-Way Connection has been de-established with ')

async def setup(bot):
    await bot.add_cog(BridgingCog(bot))
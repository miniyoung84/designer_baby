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

        if message.content.startswith('('):
            return
        
        await self.bot.cursor.execute("""SELECT rpc.to_player_id 
            FROM ramen_player_connections rpc
            JOIN ramen_player rp on rpc.from_player_id = rp.id
            WHERE rp.discord_user_id = %s;
            """, (message.author.id,))
        conn_ids = await self.bot.cursor.fetchall()
        if not conn_ids:
            return
        
        player_name = None
        if ctx.user.id != 294867951855599618:
            await self.bot.cursor.execute("""SELECT rp.name
                FROM ramen_player rp
                WHERE rp.discord_user_id = %s;
                """, (message.author.id,))
            player_name = await self.bot.cursor.fetchone()

        for player_id in conn_ids:
            await self.bot.cursor.execute("""SELECT rp.channel_id
            FROM ramen_player rp
            WHERE rp.player_id = %s;
            """, (player_id,))
            channel_id = await self.bot.cursor.fetchone()
            channel = await self.bot.get_channel(channel_id)
            if player_name == None:
                await channel.response.send_message(message.content)
            else:
                await channel.response.send_message(f'[{player_name}]' + message.content)

    @app_commands.command()
    async def bridge(self, ctx: Interaction, player: int):
        
        await self.bot.cursor.execute("""SELECT rp.player_id
            FROM ramen_player rp
            WHERE rp.channel_id = %s;
            """, (ctx.channel_id,))
        player_id = await self.bot.cursor.fetchone()

        await self.bot.cursor.execute("""SELECT rpc.to_player_id
            FROM ramen_player_connections rpc
            WHERE rpc.from_player_id = %s;
            """, (player,))
        first_players = await self.bot.cursor.fetchall()
        if first_players:
            first_players += player
        else:
            first_players = (player,)

        await self.bot.cursor.execute("""SELECT rpc.to_player_id
            FROM ramen_player_connections rpc
            WHERE rpc.from_player_id = %s;
            """, (player_id,))
        second_players = await self.bot.cursor.fetchall()
        if second_players:
            second_players += player_id
        else:
            second_players = (player_id,)

        for player1 in first_players:
            for player2 in second_players:
                await self.bot.cursor.execute("INSERT INTO ramen_player_connections VALUES (%s, %s);", (player, player_id))
                await self.bot.cursor.execute("INSERT INTO ramen_player_connections VALUES (%s, %s);", (player_id, player))

        for player1 in first_players:
            await self.bot.cursor.execute("""SELECT rp.channel_id
            FROM ramen_player rp
            WHERE rp.player_id = %s;
            """, (player1,))
            channel_id = await self.bot.cursor.fetchone()
            channel = await self.bot.get_channel(channel_id)
            second_names = ''
            for player2 in second_players:
                await self.bot.cursor.execute("""SELECT rp.name
                FROM ramen_player rp
                WHERE rp.player_id = %s;
                """, (player2,))
                name = await self.bot.cursor.fetchone()
                second_names += name
            await channel.response.send_message('A Multi-Way Connection has been established with players ' + second_names)

        for player2 in second_players:
            await self.bot.cursor.execute("""SELECT rp.channel_id
            FROM ramen_player rp
            WHERE rp.player_id = %s;
            """, (player2,))
            channel_id = await self.bot.cursor.fetchone()
            channel = await self.bot.get_channel(channel_id)
            first_names = ''
            for player1 in first_players:
                await self.bot.cursor.execute("""SELECT rp.name
                FROM ramen_player rp
                WHERE rp.player_id = %s;
                """, (player1,))
                name = await self.bot.cursor.fetchone()
                first_names += name
            await channel.response.send_message('A Multi-Way Connection has been established with players ' + first_names)

    @app_commands.command()
    @commands.has_role("IC6 Moderator")
    async def unbridge(self, ctx: Interaction):
        
        await ctx.response.send_message('A Two-Way Connection has been de-established with ')

async def setup(bot):
    await bot.add_cog(BridgingCog(bot))
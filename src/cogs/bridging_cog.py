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
        # Check if the cog is enabled
        if (not IS_ENABLED):
            await ctx.send('This Cog is disabled')
        return IS_ENABLED
    
    @app_commands.command()
    async def party(self, ctx: Interaction):
        # Retrieve player connections from the database
        await self.bot.cursor.execute("""SELECT rpc.to_player_id
            FROM ramen_player_connections rpc
            JOIN ramen_player rp on rpc.from_player_id = rp.id
            JOIN bakery_discordchannel dc on dc.id = rp.channel_id
            WHERE dc.discord_id = %s;
            """, (ctx.channel.id,))
        connections = await self.bot.cursor.fetchall()
        player_ids = [player[0] for player in connections]
        if player_ids:
            for player_id in player_ids:
                player_names_str = ', '.join(str(player_id))
            await ctx.response.send_message(f"Connected with Players: {player_names_str}")
        else:
            await ctx.response.send_message("No Active Connections Detected")

    @Cog.listener("on_message")
    async def message_forward(self, message):
        # Forward messages to connected players
        if message.author == self.bot.user:
            return

        if message.content.startswith('('):
            return
        
        await self.bot.cursor.execute("""SELECT rpc.to_player_id 
            FROM ramen_player_connections rpc
            JOIN ramen_player rp on rpc.from_player_id = rp.id
            JOIN bakery_discordchannel dc on dc.id = rp.channel_id
            WHERE dc.discord_id = %s;
            """, (message.channel.id,))
        conn_ids = await self.bot.cursor.fetchall()
        if not conn_ids:
            return
        
        player_name = None
        if message.author.id != 294867951855599618:
            await self.bot.cursor.execute("""SELECT rc.first_name, rc.last_name, rc.nick_name
                FROM ramen_character rc
                JOIN ramen_player rp on rp.id = rc.player_id
                JOIN bakery_discorduser du on du.id = rp.discord_user_id
                WHERE du.discord_id = %s;
                """, (message.author.id,))
            player_name = await self.bot.cursor.fetchone()

        for player_id in conn_ids:
            await self.bot.cursor.execute("""SELECT dc.discord_id
            FROM ramen_player rp
            JOIN bakery_discordchannel dc on dc.id = rp.channel_id
            WHERE rp.id = %s;
            """, (player_id[0],))
            channel_id = await self.bot.cursor.fetchone()
            channel = self.bot.get_channel(channel_id[0])
            if player_name == None:
                await channel.send(message.content)
            else:
                player_name = player_name[2] if player_name[2] else (player_name[0] if player_name[0] else player_name[1])
                await channel.send(f'{player_name}: ' + message.content)

    @app_commands.command()
    @app_commands.checks.has_role("IC6 Moderator")
    async def bridge(self, ctx: Interaction, player: int):
        # Establish a multi-way connection between players
        await self.bot.cursor.execute("""SELECT rp.id
        FROM bakery_discordchannel dc 
        JOIN ramen_player rp on dc.id = rp.channel_id
        WHERE dc.discord_id = %s;
        """, (ctx.channel.id,))
        player_id = await self.bot.cursor.fetchone()
        player_id = player_id[0]

        await self.bot.cursor.execute("""SELECT rpc.to_player_id
            FROM ramen_player_connections rpc
            WHERE rpc.from_player_id = %s;
            """, (player,))
        first_players = await self.bot.cursor.fetchall()
        if first_players:
            first_players.append((player,))
        else:
            first_players = [(player,)]

        await self.bot.cursor.execute("""SELECT rpc.to_player_id
            FROM ramen_player_connections rpc
            WHERE rpc.from_player_id = %s;
            """, (player_id,))
        second_players = await self.bot.cursor.fetchall()
        if second_players:
            second_players.append((player_id,))
        else:
            second_players = [(player_id,)]

        await self.bot.cursor.execute("""SELECT id FROM ramen_player_connections rpc ORDER BY id DESC;""")
        id_amount = await self.bot.cursor.fetchone()
        id_amount = id_amount[0] if id_amount else 0

        for player1 in first_players:
            for player2 in second_players:
                id_amount += 1
                await self.bot.cursor.execute("INSERT INTO ramen_player_connections VALUES (%s, %s, %s);", (id_amount, player1[0], player2[0]))
                id_amount += 1
                await self.bot.cursor.execute("INSERT INTO ramen_player_connections VALUES (%s, %s, %s);", (id_amount, player2[0], player1[0]))

        for player1 in first_players:
            await self.bot.cursor.execute("""SELECT dc.discord_id
            FROM ramen_player rp
            JOIN bakery_discordchannel dc on dc.id = rp.channel_id
            WHERE rp.id = %s;
            """, player1)
            channel_id = await self.bot.cursor.fetchone()
            channel = self.bot.get_channel(channel_id[0])
            second_names = ''
            for player2 in second_players:
                await self.bot.cursor.execute("""SELECT rp.name
                FROM ramen_player rp
                WHERE rp.id = %s;
                """, player2)
                name = await self.bot.cursor.fetchone()
                second_names += (name[0] + ', ')
            await channel.send('A Multi-Way Connection has been established with players: ' + second_names.strip(', '))

        for player2 in second_players:
            await self.bot.cursor.execute("""SELECT dc.discord_id
            FROM ramen_player rp
            JOIN bakery_discordchannel dc on dc.id = rp.channel_id
            WHERE rp.id = %s;
            """, player2)
            channel_id = await self.bot.cursor.fetchone()
            channel = self.bot.get_channel(channel_id[0])
            first_names = ''
            for player1 in first_players:
                await self.bot.cursor.execute("""SELECT rp.name
                FROM ramen_player rp
                WHERE rp.id = %s;
                """, player1)
                name = await self.bot.cursor.fetchone()
                first_names += (name[0] + ', ')
            await channel.send('A Multi-Way Connection has been established with players: ' + first_names.strip(', '))
        await self.bot.db_conn.commit()

    @app_commands.command()
    @app_commands.checks.has_role("IC6 Moderator")
    async def unbridge(self, ctx: Interaction, player: int):
        # De-establish a multi-way connection with a player
        await self.bot.cursor.execute("""SELECT rpc.to_player_id
            FROM ramen_player_connections rpc
            WHERE rpc.from_player_id = %s;
            """, (player,))
        connected_players = await self.bot.cursor.fetchall()
        
        await self.bot.cursor.execute("DELETE FROM ramen_player_connections WHERE from_player_id = %s;", (player,))
        await self.bot.cursor.execute("DELETE FROM ramen_player_connections WHERE to_player_id = %s;", (player,))

        await self.bot.cursor.execute("""SELECT rp.name
        FROM ramen_player rp
        WHERE rp.id = %s;
        """, (player,))
        disconnecting_player = await self.bot.cursor.fetchone()

        for connected_player in connected_players:
            await self.bot.cursor.execute("""SELECT dc.discord_id
            FROM ramen_player rp
            JOIN bakery_discordchannel dc on dc.id = rp.channel_id
            WHERE rp.id = %s;
            """, connected_player)
            channel_id = await self.bot.cursor.fetchone()
            channel = self.bot.get_channel(channel_id[0])
            await channel.send('A Multi-Way Connection has been de-established with ' + disconnecting_player[0])

        await self.bot.cursor.execute("""SELECT dc.discord_id
        FROM ramen_player rp
        JOIN bakery_discordchannel dc on dc.id = rp.channel_id
        WHERE rp.id = %s;
        """, (player,))
        channel_id = await self.bot.cursor.fetchone()
        disconnecting_channel = self.bot.get_channel(channel_id[0])
        await disconnecting_channel.send('A Multi-Way Connection has been de-established with everyone')
        await self.bot.db_conn.commit()


async def setup(bot):
    await bot.add_cog(BridgingCog(bot))

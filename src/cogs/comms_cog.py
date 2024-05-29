from discord.ext import commands
from discord.ext.commands import Context, Cog
from discord import app_commands, Game

IS_ENABLED = True

class CommsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_check(self, ctx: Context):
        if (not IS_ENABLED):
            await ctx.send('This Cog is disabled')
        return IS_ENABLED
    
    @Cog.listener("on_message")
    async def ping(self, message):

        if message.author == self.bot.user:
            return
        pid = '<@&1240595913261711391>'
        myid = '<@&662827894560784419>'

        channel_id = message.channel.id
        await self.bot.cursor.execute("""SELECT dc.id 
        FROM bakery_discordchannel dc 
        JOIN ramen_player rp on dc.id = rp.channel_id
        WHERE dc.discord_id = %s;
        """, (channel_id,))
        ci_msg_content = message.content.lower()
        in_ic_channel = await self.bot.cursor.fetchone()
        pings = ["p", "ping", ";p", "mp", "mping", ";mp"]
        mod_ping = ci_msg_content in pings
        player_ping = ci_msg_content in ["aa", ";a", "maa", ";ma"]
        is_ping = mod_ping or player_ping
        if is_ping and not in_ic_channel:
            await message.channel.send("Ice Cream Channels Only!")
            return
        if is_ping and in_ic_channel:

            async for msg in message.channel.history(limit=5):   # Cleanup on leftover pings
                if myid in msg.content or msg.content.lower() in ["ping", "p"]:
                    await msg.delete()
            
            if mod_ping:
                await self.bot.cursor.execute("""SELECT rc.first_name, rc.last_name, rc.nick_name 
                FROM bakery_discorduser du
                JOIN ramen_player rp on du.id = rp.discord_user_id
                JOIN ramen_character rc on rc.player_id = rp.id                              
                WHERE du.discord_id = %s;
                """, (message.author.id,))
                name = await self.bot.cursor.fetchone()
                if not name:
                    await message.channel.send(f"[Please Wait for {myid}...]")
                    return
                name = f"{name[0]} {name[1]}" if name[0] else name[1]
                if "m" in ci_msg_content:
                    await message.channel.send(f"[Turn Ended by {name}, IMPORTANT RESPONSE | {myid}]")
                else:
                    await message.channel.send(f"[Turn Ended by {name} | {myid}]")
                return 
            elif player_ping:
                if "m" in ci_msg_content:
                    await message.channel.send(f"[IMPORTANT TURN. Awaiting Player... | {pid}]")
                else:
                    await message.channel.send(f"[Awaiting Player... | {pid}]")
        if not is_ping and in_ic_channel:
            async for msg in message.channel.history(limit=5):   # Cleanup on leftover pings
                if myid in msg.content or pid in msg.content or msg.content.lower() in ["p", "ping", ";p", "mp", "mping", ";mp",
                                                                                        "aa", ";a", "maa", ";ma"]:
                    await msg.delete()

        await self.bot.process_commands(message)

async def setup(bot):
    await bot.add_cog(CommsCog(bot))
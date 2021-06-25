from __future__ import print_function
from minecraft import authentication
from minecraft.exceptions import YggdrasilError
from minecraft.networking.connection import Connection
from minecraft.networking.packets import clientbound, serverbound, keep_alive_packet
from constants import GUILD_CHAT_CHANNEL, MINECRAFT_EMAIL, MINECRAFT_PASSWORD, EMOJIS
from discord.ext import commands
import discord
import asyncio
import random
import time
import json
import re


class GuildChat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.auth_token = authentication.AuthenticationToken()
        self.email = MINECRAFT_EMAIL
        self.password = MINECRAFT_PASSWORD
        self.chatchannel = None
        self.connection = None
        self.connected = False
        self.ign = None
        self.last_connection = time.time()
        self.login_attempts = 0
        self.last_command = None
        self.lastmsg = None
        self.command_queue = []
        self.chatbuffer = []
        self.embedbuffer = []
        self.chatbufferdelay = time.time()
        self.loophandle = asyncio.get_event_loop()
        self.guild_total = 0
        self.guild_online = 0
        self.guild_count_delay = 0
        self.start()

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        self.chatchannel = self.bot.get_channel(GUILD_CHAT_CHANNEL)

    @commands.Cog.listener()
    async def on_message(self, message) -> None:
        if message.author.bot or message.channel.id != GUILD_CHAT_CHANNEL:
            return
        if len(message.clean_content) <= 150:
            text = message.clean_content
            displayname = message.author.name
            to_send = insert_invis(f"{displayname}: {re.sub('ez', 'e⛶z', text, flags=re.IGNORECASE)}")
            self.append_command(f"/gc {to_send}")
            text = discord.utils.escape_markdown(message.clean_content)
            displayname = discord.utils.escape_markdown(displayname)
            self.lastmsg = await message.channel.send(f"{EMOJIS['DISCORD']} **{displayname}**: {text}")
        else:
            await message.channel.send(":x: **ERROR**: That message is too long!")
        await message.delete()

    @commands.command()
    @commands.is_owner()
    async def sudo(self, ctx, *, msg: str = None) -> None:
        if msg is None:
            await ctx.send('You need to provide a message to send!')
        else:
            self.command_queue.append(msg)
            await ctx.send(f'Instructed the bot to type `{msg}`')

    @sudo.error
    async def sudo_error(self, ctx, error) -> None:
        if isinstance(error, commands.CheckFailure):
            await ctx.send('You are not authorized to use this command!')

    def start(self) -> None:
        self.login()
        self.connect()

        async def bg_task():
            while True:
                try:
                    self.tick()
                    if time.time() - self.chatbufferdelay > 1.5 and (
                            len(self.chatbuffer) > 0 or len(self.embedbuffer) > 0):
                        self.chatbufferdelay = time.time()
                        text = embed = None

                        if len(self.chatbuffer) > 0:
                            text = "\n".join(self.chatbuffer[:5])
                            self.chatbuffer = self.chatbuffer[5:]

                        if len(self.embedbuffer) > 0:
                            embed = self.embedbuffer[0]
                            self.embedbuffer = self.embedbuffer[1:]

                        if text is not None and embed is not None:
                            self.loophandle.create_task(self.chatchannel.send(content=text, embed=embed))
                        elif text is not None:
                            self.loophandle.create_task(self.chatchannel.send(content=text))
                        elif embed is not None:
                            self.loophandle.create_task(self.chatchannel.send(embed=embed))
                except (ValueError, Exception):
                    pass
                await asyncio.sleep(0.2)

        self.bot.loop.create_task(bg_task())

    def login(self):
        self.login_attempts += 1
        try:
            self.auth_token.authenticate(self.email, self.password)
            self.ign = self.auth_token.profile.name
        except YggdrasilError as e:
            print(f'[GC] Error while logging in: {e}')
        print(f'[GC] Logged in as {self.ign}')
        self.connection = Connection('mc.hypixel.net',
                                     25565,
                                     auth_token=self.auth_token,
                                     initial_version=47,
                                     allowed_versions=[47])

        def on_connect(_join_game_packet):
            self.login_attempts = 0
            self.last_connection = time.time()
            self.last_command = time.time()
            self.guild_count_delay = time.time() - 55
            self.connected = True
            print("[GC] Successfully logged on to Hypixel!")

        def handle_keep_alive(_data):
            self.last_connection = time.time()

        self.connection.register_packet_listener(on_connect, clientbound.play.JoinGamePacket)
        self.connection.register_packet_listener(self.handle_chat, clientbound.play.ChatMessagePacket)
        self.connection.register_packet_listener(handle_keep_alive, keep_alive_packet.AbstractKeepAlivePacket)

    def handle_chat(self, chat_packet):
        chat_raw = str(chat_packet.json_data)
        chat_json = json.loads(chat_raw)
        msg = raw_to_msg(chat_json)
        msg = "".join([msg[x] for x in range(len(msg)) if "§" not in msg[max(0, x - 1):x + 1]])

        if ("From " in msg) and ("light_purple" in chat_raw):
            return

        if ("Guild >" in msg) and (msg.count(":") == 0) and (msg.split()[-1] in ['joined.', 'left.']):
            user = msg.split()[2].replace("_", r"\_")
            if "joined." in msg:
                self.guild_online += 1
                self.chatbuffer.append(f"{EMOJIS['JOIN']} **{user}** joined `{self.guild_online}/{self.guild_total}`")
            else:
                self.guild_online -= 1
                self.chatbuffer.append(f"{EMOJIS['LEAVE']} **{user}** left `{self.guild_online}/{self.guild_total}`")

        elif ("Guild >" in msg) and (self.ign not in msg.split(":")[0]):
            content = discord.utils.escape_markdown(msg.replace("Guild >", "").strip())
            split = content.split(":")
            userdata = split[0].strip().split(" ")
            user = ""
            for data in userdata:
                if "[" not in data:
                    user = data
            message = ":".join(split[1:]).replace("@", "@\u200b").replace("<", "<\u200b")
            self.chatbuffer.append(f"{EMOJIS['HYPIXEL']} **{user}**: {message}")

        elif "You cannot say the same message twice!" in msg:
            self.loophandle.create_task(self.lastmsg.edit(
                content=self.lastmsg.content.replace(EMOJIS['DISCORD'], f"{EMOJIS['DISCORD']} **") + "** *(Blocked)*"
            ))

        elif "set the Guild Description to" in msg:
            self.embedbuffer.append(discord.Embed(
                title=msg.replace("set the Guild Description to ", "set the Guild Description to ' ") + " '",
                color=4886754
            ))

        elif "was kicked from the guild by" in msg:
            self.guild_total -= 1
            self.embedbuffer.append(discord.Embed(
                title=msg,
                color=16098851
            ))

        elif "joined the guild!" in msg:
            self.guild_total += 1
            self.embedbuffer.append(discord.Embed(
                title=msg,
                color=8311585
            ))

        elif "was promoted from " in msg and "Guild >" not in msg:
            text = msg.split(" from ")[0]
            rankbuffer = msg.split(" from ")[1].strip().split(" to ")
            if len(rankbuffer) != 2:
                return
            rank1 = rankbuffer[0]
            rank2 = rankbuffer[1]
            self.embedbuffer.append(discord.Embed(
                title=text,
                description=f"{rank1} {chr(10233)} {rank2}",
                color=8311585))

        elif "was demoted from " in msg and "Guild >" not in msg:
            split = msg.split(" from ")
            rankbuffer = split[1].strip().split(" to ")
            if len(rankbuffer) != 2:
                return
            self.embedbuffer.append(discord.Embed(
                title=split[0],
                description=f"{rankbuffer[0]} {chr(10233)} {rankbuffer[1]}",
                color=13632027))

        elif "The Guild has reached Level" in msg and "Guild >" not in msg:
            self.embedbuffer.append(discord.Embed(
                title=msg.strip().replace("!", ""),
                color=8311585))

        elif "Total Member" == msg[:12] and ":" in msg:
            self.guild_total = int(msg.strip().split()[-1])

        elif "Online Member" == msg[:13] and ":" in msg:
            self.guild_online = int(msg.strip().split()[-1])

    def append_command(self, command, do_first=False):
        if do_first:
            self.command_queue.insert(0, command)
        else:
            self.command_queue.append(command)

    def send_command(self, command):
        packet = serverbound.play.ChatPacket()
        packet.message = command
        self.connection.write_packet(packet)

    def tick(self):
        self.command_tick()
        self.check_connection()
        self.guild_count_update()

    def guild_count_update(self):
        if time.time() - self.guild_count_delay >= 60 and self.connected:
            self.guild_count_delay = time.time()
            self.append_command("/gl")

    def check_connection(self):
        if time.time() - self.last_connection > 60 + max(0, (
                120 * (self.login_attempts - 1))) and self.login_attempts < 11:
            self.last_connection = time.time()
            try:
                self.disconnect()
            except (ValueError, Exception):
                pass
            print("[GC] Reconnecting...")
            self.connected = False
            self.login()
            self.connect()

    def command_tick(self):
        if len(self.command_queue) > 0:
            if time.time() - self.last_command > 0.75:
                self.last_command = time.time()
                command = self.command_queue.pop(0)
                self.send_command(command)

    def connect(self):
        print("[GC] Connecting...")
        self.connection.connect()

    def disconnect(self):
        print("[GC] Disconnecting...")
        self.connection.disconnect(True)


def raw_to_msg(msg_json):
    try:
        msg = ""
        if "text" in msg_json:
            msg += msg_json["text"]
        if "extra" in msg_json:
            for i in msg_json["extra"]:
                msg += i["text"]
        return msg
    except Exception as error:
        print(f'Encountered an error while parsing message: {error}')
        return ""


def insert_invis(msg):
    n = len(msg) // 10 + 1
    invischar = "⛬⛫⛭⛮⛶"
    for i in range(n):
        randompos = random.randint(0, len(msg) - 1)
        msg = msg[:randompos] + random.choice(invischar) + msg[randompos:]
    return msg


def setup(bot):
    bot.add_cog(GuildChat(bot))

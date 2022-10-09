import discord
from discord.ext import commands
from discord.utils import get
import discord.errors
import datetime
import os
import asyncio
from dotenv import load_dotenv
import chat_exporter
import mysql.connector
from sklearn import tree
from sklearn.feature_extraction.text import CountVectorizer
from passlib.hash import pbkdf2_sha256 as hash_algorithm
import string
import random
from io import open as openfile_
from tickets_variables import *
from hypixel_api import *
from external_calculators import *
from web import start
from tcp_latency import measure_latency
start()
#################################
human_ticket_interrogation = [
  "is this ticket dead?",
  "is this done?",
  "order done?",
  "completed?",
  "hello?",
  "what happened to this?",
  "do you still need it?",
  "do you still want?",
  "close this ticket if your done"
  "is this ticket still open?",
  "is it still running?",
]

non_interrogative_text = [
    "hello",
    "what do you want",
    "when can you come on",
    "the fuck",
    "how much do you need?",
    "what collat",
    "what is the price",
    "h",
    "f",
    "ggg",
    "fsdgshrhdfhh",
    "sdfjsgjsbghewgbehbqgh",
    "487487",
    "i can do at 5pm",
    "i'm not on",
]
test_texts = ["is this order finished?"]

training_texts = non_interrogative_text + human_ticket_interrogation
training_labels = ["alive"] * len(non_interrogative_text) + ["dead"] * len(
    human_ticket_interrogation)

vectorizer = CountVectorizer()
vectorizer.fit(training_texts)

training_vectors = vectorizer.transform(training_texts)

classifier = tree.DecisionTreeClassifier()
classifier.fit(training_vectors, training_labels)

##################################
intent = discord.Intents.all()
bot = discord.Client(intents=intent)
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
db_host=os.getenv("db_host")
db_user=os.getenv("db_user")
db_password=os.getenv("db_password")
db_name=os.getenv("db_name")
db_port=os.getenv("db_port")


class Cursor:
    def execute(prepare, return_fetchall=False):
        Database = mysql.connector.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            database=db_name,
            port=db_port,
            autocommit=True)

        unicursor = Database.cursor()
        # unicursor.execute(f"USE {database_name}")
        unicursor.execute(prepare)

        if return_fetchall:
            item = unicursor.fetchall()
            Database.close()
            return item
        else:
            Database.close()

    def __init__(self, prepare):
        self.execute =execute()

######################

#while True:
#  category_name=input("Category name : ")
#  new_count=int(input("New count : "))
#  Cursor.execute(f"UPDATE `Panel` SET `ticket_number`='{new_count}' WHERE `name` LIKE '{category_name}%' LIMIT 1")

async def get_category(id):
    myguild = bot.get_guild(myguild_id)
    category = discord.utils.get(myguild.categories, id=id)
    return category


async def system_loop():
  await asyncio.sleep(60)
  while True:
      await update_database()
      await asyncio.sleep(int(when_to_update_database))



async def sec_to_time(sec):
    sec = int(sec)
    day = sec // (24 * 3600)
    sec = sec % (24 * 3600)
    hour = sec // 3600
    sec %= 3600
    minutes = sec // 60
    sec %= 60
    seconds = sec
    time_human: str = ""
    if day > 0:
        time_human = time_human + f"{day} days"
    if hour > 0:
        time_human = time_human + f"{hour} hours"
    if minutes > 0:
        time_human = time_human + f"{minutes} mins"
    if seconds > 0:
        time_human = time_human + f"{seconds} seconds"
    return time_human


async def reformat_list(items):
    to_be_returned = []
    for item in items:
        if type(item) == list or tuple:
            for i in item:
                to_be_returned.append(i)
        else:
            to_be_returned.append(item)
    return to_be_returned


@bot.event
async def on_ready():
    print("getting chat exporter(transcript systems) ready")
    chat_exporter.init_exporter(bot)
    print("ready")
    #print(await get_info(rarity=5,goal=80,xp_boost=40,current_level=79,current_xp=69,skill="fishing")).price)
    guild = bot.get_guild(721318863433629707)
    print(guild)
    #for i in guild.categories:
      #pass
      #print(i.name, i.id)
    print("done")
    #for i in await reformat_list(Cursor.execute("SELECT `channel_id` FROM `Tickets`",#return_fetchall=True)):
      #channel=await bot.fetch_channel(int(i))

    
    #channel=await bot.fetch_channel(803021927710064711)
    #await channel.send(embed=embed)
    await system_loop()


@bot.event
async def on_raw_reaction_add(payload):
    message_id = str(payload.message_id)
    if str(payload.user_id) == str(bot.user.id):
        return
    emoji = str(payload.emoji)

    if str(payload.emoji) == close_reaction:
        prepare = "SELECT `channel_id` FROM `Tickets`"
        tickets = Cursor.execute(prepare, return_fetchall=True)
        tickets = await reformat_list(tickets)
        if int(payload.channel_id) in tickets:
            guild = await bot.fetch_guild(payload.guild_id)
            channel = bot.get_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
            member = await guild.fetch_member(payload.user_id)

            await message.remove_reaction(payload.emoji, member)
            await close(guild=guild, channel=channel, member=member)

    if str(payload.emoji) == claim_reaction:
        prepare = "SELECT `channel_id` FROM `Tickets`"
        tickets = Cursor.execute(prepare, return_fetchall=True)
        tickets = await reformat_list(tickets)
        if int(payload.channel_id) in tickets:
            guild = await bot.fetch_guild(payload.guild_id)
            channel = bot.get_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
            member = await guild.fetch_member(payload.user_id)
            await message.remove_reaction(payload.emoji, member)
            await claim(guild=guild, channel=channel, member=member)

    if str(payload.emoji) == delete_reaction:
        prepare = "SELECT `channel_id` FROM `Tickets`"
        tickets = Cursor.execute(prepare, return_fetchall=True)
        tickets = await reformat_list(tickets)
        if int(payload.channel_id) in tickets:
            guild = await bot.fetch_guild(payload.guild_id)
            channel = bot.get_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
            member = await guild.fetch_member(payload.user_id)
            await message.remove_reaction(payload.emoji, member)

            def check(message):
                return (message.channel == channel and message.author == member
                        and message.content.lower() in ["confirm", "cancel"])

            await channel.send(
                "Are you sure that you want to delete this ticket?\nSay **confirm** to confirm and **cancel** to cancel"
            )
            try:
                msg = await bot.wait_for("message", timeout=15.0, check=check)
            except asyncio.TimeoutError:
                await channel.send(timeout_msg)
                return
            else:
                if msg.content.lower() == "cancel":
                    await channel.send(timeout_msg)
                    return
            await delete(guild=guild, channel=channel, member=member)

    if str(payload.emoji) == open_reaction:
        prepare = "SELECT `channel_id` FROM `Tickets`"
        tickets = Cursor.execute(prepare, return_fetchall=True)
        tickets = await reformat_list(tickets)
        if int(payload.channel_id) in tickets:
            guild = await bot.fetch_guild(payload.guild_id)
            channel = bot.get_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
            member = await guild.fetch_member(payload.user_id)
            await message.remove_reaction(payload.emoji, member)
            await open(guild=guild, channel=channel, member=member)

    if str(payload.emoji) == ticket_reaction:
        prepare = "SELECT `msg_id` from `Panel`"
        ticket_msg_ids = await reformat_list(
            Cursor.execute(prepare, return_fetchall=True))
        if int(message_id) not in ticket_msg_ids:
          return
        prepare = f"SELECT `ticket_prefix`,`ticket_category`,`ticket_number`,`msg_text`,`name` from `Panel` WHERE `msg_id`='{message_id}'"
        guild = await bot.fetch_guild(payload.guild_id)
        channel = bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        member = await guild.fetch_member(payload.user_id)
        await message.remove_reaction(payload.emoji, member)
        role_check = discord.utils.get(guild.roles, name="Service Banned")
        if role_check in member.roles:
            dm = await member.create_dm()
            embed = discord.Embed(
                title="Service Blocked",
                description=
                f"You are service blocked in **{guild_name}** and hence cannot create the ticket.",
                color=0xFF2121,
                timestamp=datetime.datetime.now(datetime.timezone.utc),
            )
            embed.set_footer(text=footer)
            await dm.send(embed=embed)
            return
        database_info = Cursor.execute(prepare, return_fetchall=True)[0]
        hypixel_verified=discord.utils.get(guild.roles, id=979541904507162634)
        if hypixel_verified not in member.roles and database_info[0].lower() != "support":
            dm = await member.create_dm()
            embed = discord.Embed(
                title="Hypixel Verification",
                description=
                f"You are not verified on Hypixel and hence cannot create the ticket.\nPlease verify via <#1025465497266962472>",
                color=0xFF2121,
                timestamp=datetime.datetime.now(datetime.timezone.utc),
            )
            embed.set_footer(text=footer)
            await dm.send(embed=embed)
            return
        prepare = f"SELECT * FROM `Tickets` WHERE `user_id`='{member.id}' and `category`='{database_info[4]}' and `is_closed`='0'"
        previous_ticket = Cursor.execute(prepare, return_fetchall=True)
        if len(previous_ticket) > 0:
            old_ticket = previous_ticket[0][1]
            dm = await member.create_dm()
            embed = discord.Embed(
                title="You already have a ticket",
                description=
                f"You already have a ticket of that service in **{guild_name}** and hence cannot create a new one. \n<#{old_ticket}>",
                timestamp=datetime.datetime.now(datetime.timezone.utc),
                color=default_embed_color
            )
            embed.set_footer(text=footer)
            await dm.send(embed=embed)
            return
        channel_to_be_created = database_info[0]
        ticket_num = int(database_info[2])
        ticket_num += 1
        ticket_num = str(ticket_num).zfill(3)
        channel_to_be_created = channel_to_be_created + "-" + ticket_num
        prepare = f"UPDATE `Panel` SET `ticket_number` = '{ticket_num}' WHERE `msg_id`='{message_id}'"
        Cursor.execute(prepare)
        category = await get_category(int(database_info[1]))

        role=None
        for role_id in ticket_experts_id:
          if role_id.lower() in database_info[4].lower():
            role = discord.utils.get(guild.roles,id=ticket_experts_id[role_id])

        ticket = await guild.create_text_channel(channel_to_be_created,
                                                 category=category)
        await ticket.edit(sync_permissions=True)
        if role!=None:
          await ticket.set_permissions(role,send_messages=True,read_messages=True)
        await ticket.set_permissions(member,
                                     send_messages=True,
                                     read_messages=True)
        prepare = f"""INSERT INTO `Tickets` (`user_id`,`channel_id`,`category`,`claim_id`,`is_closed`)
        VALUES ('{str(member.id)}','{str(ticket.id)}','{database_info[4]}','NULL','0')"""
        Cursor.execute(prepare)
        if database_info[3] == None:
            description = database_info[3]
        else:
          #description=default_ticket_msg
          description = database_info[3]
          pings=[]
          description=str(description)
          for i in description.split("<@"):
            i=str(i)
            if len(i)>20:
              if i[0] in ["!","&"] and i[1:19]==str(await get_digit(i[1:19])) and "<@"+i[:21] not in pings:
                pings.append("<@"+i[:21])
        embed = discord.Embed(
            description=description,
            color=0x0094FF,
            timestamp=datetime.datetime.now(datetime.timezone.utc),
        )
        embed.set_footer(text=footer)
        msg = await ticket.send(content=f"<@{str(payload.user_id)}>,"+" ,".join(pings),embed=embed)
        await msg.add_reaction(close_reaction)
        await msg.add_reaction(claim_reaction)


async def is_digit(text):
    try:
        text = int(text)
    except:
        return False
    else:
        return True


async def not_a_ticket():
    embed = discord.Embed(
        title="Not a ticket :pensive:",
        description=
        "I'm sorry but this doesn't seem like a ticket....\nIt has no reference in the database",
        timestamp=datetime.datetime.now(datetime.timezone.utc),
        color=0xFF0D00,
    )
    embed.set_footer(text=footer)
    return embed


async def close(ctx=None, channel=None, guild=None, member=None):
    if ctx != None:
        channel = ctx.channel
        guild = ctx.guild
        member = ctx.author
    prepare = f"SELECT * FROM `Tickets` WHERE `channel_id`='{str(channel.id)}'"
    database_info = Cursor.execute(prepare, return_fetchall=True)
    if len(database_info) < 1:
        await channel.send(embed=await not_a_ticket())
        return
    elif database_info[0][4]:
        embed = discord.Embed(
            title="Already closed",
            description=
            f"I'm sorry but this ticket seems like it's already been closed....\nDo `{prefix}open` to reopen the ticket and then try to close it again.",
            timestamp=datetime.datetime.now(datetime.timezone.utc),
            color=0x0000FF,
        )
        embed.set_footer(text=footer)
        await channel.send(embed=embed)
        return
    database_info = database_info[0]
    #await transcript(channel=channel,
    #                 member=member,
    #                 guild=guild,
    #                 action="Ticket Closed")
    owner=await bot.fetch_user(int(database_info[0]))
    embed = await ticket_info_embed(
        action="Ticket Closed",
        color=0xFFD600,
        database_info=database_info,
        channel=channel,
        member=member,
        owner=owner,
    )
    await channel.send(embed=embed)
    await transcript_log(embed=embed)
    prepare = f"""UPDATE `Tickets` SET `is_closed`='1' 
    WHERE `channel_id`='{str(channel.id)}'"""
    Cursor.execute(prepare)
    embed = discord.Embed(
        description=
        f"Ticket has been closed\n{open_reaction} - Open Ticket\n{delete_reaction} - Delete Ticket",color=default_embed_color
    )
    msg = await channel.send(embed=embed)
    await msg.add_reaction(open_reaction)
    await msg.add_reaction(delete_reaction)
    prepare = f"UPDATE `Tickets` SET `claim_id`='NULL' WHERE `channel_id`='{channel.id}'"
    Cursor.execute(prepare)
    try:
      await channel.set_permissions(owner,read_messages=False,send_messages=False)
    except:
      pass 
    category=await get_category(closed_category)
    if str(channel.name).startswith("🔒") == False:
        await channel.edit(name="🔒-" + channel.name,category=category)
    else:
        await channel.edit(category=category)


async def delete(ctx=None, channel=None, guild=None, member=None):
    if ctx != None:
        channel = ctx.channel
        guild = ctx.guild
        member = ctx.author
    prepare = f"SELECT * FROM `Tickets` WHERE `channel_id`='{str(channel.id)}'"
    database_info = Cursor.execute(prepare, return_fetchall=True)
    if len(database_info) < 1:
        await channel.send(embed=await not_a_ticket())
        return
    database_info = database_info[0]
    await transcript(
        channel=channel,
        member=member,
        guild=guild,
        action="Ticket being Deleted",
        dm_people=True,
    )
    await channel.delete()
    prepare = f"""DELETE FROM `Tickets` WHERE `channel_id`='{str(channel.id)}'"""
    Cursor.execute(prepare)


async def open(ctx=None, channel=None, guild=None, member=None):
    if ctx != None:
        channel = ctx.channel
        guild = ctx.guild
        member = ctx.author
    prepare = f"SELECT * FROM `Tickets` WHERE `channel_id`='{str(channel.id)}'"
    database_info = Cursor.execute(prepare, return_fetchall=True)
    if len(database_info) < 1:
        await channel.send(embed=await not_a_ticket())
        return
    elif database_info[0][4] == False:
        embed = discord.Embed(
            title="Already Open",
            description=
            f"I'm sorry but this ticket seems like it's already been open....",
            timestamp=datetime.datetime.now(datetime.timezone.utc),
            color=0x0000FF,
        )
        embed.set_footer(text=footer)
        await channel.send(embed=embed)
        return
    database_info = database_info[0]
    prepare = (
        f"""UPDATE `Tickets` SET `is_closed`='0' WHERE `channel_id`='{str(channel.id)}'"""
    )
    Cursor.execute(prepare)
    embed = discord.Embed(description=f"Ticket opened by <@!{member.id}>",color=default_embed_color)
    owner=database_info[0]
    try:
      owner=await bot.fetch_user(int(owner))
      await channel.set_permissions(owner,read_messages=True,send_messages=True)
    except:
      pass
    await channel.send(embed=embed)
    prepare=f"SELECT `ticket_category` FROM `Panel` WHERE `name`='{database_info[2]}'"
    category=Cursor.execute(prepare,return_fetchall=True)
    if len(category)>0:
      category=category[0][0]
      category=await get_category(int(category))
      await channel.edit(category=category)
    if str(channel.name).startswith("🔒"):
      await channel.edit(name=channel.name[2:])
    


async def get_users(channel):
    messages = [message async for message in channel.history(limit=200)]
    users = []
    for message in messages:
        if str(message.author.id) not in users and message.author.bot == False:
            users.append(str(message.author.id))
    return users


async def rename(ctx):
    channel = ctx.channel
    if await check_ticket(ctx.channel.id) == False:
        await channel.send(embed=await not_a_ticket())
        return
    channel = ctx.channel
    old_name = channel.name
    member = ctx.author
    content = ctx.content
    content_split = content.split()
    if len(content_split) < 2:
        confirmation = await channel.send(
            "Please enter the channel name! or say it in chat")

        def check(message):
            return message.channel == channel and message.author == member

        try:
            msg = await bot.wait_for("message", timeout=15.0, check=check)
        except asyncio.TimeoutError:
            await confirmation.delete()
            await channel.send("Rename aborted", delete_after=5)
            return
        else:
            await confirmation.delete()
            if msg.content.startswith(f"{prefix}rename"):
                return
            else:
                new_name = msg.content
    else:
        new_name = "-".join(content_split[1:])
        if len(new_name) > 1024:
            new_name = new_name[:1023]
    try:
        embed = discord.Embed(
            title="Trying to update channel name....",
            description=
            f"This may take a while as thats how discord works for bots :(\nNew channel name will be set to {new_name}",
            timestamp=datetime.datetime.now(datetime.timezone.utc),
            color=0x0094FF,
        )
        embed.set_footer(text=footer)
        msg = await channel.send(embed=embed)
        await channel.edit(name=new_name)
    except Exception as e:
        await msg.delete()
        embed = discord.Embed(
            title="Error changing ticket name",
            description=f"Error: {e}",
            color=0xFF0D00,
            timestamp=datetime.datetime.now(datetime.timezone.utc),
        )
        embed.set_footer(text=footer)
        await channel.send(embed=embed)
    else:
        await msg.delete()
        embed = discord.Embed(
            title="Name updated successfully",
            description=f"**Old Name:** {old_name}\n**New Name:** {new_name}",
            color=0x2FFF70,
            timestamp=datetime.datetime.now(datetime.timezone.utc),
        )
        embed.set_footer(text=footer)
        embed.set_author(name=member, icon_url=member.avatar)
        await channel.send(embed=embed)


async def check_ticket(channel_id):
    prepare = f"SELECT * FROM `Tickets` WHERE `channel_id`='{str(channel_id)}'"
    database_info = Cursor.execute(prepare, return_fetchall=True)
    if len(database_info) < 1:
        return False
    else:
        return database_info[0]


async def transcript(ctx=None,member=None,channel=None,guild=None,action="Transcript Saved",dm_people=False,):
    if ctx != None:
        member = ctx.author
        channel = ctx.channel
        guild = ctx.guild
    prepare = f"SELECT * FROM `Tickets` WHERE `channel_id`='{str(channel.id)}'"
    database_info = Cursor.execute(prepare, return_fetchall=True)
    if len(database_info) < 1:
        await channel.send(embed=await not_a_ticket())
        return
    database_info = database_info[0]
    users = await get_users(channel)
    pls_wait = await channel.send(
        "Compiling the transcript, please wait upto 10 seconds <a:windowsloadingsbs:783051854413955072>"
    )

    file = await chat_exporter.export(channel)
    with openfile_(channel.name+".htm", "w") as f:
        f.write(file)
    file = discord.File(channel.name+".htm")
    # transcript_saved = False
    # if file == None:
    #     embed = discord.Embed(
    #         title="Transcript Error!",
    #         description=
    #         "Well, this is akward but I got an error while compiling the transcript......\nTime to call the pest control to get rid of bugs :cockroach::cockroach: ",
    #         color=0xFF2121,
    #     )
    #     await channel.send(embed=embed)
    #     await transcript_log(embed=embed)
    await transcript_log(file=file)
    owner_id = database_info[0]
    try:
        owner = await bot.fetch_user(int(owner_id))
    except:
        owner = None
    if dm_people:
        try:
            dm_owner = await owner.create_dm()
            await dm_owner.send(file=file)
        except:
            dm = None
    await channel.send(file=discord.File(channel.name+".htm"))
    try:
        await pls_wait.delete()
    except:
        pass
    if member != owner and dm_people == True:
        try:
            dm_member = await member.create_dm()
            await dm_member.send(file=discord.File(channel.name+".htm"))
        except:
            dm = None
    embed = discord.Embed(
        title="Transcript Saved!",
        description=
        "Transcript has been successfully compiled.\nHere's some information about the ticket I gathered",
        color=0x2FFF70,
    )
    await channel.send(embed=embed)
    actions = {
        "Transcript Saved": 0x2FFF70,
        "Ticket Closed": 0xFFD600,
        "Ticket being Deleted": 0xFF0D00,
    }
    color = actions[action]
    embed = await ticket_info_embed(
        action=action,
        color=color,
        database_info=database_info,
        channel=channel,
        member=member,
        owner=owner,
        link=f"https://skyticket.dotcoes.xyz/transcripts/transcript-{channel.name}.html"
    )
    await channel.send(embed=embed)
    await transcript_log(embed=embed)
    if dm_people:
        try:
            await dm_owner.send(embed=embed)
        except:
            class_helper = 0
    if member != owner and dm_people == True:
        try:
            await dm_member.send(embed=embed)
        except:
            class_helper = 0


async def ticket_info_embed(action, color, database_info, channel, member,owner,link=None):
    users = await get_users(channel)
    embed = discord.Embed(
        description=f"**{action}**",
        color=color,
        timestamp=datetime.datetime.now(datetime.timezone.utc),
    )
    embed.set_footer(text=footer)
    if len(users) > 0:
        experts = await create_multiline_mention(users)
    else:
        experts = "None"
    try:
        embed.set_author(name=owner, icon_url=owner.avatar)
    except:
        embed.set_author(name="Ticket Owner not found...")
         
    embed.add_field(name="**Owner**", value=f"<@!{owner.id}>", inline=True)
    embed.add_field(name="**Name**", value=channel.name, inline=True)
    embed.add_field(name="**Panel**", value=database_info[2], inline=True)
    embed.add_field(name="**Action by**",
                    value=f"<@!{member.id}>",
                    inline=True)
    embed.add_field(name="**Channel**",
                    value=f"<#{database_info[1]}>",
                    inline=True)
    embed.add_field(name="**Experts**", value=experts, inline=True)
    if link!=None:
      embed.add_field(name="**Transcript**", value=f"[Direct Transcript]({link})", inline=True)

    return embed


async def ticket_info(ctx):
    channel = ctx.channel
    prepare = f"SELECT `user_id`,`channel_id`,`category` FROM `Tickets` WHERE `channel_id`='{str(ctx.channel.id)} LIMIT 1'"
    database_info = Cursor.execute(prepare, return_fetchall=True)
    if len(database_info) < 1:
        await channel.send(embed=await not_a_ticket())
        return
    database_info = database_info[0]
    try:
        owner_id = database_info[0]
        owner = await bot.fetch_user(int(owner_id))
    except:
        owner = None
    embed = await ticket_info_embed(
        action="Ticket Info",
        color=0x2FFF70,
        database_info=database_info,
        channel=ctx.channel,
        member=ctx.author,
        owner=owner,
    )
    await ctx.channel.send(embed=embed)


async def transcript_log(embed=None, content=None, file=None):
    channel = await bot.fetch_channel(int(transcript_channel))
    try:
        await channel.send(file=file)
    except:
        class_helper = 0
    if content != None and embed != None:
        await channel.send(content=content, embed=embed)
    else:
        try:
            await channel.send(content=content)
        except:
            class_helper = 0
        try:
            await channel.send(embed=embed)
        except:
            class_helper = 0


async def update_database(ctx=None):
    if ctx != None:
        if (ctx.author.guild_permissions.administrator == False
                and str(ctx.author.id) not in access_privilage):
            await ctx.channel.send("You don't have the perms to do this")
            return
    prepare = "SELECT `channel_id` FROM `Tickets`"
    channel_ids = Cursor.execute(prepare, return_fetchall=True)
    channel_ids = await reformat_list(channel_ids)
    for channel_id in channel_ids:
        try:
            channel = await bot.fetch_channel(int(channel_id))
        except discord.NotFound:
            try:
                prepare = f"DELETE FROM `Tickets` WHERE `channel_id`='{str(channel_id)}'"
                Cursor.execute(prepare)
            except:
                class_helper = 0
        else:
            if channel == None:
                prepare = (
                        f"DELETE FROM `Tickets` WHERE `channel_id`='{str(channel_id)}'"
                    )
                Cursor.execute(prepare)
    prepare = "SELECT `user_id` FROM `Tickets`"
    owner_ids = Cursor.execute(prepare, return_fetchall=True)
    owner_ids = await reformat_list(owner_ids)
    guild = await bot.fetch_guild(int(myguild_id))
    server_left_owners = []
    for owner_id in owner_ids:
        try:
            member = await guild.fetch_member(int(owner_id))
        except discord.NotFound:
            server_left_owners.append(owner_id)
        else:
            if member == None:
                server_left_owners.append(owner_id)
    for owner_id in server_left_owners:
        prepare = f"SELECT * FROM `Tickets` WHERE `user_id`='{str(owner_id)}'"
        try:
            database_info = Cursor.execute(prepare, return_fetchall=True)
        except:
            class_helper = 0
        else:
            for i in database_info:
                channel = await bot.fetch_channel(int(i[1]))
                await channel.send(content=prefix + "close", delete_after=1)
    prepare = "SELECT `claim_id` FROM `Tickets`"
    claimed_ids = Cursor.execute(prepare, return_fetchall=True)
    claimed_ids = await reformat_list(claimed_ids)
    guild = await bot.fetch_guild(int(myguild_id))
    server_left_claimed = []
    for claimed_id in claimed_ids:
        try:
            member = await guild.fetch_member(int(claimed_ids))
        except:
            server_left_claimed.append(claimed_ids)
        else:
            if member == None:
                server_left_claimed.append(claimed_ids)
    for claimed_id in server_left_claimed:
        prepare = f"SELECT * FROM `Tickets` WHERE `claim_id`='{str(claimed_id)}'"
        try:
            database_info = Cursor.execute(prepare, return_fetchall=True)
        except:
            class_helper = 0
        else:
            for i in database_info:
                channel = await bot.fetch_channel(int(i[1]))
                await channel.send(content=prefix + "unclaim", delete_after=1)
    if ctx != None:
        await ctx.channel.send("Database refreshed")


async def create_multiline_mention(users, mention_helper="@!"):
    mention = ""
    for user in users:
        user = str(user)
        mention = mention + "<" + mention_helper + user + ">\n"
    if mention[-2:] == "\n":
        mention = mention[:-2]
    return mention


async def get_all_tickets():
    prepare = """SELECT * FROM `Tickets` WHERE `is_closed`='0'"""
    return Cursor.execute(prepare, return_fetchall=True)


async def unaware_timezone(time_now):
    sec = time_now.second
    minute = time_now.minute
    hour = time_now.hour
    day = time_now.day
    month = time_now.month
    year = time_now.year
    return datetime.datetime(year=year,
                             month=month,
                             day=day,
                             hour=hour,
                             minute=minute,
                             second=sec)


async def find_inactive_tickets(ctx):
    await bot.wait_until_ready()
    if (ctx.author.guild_permissions.administrator == False
            and str(ctx.author.id) not in access_privilage):
        await ctx.channel.send("You don't have the perms to do this")
        return
    embed = discord.Embed(
        title="Please wait",
        description=
        f"Trying to find inactive tickets, any ticket in which no message has been sent in the last {await sec_to_time(ticket_inactivity_close_time)}\nThis could take **upto 20 seconds** <a:windowsloadingsbs:783051854413955072>",
        color=0x2FFF70,
        timestamp=datetime.datetime.now(datetime.timezone.utc),
    )
    embed.set_footer(text=footer)
    msg = await ctx.channel.send(embed=embed)
    database_info = await get_all_tickets()
    inactive_channels = []
    for ticket in database_info:
        channel_id = ticket[1]
        try:
            channel = await bot.fetch_channel(int(channel_id))
        except:
            class_helper = 0
        else:
            if channel != None:
                last_message = await channel.history(limit=1).flatten()
                if len(last_message) > 0:
                    last_message = last_message[0]
                    sent_at = (await unaware_timezone(
                        datetime.datetime.now(datetime.timezone.utc)) -
                               last_message.created_at)
                    sent_at = sent_at.seconds
                    if sent_at > ticket_inactivity_close_time:
                        inactive_channels.append(channel.id)
                    elif sent_at > 3 * ticket_inactivity_close_time / 4:
                        content = [last_message.content]
                        testing_vectors = vectorizer.transform(content)
                        classified_answer = classifier.predict(
                            testing_vectors)[0]
                        if classified_answer != "alive":
                            inactive_channels.append(channel.id)
    try:
        await msg.delete()
    except:
        class_helper = 0
    hashtag = "#"  # apparently my code formatting pluign sucks and was creating the next line as comment :/
    mention = await create_multiline_mention(inactive_channels,
                                             mention_helper=hashtag)
    text = f"This is a list of all inactive ticket!\n{await create_multiline_mention(inactive_channels, mention_helper=hashtag)}"
    if len(mention) < 10:
        text = f"No Such ticket found!"
    embed = discord.Embed(
        title="List of inactive tickets",
        description=text,
        color=0x2FFF70,
        timestamp=datetime.datetime.now(datetime.timezone.utc),
    )
    embed.set_footer(text=footer)
    await ctx.channel.send(embed=embed)


async def ping(ctx):
    embed = discord.Embed(title="Pong :ping_pong:",
                          timestamp=datetime.datetime.now(
                              datetime.timezone.utc),color=default_embed_color)
    embed.set_footer(text=footer)
    embed.add_field(name="Discord", value=f"`{int(bot.latency*1000)}ms`")
    embed.add_field(name="Database",value=f"`{int(measure_latency(host=db_host,port=db_port,runs=1,wait=0)[0])}ms`")
    time_then = datetime.datetime.now(datetime.timezone.utc)
    msg = await ctx.channel.send(embed=embed)
    time_now = datetime.datetime.now(datetime.timezone.utc)
    embed.add_field(
        name="Message",
        value=f"`{int(int((time_now-time_then).microseconds)/1000)}ms`")
    await msg.edit(embed=embed)


async def is_claimed(channel_id):
    prepare = f"SELECT * FROM `Tickets` WHERE `channel_id`='{str(channel_id)}'"
    database_info = Cursor.execute(prepare, return_fetchall=True)
    if database_info[0][3] == "NULL":
        return False
    else:
        return database_info[0][3]


async def is_closed(channel_id):
    prepare = f"SELECT * FROM `Tickets` WHERE `channel_id`='{str(channel_id)}'"
    database_info = Cursor.execute(prepare, return_fetchall=True)
    return database_info[0][4]


async def claim(ctx=None, channel=None, guild=None, member=None):
    if ctx != None:
        channel = ctx.channel
        guild = ctx.guild
        member = ctx.author
    yes = ["yes", "ye", "yeah", "yep"]
    ticket_info = await check_ticket(channel.id)
    if ticket_info == False:
        await channel.send(embed=await not_a_ticket())
        return
    if await is_closed(channel.id):
        embed = discord.Embed(
            description=
            "This ticket is closed. Closed tickets can't be claimed",
            color=0x0000FF,
        )
        await channel.send(embed=embed)
        return
    if str(ticket_info[0]) == str(member.id):
        embed = discord.Embed(
            description=
            "You are the ticket owner can't and claim your own ticket nerd!",
            color=0x0000FF,
        )
        await channel.send(embed=embed)
        return
    claimed_info = await is_claimed(channel.id)
    if claimed_info != False:
        embed = discord.Embed(
            description=
            f"This ticket has already been claimed by <@!{claimed_info}>, do you want to claim it?\nSay **`confirm`** if you want to snatch the claim",
            color=0x0094FF,
            title="Ticket already claimed",
            timestamp=datetime.datetime.now(datetime.timezone.utc),
        )
        embed.set_footer(text=footer)
        msg = await channel.send(embed=embed)

        def check(message):
            return (message.channel == channel and message.author == member
                    and message.content.lower() == "confirm")

        try:
            confirmation = await bot.wait_for("message",
                                              timeout=15.0,
                                              check=check)
        except asyncio.TimeoutError:
            await msg.delete()
            await channel.send("Claim aborted", delete_after=5)
            return
        else:
            embed = discord.Embed(
                description=
                f"<@!{member.id}> has snatched this ticket from you...\nif you believe this is unfair then please make a support ticket.",
                color=0xFFD600,
            )
            await channel.send(content=f"<@!{claimed_info}> **!**",
                               embed=embed)
    if (member.guild_permissions.administrator == False
            and str(member.id) not in access_privilage):
        role_check = discord.utils.get(guild.roles, id=784539526944260116)
        if role_check not in member.roles:
            embed = discord.Embed(
                description=
                f"I'm sorry but you need the <@&{expert_role_id}> role to claim a ticket....",
                color=0x0000FF,
            )
            await channel.send(embed=embed)
            return
    """
    # make sure expert is online, else dm them
    prepare = f"SELECT `ign` from `ign` WHERE `user_id`='{str(member.id)}'"
    ign = Cursor.execute(prepare, return_fetchall=True)
    if len(ign) < 1:
        dm = await member.create_dm()
        await dm.send(
            f"Hey! i don't have your ign! do `{prefix}verify` to verify\nAnyways if you wish to claim this ticketthen say `confirm` to confirm"
        )

        def check(message):
            return (message.channel == dm and message.author == member
                    and message.content.lower() == "confirm")

        try:
            confirmation = await bot.wait_for("message",
                                              timeout=15.0,
                                              check=check)
        except asyncio.TimeoutError:
            await dm.send("Claim aborted", delete_after=5)
            return
        else:
            await dm.send("Oh, in that case, you can claim the ticket!")
        # dm the user amd ask for ign or do what cloud says
    else:
        ign = str(ign[0][0])
        if (await run_with_no_exception(function=is_player_online,
                                        args=[str(ign)]) == False):
            dm = await member.create_dm()
            await dm.send(
                "My sources say that your are offline on the hypixel  network\n\nCan you get online within the next 10 mins? \nsay `confirm` to confirm"
            )

            def check(message):
                return (message.channel == dm and message.author == member
                        and message.content.lower() == "confirm")

            try:
                confirmation = await bot.wait_for("message",
                                                  timeout=15.0,
                                                  check=check)
            except asyncio.TimeoutError:
                await dm.send("Claim aborted", delete_after=5)
                return
            else:
                await dm.send("Oh, in that case, you can claim the  ticket!")"""

    prepare = (f"UPDATE `Tickets` SET `claim_id`='{member.id}' WHERE `channel_id`='{channel.id}'"
    )
    Cursor.execute(prepare)
    embed = discord.Embed(
        title="Ticket Claimed!",
        description=f"This Ticket has been claimed by <@!{member.id}>",
        timestamp=datetime.datetime.now(datetime.timezone.utc),
        color=default_embed_color
    )
    prepare = f"SELECT `user_id` FROM `Tickets` WHERE `channel_id`='{channel.id}'"
    owner_id = Cursor.execute(prepare, return_fetchall=True)[0][0]
    embed.set_footer(text=footer)
    await channel.send(
        content=
        f"<@{owner_id}> Please be sure to ask for collateral **if** applicable.",
        embed=embed)
    if str(channel.name).startswith("✔") == False:
        await channel.edit(name="✔-" + channel.name)


async def unclaim(ctx):
    channel = ctx.channel
    member = ctx.author
    content = ctx.content
    guild = ctx.guild
    if (member.guild_permissions.administrator == False
            and str(ctx.author.id) not in access_privilage):
        ticket_info = await check_ticket(channel.id)
        if ticket_info == False:
            await channel.send(embed=await not_a_ticket())
            return
        claimed_info = await is_claimed(channel.id)
        if claimed_info == False:
            embed = discord.Embed(
                description="This ticket isn't claimed by anyone",
                color=0x0000FF)
            await channel.send(embed=embed)
            return
        if str(claimed_info) != str(member.id):
            embed = discord.Embed(
                description=
                "This ticket isn't yours to unclaim, ask an admin or maybe do `{prefix}claim` to snatch the ticket",
                color=0x0000FF,
            )
            await channel.send(embed=embed)
            return
    prepare = f"UPDATE `Tickets` SET `claim_id`='NULL' WHERE `channel_id`='{channel.id}'"
    Cursor.execute(prepare)
    embed = discord.Embed(
        title="Ticket Unclaimed!",
        description=f"This Ticket has been unclaimed by <@!{member.id}>",color=default_embed_color
    )
    await channel.send(embed=embed)
    if str(channel.name)[:2] == "✔-":
        await channel.edit(name=channel.name[2:])


async def get_digit(input):
    to_be_return: str = ""
    for i in input:
        i = str(i)
        if i in "1234567890":
            to_be_return = to_be_return + i
    if to_be_return == "":
        return 0
    else:
        return int(to_be_return)


async def invalid_syntax(correct_syntax):
    embed = discord.Embed(
        title="Invalid syntax",
        description=
        f"Invalid syntax! correct syntax is `{prefix}{correct_syntax}`",
        color=0xFFD600,
        timestamp=datetime.datetime.now(datetime.timezone.utc),
    )
    embed.set_footer(text=footer)
    return embed


async def add_user(ctx):
    member = ctx.author
    content = ctx.content
    channel = ctx.channel
    guild = ctx.guild
    ticket_info = await check_ticket(channel.id)
    if ticket_info == False:
        await channel.send(embed=await not_a_ticket())
        return
    if len(content.split()) < 2:
        await channel.send(
            embed=await invalid_syntax(f"add-user <member/role id or mention>")
        )
        return
    to_be_added_id = await get_digit(content.split()[1])
    is_item_found = False
    try:
        to_be_added = await guild.fetch_member(int(to_be_added_id))
    except:
        pass
    else:
        if to_be_added != None:
            is_item_found = True
    if is_item_found == False:
        try:
            to_be_added = discord.utils.get(guild.roles,id=int(to_be_added_id))
        except:
            pass
        else:
            if to_be_added != None:
                is_item_found = True
    if is_item_found == False:
      user=await ctx.guild.query_members(query=str(" ".join(content.split()[1:])),limit=1)
      if len(user)>0:
        to_be_added=user[0]
        is_item_found=True
      else:
        try:
          to_be_added = discord.utils.get(guild.roles,name=str(" ".join(content.split()[1:])))
        except:
          pass
        else:
          if to_be_added!=None:
            is_item_found=True
          else:
            await channel.send(embed=await invalid_syntax(f"add-user <member/role id or mention>"))
            return
    await channel.set_permissions(to_be_added,read_messages=True,send_messages=True)
    await channel.send("Done!")


async def remove_user(ctx):
    member = ctx.author
    content = ctx.content
    channel = ctx.channel
    guild = ctx.guild
    ticket_info = await check_ticket(channel.id)
    if ticket_info == False:
        await channel.send(embed=await not_a_ticket())
        return
    if len(content.split()) < 2:
        await channel.send(embed=await invalid_syntax(
            f"remove-user <member/role id or mention>"))
        return
    to_be_added_id = await get_digit(content.split()[1])
    is_item_found = False
    try:
        to_be_added = await guild.fetch_member(int(to_be_added_id))
    except:
        pass
    else:
        if to_be_added != None:
            is_item_found = True
    if is_item_found == False:
        try:
            to_be_added = discord.utils.get(guild.roles,
                                            id=int(to_be_added_id))
        except:
            pass
        else:
            if to_be_added != None:
                is_item_found = True
    if is_item_found == False:
      user=await ctx.guild.query_members(query=str(" ".join(content.split()[1:])),limit=1)
      if len(user)>0:
        to_be_added=user[0]
        is_item_found=True
      else:
        try:
          to_be_added = discord.utils.get(guild.roles,name=str(" ".join(content.split()[1:])))
        except:
          pass
        else:
          if to_be_added!=None:
            is_item_found=True
          else:
            await channel.send(embed=await invalid_syntax(
            f"remove-user <member/role id or mention>"))
            return
    await channel.set_permissions(to_be_added,
                                  read_messages=False,
                                  send_messages=True)
    await channel.send("Done!")


    password = content[1]
    new_hash = content[2]
    hashed_pass = None
    with openfile_(".env", "r") as file1:
        lines = file1.readlines()
        for line in lines:
            if line.startswith("pass="):
                hashed_pass = line[5:]
                hashed_pass = hashed_pass.replace("\n", "")
        file1.close()
    if hashed_pass == None:
        await ctx.channel.send(
            "error in the code, please edit the .env file and regenerate the pass"
        )
        return
    lower_upper_alphabet = string.ascii_letters
    # password = "Yh58v#0j6AL9HjybGs"
    # $pbkdf2-sha256$29000$5FyLsVaKUaq1lhKiNOb8Hw$oP2cVfSkkhmnrKA40L4vtAhL7u9KjDc7HhyLJinE3qo
    # ggsinchat
    is_logged_in = False
    for i in lower_upper_alphabet:
        if is_logged_in == False:
            if hash_algorithm.verify(password + i, hashed_pass):
                try:
                    hash_algorithm.verify("123", new_hash)
                except:
                    await ctx.channel.send("the new password hash is invalid")
                    return
                else:
                    await ctx.channel.send("confirming the new password")
                    with openfile_(".env", "r") as file1:
                        lines = file1.readlines()
                        file1.close()
                    with openfile_(".env", "w") as file1:
                        new_lines = []
                        for line in enumerate(lines):
                            count = line[0]
                            line = line[1]
                            if line.startswith("pass="):
                                new_lines.append(f"pass={new_hash}\n")
                            else:
                                new_lines.append(line)
                        file1.writelines(new_lines)
                        file1.close()
                        is_logged_in = True
    if is_logged_in:
        access_privilage.append(ctx.author.id)
        await ctx.channel.send("confirmed the new password")
        await asyncio.sleep(600)
        access_privilage.remove(ctx.author.id)
    else:
        await ctx.channel.send("Wrong password")


async def help(ctx):
    content = ctx.content.split()
    if len(content) < 2:
        embed = discord.Embed(
            title="Please specify the module.",
            description=
            f"**Tickets**\nContains all ticket commands\n\n**Utilities**\nUtility commands\n\n**Staff commands**\nThe commands which can be used by staff",
            timestamp=datetime.datetime.now(datetime.timezone.utc),color=default_embed_color
        )
    elif content[1].lower().startswith("tick"):
        embed = discord.Embed(
            title="Here are the ticket commands",
            description=
            f"**`{prefix}close`** - closes this ticket and also unclaims it\n**`{prefix}open`** - opens a closed ticket\n**`{prefix}delete`** - deletes a ticket, also saves and dms the transcript\n**`{prefix}transcript`** - saves the transcript\n**`{prefix}ticket-info`** - gives info about the ticket\n**`{prefix}rename`** - renames the ticket\n**`{prefix}add`** - add some user or role to the ticket using their user/role id\n**`{prefix}remove`** - does the opposite of {prefix}add and removes user/role\n**`{prefix}claim`** - claims the ticket, must be a expert\n**`{prefix}unclaim`** - unclaims the ticket, must be an admin or the one to have claimed it",
            timestamp=datetime.datetime.now(datetime.timezone.utc),color=default_embed_color
        )
    elif content[1].lower().startswith("staff"):
        embed = discord.Embed(
            title="Here's the staff commands",
            description=
            f"**`{prefix}panel`** - Panel command list\n**`{prefix}inactive`** - finds ticket in which no one has spoken since {await sec_to_time(ticket_inactivity_close_time)}\n**`{prefix}say`** - make the bot say anything",
            timestamp=datetime.datetime.now(datetime.timezone.utc),color=default_embed_color
        )
    elif content[1].lower().startswith("uti"):
        embed = discord.Embed(
            title="Here's the utility commands",
            description=
            f"**`{prefix}verify`** - verify with your ign\n**`{prefix}ign <optional - user Id or mention>`** - Shows the person's ign, will show yours if sent wihout optional argument\n**`{prefix}pet-calc`** - Inbuilt Pet calculator for Pet levelling\n**`{prefix}ping`** - see the bot's ping (updated every few mins)\n**`{prefix}ticket-msg`** - see the bot's default ticket msg\n**`{prefix}eventping`** - Ping the events role\n**`{prefix}about`** - about",
            timestamp=datetime.datetime.now(datetime.timezone.utc),color=default_embed_color
        )

    else:
        embed = discord.Embed(
            title="Please specify the module.",
            description=
            f"**Tickets**\nContains all ticket commands\n\n**Utilities**\nUtility commands\n\n**Staff commands**\nThe commands which can be used by staff",
            timestamp=datetime.datetime.now(datetime.timezone.utc),color=default_embed_color
        )
    embed.set_footer(text=footer)
    await ctx.channel.send(embed=embed)


async def say(ctx):
    if (ctx.author.guild_permissions.administrator
            or str(ctx.author.id) in access_privilage):
        await ctx.delete()
        content = ctx.content[5:]
        pings = ["@everyone", "@here", "<@"]
        will_ping = False
        for i in pings:
            if "<@" in ctx.content:
                will_ping = True
        if will_ping:
            msg = await ctx.channel.send(
                "This message can ping people\nPlease say `confirm` to confirm the action"
            )

            def check(message):
                return (message.channel == ctx.channel and message.author == ctx.author
                        and message.content.lower() == "confirm")

            try:
                confirm_msg = await bot.wait_for("message",
                                                 timeout=15.0,
                                                 check=check)
            except asyncio.exceptions.TimeoutError:
                await msg.delete()
                await ctx.channel.send("ok maybe some other day",
                                       delete_after=5)
                return
            else:
                await confirm_msg.delete()
                await msg.delete()
        await ctx.channel.send(content)
    else:
        await ctx.channel.send("You don't have the perms to do this")


async def purge(ctx):
    if (ctx.author.guild_permissions.administrator == True
            or str(ctx.author.id) in access_privilage):
        await ctx.delete()
        value = await get_digit(ctx.content.split()[1])
        await ctx.channel.purge(limit=int(value))


async def crash(ctx):
    if str(ctx.author.id) in access_privilage:
        await ctx.channel.send(
            f"Bot will be crashed by `access_privilage` member: {ctx.author.id}"
        )
        quit()
    else:
        await ctx.channel.send("LOL! this command is `access_privilage` only!")


async def verify(ctx):
    try:
        await ctx.delete()
    except:
        pass
    member = ctx.author
    channel = ctx.channel
    content = ctx.content
    if len(content.split()) < 2:
        await channel.send(embed=await invalid_syntax(f"verify <ign>"),
                           delete_after=10)
        return
    ign = content.split()[1]
    discord_id = await get_player_discord(str(ign))
    if discord_id == None:
        await channel.send("Please add your Discord to your hypixel", delete_after=15)
        return
    if discord_id != str(member):
        await channel.send(
            f"<@!{member.id}> I'm sorry but this player's discord is {discord_id}",
            delete_after=10,
        )
        return
    await channel.send(f"<@!{member.id}> Verified you as {ign}")
    for i in verified_role:
        try:
            role_add = discord.utils.get(ctx.guild.roles, id=int(i))
            await member.add_roles(role_add)
        except:
            pass
    prepare = f"DELETE FROM `ign` WHERE `user_id`='{member.id}' OR `ign`='{ign}'"
    Cursor.execute(prepare)
    prepare = f"""INSERT INTO `ign` (`user_id`,`ign`)
    VALUES ('{member.id}','{ign}')"""
    Cursor.execute(prepare)


async def get_ign(ctx):
    member = ctx.author
    channel = ctx.channel
    content = ctx.content
    content_split = content.split()
    user=None
    if len(content_split) < 2:
       user_id = member.id
    else:
      user_id = await get_digit(content_split[1])
      try:
        user=await ctx.guild.fetch_member(int(user_id))
      except:        
        user=(await ctx.guild.query_members(query=str(" ".join(content_split[1:])),limit=1))
        if len(user)<1:
          await ctx.channel.send("Not a valid username/nickname, please type in their full nickname/username/ping them")
          return
          user_id=user[0].id
    prepare = f"SELECT `ign` from `ign` WHERE `user_id`='{user_id}' LIMIT 1"
    ign = await reformat_list(Cursor.execute(prepare, return_fetchall=True))
    if len(ign) < 1:
        await channel.send("They haven't verified!")
        return
    else:
        msg_content = f"Their ign is {ign[0]}"
        msg = await channel.send(msg_content)
        msg_content = f"<@{user_id}>'s ign is {ign[0]}"
        await msg.edit(content=msg_content)


async def panel_add(ctx):
    if await is_not_admin(ctx.author):
        await ctx.channel.send("You don't have the perms to do this.")
        return
    member = ctx.author
    channel = ctx.channel
    content = ctx.content

    async with channel.typing():
        await asyncio.sleep(1)
        await channel.send(
            "So you wanna create a new panel <:SBS_yawn:809248209121574933>.   Say **cancel** if you want to cancel"
        )
        await asyncio.sleep(1.5)
        await channel.send(
            "Please tell me the name of the panel <:SBS_BlobCookie:762455347977519124>\nFor example **dungeon-carrying** or **afking**"
        )

    async def is_cancelled(content):
        if content.lower() == "cancel":
            await channel.send(timeout_msg)
            return True
        else:
            return False

    def check(message):
        return message.channel == channel and message.author == member

    try:
        msg = await bot.wait_for("message", timeout=15.0, check=check)
    except asyncio.TimeoutError:
        await channel.send(timeout_msg)
        return
    name = msg.content
    if await is_cancelled(name):
        return
    async with channel.typing():
        await asyncio.sleep(1)
        await channel.send(
            f"Okey! the name will be set to **{name}** <:rooBigMoney:809260048294608918>\n\nWhat should be the prefix of the ticket?\nFor eaxmple, for **bit-009** say **bit**"
        )
    try:
        msg = await bot.wait_for("message", timeout=15.0, check=check)
    except asyncio.TimeoutError:
        await channel.send(timeout_msg)
        return
    ticket_prefix = msg.content
    if await is_cancelled(ticket_prefix):
        return
    async with channel.typing():
        await asyncio.sleep(1)
        await channel.send(
            f"Yes, the prefix will be set to **{ticket_prefix}**\nNow tell me the Id of the category in which the tickets should be made?right click the category and select copy id, also make sure to set the category permissions <:SBS_sharkHi:809244998679134269>"
        )
    try:
        msg = await bot.wait_for("message", timeout=30.0, check=check)
    except asyncio.TimeoutError:
        await channel.send(timeout_msg)
        return
    ticket_category = msg.content
    if await is_cancelled(ticket_category):
        return
    ticket_category = await get_digit(ticket_category)
    if (ticket_category) < 1:
        await channel.send("Invalid category")
        return
    async with channel.typing():
        await asyncio.sleep(1)
        await channel.send(
            f"Hmm..... the category will be set to **{await get_category(int(ticket_category))}**\n\nSo which channel should I send the ticket creation message? mention it or type name plz :pleading_face:"
        )
    try:
        msg = await bot.wait_for("message", timeout=30.0, check=check)
    except asyncio.TimeoutError:
        await channel.send(timeout_msg)
        return
    ticket_channel = msg.content
    if await is_cancelled(ticket_channel):
        return
    ticket_channel = discord.utils.get(ctx.guild.text_channels, name=ticket_channel)
    if ticket_channel==None:
      try:
          ticket_channel = await bot.fetch_channel(await get_digit(msg.content))
      except:
          await channel.send("Invalid channel")
          return
      if ticket_channel == None:
          await channel.send("Invalid channel")
          return
    async with channel.typing():
        await asyncio.sleep(1)
        await channel.send(
            file=discord.File("ticket_msg.png"),
            content=
            f"K, so I will send the ticket message to **<#{ticket_channel.id}>**\nOne last thing to bother you <a:popcorngirlSBS:809249000921235457>, do you want a custom ticket msg? usually the defaults works well but you never know <:SBS_iceCreamCat:809248987059454024>\nSay `none` to go with default (this can edited later)",
        )
    try:
        msg = await bot.wait_for("message", timeout=60.0, check=check)
    except asyncio.TimeoutError:
        await channel.send(timeout_msg)
        return
    msg_text = msg.content
    if await is_cancelled(msg_text):
        return
    if msg_text.lower() in ["default", "no", "none"]:
        msg_text = "Null"
        send_text = "default"
    else:
        send_text = msg_text
    async with channel.typing():
        await asyncio.sleep(1)
        stuff=f"ahh yes! the msg text has been set to {send_text}, gimme a second to compile everything"
        uwu=await channel.send(stuff.replace("@","")
        )
        await uwu.edit(content=stuff)
    embed = discord.Embed(
        title=name,
        description=f"React with {ticket_reaction} to create a ticket.",color=default_embed_color)
    embed.set_footer(text=footer)
    msg = await ticket_channel.send(embed=embed)
    await msg.add_reaction(ticket_reaction)
    prepare = f"""INSERT INTO `Panel` (`name`,`ticket_prefix`,`ticket_category`,`msg_id`,`ticket_number`,`msg_text`)
    VALUES ('{name}','{ticket_prefix}','{ticket_category}','{msg.id}','000','{msg_text}')"""
    Cursor.execute(prepare)
    await channel.send("YAY! the panel has been sucessfully created!")


async def panel_remove(ctx):
    async def is_cancelled(content):
        if content.lower() == "cancel":
            await channel.send(timeout_msg)
            return True
        else:
            return False

    if await is_not_admin(ctx.author):
        await ctx.channel.send("You don't have the perms to do this.")
        return
    member = ctx.author
    channel = ctx.channel
    content = ctx.content
    await channel.send(
        "What is the name of the Panel that you're trying to delete? say **cancel** to cancel"
    )

    def check(message):
        return message.channel == channel and message.author == member

    try:
        msg = await bot.wait_for("message", timeout=15.0, check=check)
    except asyncio.TimeoutError:
        await channel.send(timeout_msg)
        return
    name = msg.content
    if await is_cancelled(name):
        return
    prepare = f"SELECT `name` from `Panel` WHERE `name` LIKE '%{name}%' LIMIT 1"
    panel_name=Cursor.execute(prepare,return_fetchall=True)
    if len(panel_name)<1:
      await channel.send(
            "There is no such Panel <:SBS_idk:723478539596333066>\nPlease check the panel name and try again"
        )
      return
    panel_name=panel_name[0][0]
    await channel.send(
        f"Are you sure you wanna delete **{panel_name}**?\nSay **confirm** to confirm")

    def check(message):
        return (message.channel == channel and message.author == member
                and message.content in ["confirm", "cancel"])

    try:
        msg = await bot.wait_for("message", timeout=15.0, check=check)
    except asyncio.TimeoutError:
        await channel.send(timeout_msg)
        return
    else:
        if await is_cancelled(msg.content):
            return
    prepare = f"DELETE FROM `Panel` WHERE `name`='{panel_name}'"
    Cursor.execute(prepare)
    await channel.send(
        f"Done! Panel **{panel_name}** has been deleted <:SBS_tommypog:770346000208232479>"
    )


async def panel_list(ctx):
    if await is_not_admin(ctx.author):
        await ctx.channel.send("You don't have the perms to do this.")
        return
    prepare = "SELECT `name` FROM `Panel`"
    panels = await reformat_list(Cursor.execute(prepare, return_fetchall=True))
    panels = "\n".join(panels)
    embed = discord.Embed(title="Panels",
                          description="**" + panels + "**",
                          color=0x2FFF70)
    embed.set_footer(text=footer)
    await ctx.channel.send(embed=embed)


async def is_not_admin(member):
    return (member.guild_permissions.administrator == False
            and str(member.id) not in access_privilage)


async def panel_info(ctx):
    if await is_not_admin(ctx.author):
        await ctx.channel.send("You don't have the perms to do this.")
        return
    content = ctx.content.split()
    channel = ctx.channel
    if content[0].lower()==prefix+"panel":
      content=content[1:]
    if len(content) < 2:
        await channel.send(
            embed=await invalid_syntax(f"panel-info <panel name>"))
        return
    del content[0]
    name = " ".join(content)
    prepare = f"SELECT `name`,`ticket_prefix`,`ticket_category`,`msg_id`,`ticket_number`,`msg_text` FROM `Panel` WHERE `name` LIKE '%{name}%' LIMIT 1"
    panel = Cursor.execute(prepare, return_fetchall=True)
    if len(panel) < 1:
        await channel.send(
            f"There is no Panel named as **{name}**. Please do {prefix}panel-list to see a list of Panels."
        )
        return
    panel = panel[0]
    if panel[5] == None:
        msg_text = "Default"
    else:
        msg_text = panel[5]
    description = f"**Name**: {panel[0]}\n**Prefix**: {panel[1]}\n**Category**: {await get_category(int(panel[2]))}\n**Msg Id**: {panel[3]}\n**Next Ticket** {str(int(panel[4])+1).zfill(3)}\n**Msg Text**: {msg_text}"
    embed = discord.Embed(
        title=panel[0],
        description=description,
        color=0x2FFF70,
        timestamp=datetime.datetime.now(datetime.timezone.utc),
    )
    embed.set_footer(text=f"Do {prefix}panel-help for assistance")
    await channel.send(embed=embed)


async def panel_help(ctx):
    description = "**Name**: This is the name of Panel is shown in the reaction message and is also used to view/delete/modiy panels.\n\n**Prefix**: This is the prefix which is used in the ticket name, example **bit**-257.\n\n**Category**: Id of the category in which the ticket will be created, it's settings need to be setup, as all ticket by default sync to it's settings.\n\n**Msg Id**: This is the Id of the message where people react to create tickets.\n\n**Next Ticket** The number of the next ticket to be created, in the db it is stored as current number and is incremented before ticket is made.\n\n**Msg Text**: This is the text that is sent in the embed when a ticket is created."
    embed = discord.Embed(title="Panel Help", description=description,color=default_embed_color)
    embed.set_footer(text=f"Do {prefix}panel for list of commands")
    await ctx.channel.send(embed=embed)


async def panel_edit(ctx):
    async def is_cancelled(content):
        if content.lower() == "cancel":
            await channel.send(timeout_msg)
            return True
        else:
            return False

    if await is_not_admin(ctx.author):
        await ctx.channel.send("You don't have the perms to do this.")
        return
    channel = ctx.channel
    member = ctx.author

    def check(message):
        return message.channel == channel and message.author == member

    async with channel.typing():
        await asyncio.sleep(1)
        await channel.send(
            "Oh so you want to edit a Panel <:SBS_peepoG:804884379650228244>\nBtw you can **cancel** to cancel this process"
        )
        await asyncio.sleep(1)
        await channel.send(
            "Tell me name of the Panel you wish to modify <a:rainbowcatSBS:799803970808840222>"
        )
    try:
        msg = await bot.wait_for("message", timeout=15.0, check=check)
    except asyncio.TimeoutError:
        await channel.send(timeout_msg)
        return
    if await is_cancelled(msg.content):
        return
    name = msg.content
    prepare = f"SELECT `name` FROM `Panel` WHERE `name` LIKE '%{name}%' LIMIT 1"
    panel_name=Cursor.execute(prepare, return_fetchall=True)
    if len(panel_name)<1:
        await channel.send(f"There is no Panel with a name of {name}")
        return
    panel_name=panel_name[0][0]
    async with channel.typing():
        await asyncio.sleep(1)
        await channel.send(
            f"So the panel is **{panel_name}**, What attribute you wanna modify?\n*{prefix}panel-help* <a:Rainbow_Blob_TrashSBS:809246883423322113>"
        )
    try:
        msg = await bot.wait_for("message", timeout=15.0, check=check)
    except asyncio.TimeoutError:
        await channel.send(timeout_msg)
        return
    if await is_cancelled(msg.content):
        return
    attribute = msg.content.lower()
    if attribute in ["name", "names", "panel name", "panel names"]:
        attribute = "name"
    elif attribute in ["prefix", "ticket prefix", "ticket_prefix"]:
        attribute = "ticket_prefix"
    elif attribute in [
            "category", "ticket category", "ticket_category", "category id"
    ]:
        attribute = "ticket_category"
    elif attribute in ["msg id", "id of msg", "msg_id", "id msg"]:
        attribute = "msg_id"
    elif attribute in ["ticket value","number","ticket_number","ticket number","next ticket"]:
        attribute = "ticket_number"
    elif attribute in ["msg text", "text of msg", "msg_text", "text msg","text"]:
        attribute = "msg_text"
    else:
        await channel.send(
            f"Thats not a valid attribute <a:dogebonkSBS:809244948075118643> !\nDo **{prefix}panel-help** to see a list of attributes"
        )
        return
    async with channel.typing():
        await asyncio.sleep(1)
        await channel.send(
            f"Okey thats a valid attribute(or alias) <a:hypeSBS:783053625021694012>, What should be the new value be?"
        )
    try:
        msg = await bot.wait_for("message", timeout=15.0, check=check)
    except asyncio.TimeoutError:
        await channel.send(timeout_msg)
        return
    if await is_cancelled(msg.content):
        return
    new_value = msg.content
    print(new_value)
    await channel.send(
        "Are you sure that you want to do this change? Say `confirm` to confirm or `cancel` to cancel"
    )

    def check(message):
        return (message.channel == channel and message.author == member
                and message.content.lower() in ["confirm", "cancel"])

    try:
        msg = await bot.wait_for("message", timeout=15.0, check=check)
    except asyncio.TimeoutError:
        await channel.send(timeout_msg)
        return
    if await is_cancelled(msg.content):
        return
    prepare = (
        f"UPDATE `Panel` SET `{attribute}`='{new_value}' WHERE `name` LIKE '%{panel_name}%'"
    )
    Cursor.execute(prepare)
    if attribute=="name":
      prepare=f"UPDATE `Tickets` SET `category`='{new_value}' WHERE `category`='{panel_name}'"
      Cursor.execute(prepare)
    await channel.send("Done!")


async def panel(ctx):
  if len(ctx.content.split())<2:
    description = f"Panel is basically a system of adding ticketing, for example add ticketing feature to **Dungeon Carrying** service\n**{prefix}panel list** : Lists all Panels\n**{prefix}panel info** : Displays information about a Panel\n**{prefix}panel add** : Add a Panel\n**{prefix}panel remove** : removes a Panel\n**{prefix}panel edit** : Edits a Panel\n**{prefix}panel send** : Resends a Panel message\n**{prefix}panel help** : Lists all the attributes"
    embed = discord.Embed(title="Panel", description=description,color=default_embed_color)
    embed.set_footer(text=footer)
    await ctx.channel.send(embed=embed)
  else:
    sub_commands={
            "add": panel_add,
            "remove": panel_remove,
            "list": panel_list,
            "info": panel_info,
            "help": panel_help,
            "edit": panel_edit,
            "send":panel_send}
    sub_command = sub_commands.get(ctx.content.split()[1])
    if sub_command != None:
      await sub_command(ctx=ctx)



async def pet_calc(ctx):
    #print(get_info(rarity=1,goal=100,xp_boost=0,current_level=0,current_xp=0,price=0.6,skill=None))
    channel = ctx.channel
    member = ctx.author
    rarity_table = {
        "legendary": 5,
        "epic": 4,
        "rare": 3,
        "uncommon": 2,
        "common": 1
    }
    skill_table = [
        "combat", "mining", "farming", "foraging", "alchemy", "fishing"
    ]
    content = ctx.content.split()
    embed = discord.Embed(
        title="Invalid syntax",
        description=
        f"Invalid syntax! either just do **`{prefix}pet-calc`**\nOr do \n`{prefix}pet-calc <rarity> <current level> <current xp> <goal> <skill> <optional:exp boost item>`",
        color=0xFFD600,
        timestamp=datetime.datetime.now(datetime.timezone.utc),
    )
    embed.set_footer(text=footer)
    if len(content) in [6, 7]:
        rarity = rarity_table.get(content[1])
        if rarity == None:
            await channel.send(embed=embed)
            return
        current_level = await get_digit(content[2])
        current_xp = await get_digit(content[3])
        goal = await get_digit(content[4])
        skill = content[5]
        if skill not in skill_table:
            await channel.send(
                "Invalid skill   <:SBS_ZeroLurk:809247965281648691>\nValid rarity include combat,farming,alchemy,fishing,foraging and mining"
            )
            return
        try:
            xp_boost = await get_digit(content[6])
        except:
            xp_boost = 0
        pet_info = await get_info(rarity=rarity,
                                  goal=goal,
                                  xp_boost=xp_boost,
                                  current_level=current_level,
                                  current_xp=current_xp,
                                  skill=skill)
        await channel.send(
            f"**Price** = {pet_info.price} \n**Xp needed** = {pet_info.xp}\n\n  {pet_info.explain}"
        )
        return
    if len(content) > 1:
        await channel.send(embed=embed)
        return
    question = await channel.send(
        "Oh, so what is the rarity of the pet?\nSay `cancel` to cancel")

    def check(message):
        return message.channel == channel and message.author == member

    try:
        msg = await bot.wait_for("message", timeout=15.0, check=check)
    except asyncio.TimeoutError:
        await channel.send(timeout_msg)
        return
    else:
        if msg.content.lower() == "cancel":
            await channel.send(timeout_msg)
            return
    await question.delete()
    try:
        await msg.delete()
    except:
        pass
    rarity = rarity_table.get(msg.content.lower())
    if rarity == None:
        await channel.send(
            "Invalid rarity <:SBS_ZeroLurk:809247965281648691>\nValid rarity include legendary,epic,rare,uncommon and common"
        )
        return
    question = await channel.send(
        "Whats the **current** level of the pet <:SBS_owosneaky:762216062888443924>?"
    )
    try:
        msg = await bot.wait_for("message", timeout=15.0, check=check)
    except asyncio.TimeoutError:
        await channel.send(timeout_msg)
        return
    else:
        if msg.content.lower() == "cancel":
            await channel.send(timeout_msg)
            return
    await question.delete()
    try:
        await msg.delete()
    except:
        pass
    current_level = await get_digit(msg.content)
    question = await channel.send("How much xp does it have in the bar?")
    try:
        msg = await bot.wait_for("message", timeout=15.0, check=check)
    except asyncio.TimeoutError:
        await channel.send(timeout_msg)
        return
    else:
        if msg.content.lower() == "cancel":
            await channel.send(timeout_msg)
            return
    await question.delete()
    try:
        await msg.delete()
    except:
        pass
    current_xp = await get_digit(msg.content)
    question = await channel.send(
        "What should be the level of the pet after service??? <a:wiggleSBS:799803917033930823>"
    )
    try:
        msg = await bot.wait_for("message", timeout=15.0, check=check)
    except asyncio.TimeoutError:
        await channel.send(timeout_msg)
        return
    else:
        if msg.content.lower() == "cancel":
            await channel.send(timeout_msg)
            return
    await question.delete()
    try:
        await msg.delete()
    except:
        pass
    goal = await get_digit(msg.content)
    question = await channel.send("What skill is the pet?")
    try:
        msg = await bot.wait_for("message", timeout=15.0, check=check)
    except asyncio.TimeoutError:
        await channel.send(timeout_msg)
        return
    else:
        if msg.content.lower() == "cancel":
            await channel.send(timeout_msg)
            return
    await question.delete()
    try:
        await msg.delete()
    except:
        pass
    skill = msg.content.lower()
    if skill not in skill_table:
        await channel.send(
            "Invalid skill <:SBS_ZeroLurk:809247965281648691>\nValid rarity include combat,farming,alchemy,fishing,foraging and mining"
        )
        return
    question = await channel.send(
        "How much exp boost item it has? say 0 if none")
    try:
        msg = await bot.wait_for("message", timeout=15.0, check=check)
    except asyncio.TimeoutError:
        await channel.send(timeout_msg)
        return
    else:
        if msg.content.lower() == "cancel":
            await channel.send(timeout_msg)
            return
    await question.delete()
    try:
        await msg.delete()
    except:
        pass
    xp_boost = await get_digit(msg.content)
    pet_info = await get_info(rarity=rarity,
                              goal=goal,
                              xp_boost=xp_boost,
                              current_level=current_level,
                              current_xp=current_xp,
                              skill=skill)
    await channel.send(
        f"**Price** = {pet_info.price}\n**Xp needed** = {pet_info.xp}\n\n{pet_info.explain}"
    )


async def send_default_ticket_msg(ctx):
  pings=[]
  #for i in default_ticket_msg.split("<@"):
    #if i[0] in ["!","&"] and i[1:19]==str(await get_digit(i[1:19])) and "<@"+i[:21] not in pings:
      #pings.append("<@"+i[:21])
  embed = discord.Embed(
    description=default_ticket_msg,
    color=0x0094FF,
    timestamp=datetime.datetime.now(datetime.timezone.utc),
)
  embed.set_footer(text=footer)
  msg = await ticket.send(content=f"<@!{ctx.author.id}>,"+" ,".join(ping),embed=embed)
  await msg.add_reaction(close_reaction)
  await msg.add_reaction(claim_reaction)
    


async def discount_market(ctx):
    member = ctx.author
    guild = ctx.guild
    channel = await member.create_dm()
    await channel.send("Howdy!, you made a discount")

async def change_prefix(ctx):
  if await is_not_admin(ctx.author):
    await ctx.channel.send("You don't have the perms")
    return
  content=ctx.content.split()
  if len(content)<2:
    await channel.send("Pls tell the new prefix next time")

async def panel_send(ctx):
  if await is_not_admin(ctx.author):
    await ctx.channel.send("You do not have the perms to do that")
    return
  channel=ctx.channel
  member=ctx.author
  await channel.send(
        "What Panel are you trying to send? say its name. Say **cancel** to cancel"
    )
  def check(message):
      return message.channel == channel and message.author == member
  try:
      msg = await bot.wait_for("message", timeout=15.0, check=check)
  except asyncio.TimeoutError:
      await channel.send(timeout_msg)
      return
  name = msg.content.lower()
  if name=="cancel":
    await channel.send(timeout_msg)
    return
  prepare=f"SELECT `name` FROM `Panel` WHERE `name` LIKE '%{name}%' LIMIT 1"
  panel_name=Cursor.execute(prepare,return_fetchall=True)
  if len(panel_name)<1:
    await channel.send("No such panel exists <:SBS_veryangryboi:800900873101639730>")
    return
  panel_name=panel_name[0][0]
  await channel.send(f"Ahh Yes, I think you meant {panel_name}\nSo tell me the channel to send this to (mention / name / channel id)")
  try:
      msg = await bot.wait_for("message", timeout=15.0, check=check)
  except asyncio.TimeoutError:
      await channel.send(timeout_msg)
      return
  ticket_channel = msg.content.lower()
  if ticket_channel=="cancel":
    await channel.send(timeout_msg)
    return
  ticket_channel = discord.utils.get(ctx.guild.text_channels, name=ticket_channel)
  if ticket_channel==None:
    try:
        ticket_channel = await bot.fetch_channel(await get_digit(msg.content))
    except:
        await channel.send("Invalid channel")
        return
    if ticket_channel == None:
        await channel.send("Invalid channel")
        return
  embed = discord.Embed(
      title=panel_name,
      description=f"React with {ticket_reaction} to create a ticket.",color=default_embed_color)
  embed.set_footer(text=footer)
  msg = await ticket_channel.send(embed=embed)
  await msg.add_reaction(ticket_reaction)
  await channel.send(f"Done! your panel is now in <#{ticket_channel.id}>")
  prepare=f"UPDATE `Panel` SET `msg_id`='{msg.id}' WHERE `name`='{panel_name}'"
  Cursor.execute(prepare)

async def about(ctx):
  embed=discord.Embed(description="Made by <@!640773439115886642>! <:SBS_BunnyHype:811193964991348746>",color=0xFF0000)
  embed.set_footer(text="Skytickets!")
  await ctx.channel.send(embed=embed)
@bot.event
async def on_message(ctx):
    await bot.wait_until_ready()
    allow_dm = [
        "help","verify", "ping", "inactive", "pet-calc", "ign",
        "ticket-msg"
    ]
    member = ctx.author
    content = ctx.content
    channel = ctx.channel
    guild = ctx.guild
    if isinstance(ctx.channel, discord.channel.DMChannel):
        allowed = False
        for i in allow_dm:
            if content.startswith(prefix + i):
                allowed = True
        if allowed == False:
            return
    if content.startswith("You must wait") and str(
            member.id) == "806630385696899124":
        async with ctx.channel.typing():
            await asyncio.sleep(1)
        await ctx.channel.send("Told ya, this bot is useless af",
                               delete_after=4)
    if "<@&763573152122404894>" in content and str(
            member.id) == "806630385696899124":
        async with ctx.channel.typing():
            await asyncio.sleep(1)
        await ctx.channel.send("bro <@806630385696899124> why u ping dude",
                               delete_after=4)
    if (str(member.id) in ["159985870458322944", "806630385696899124"]
            and "level" in content):
        async with ctx.channel.typing():
            await asyncio.sleep(1)
        await ctx.channel.send(
            "these bots just want a reason to ping and thats it <:SBS_ningkaibruh:797213782115090444>",
            delete_after=4,
        )

    if member.bot == True and member.id != bot.user.id:
        return
    if content == f"<@!{bot.user.id}>":
        await ctx.channel.send(f"My prefix is `{prefix}`")

    if content.startswith(prefix):
        commands = {
            "close": close,
            "open": open,
            "claim": claim,
            "unclaim": unclaim,
            "delete": delete,
            "transcript": transcript,
            "ticket-info": ticket_info,
            "add": add_user,
            "remove": remove_user,
            "rename": rename,
            "help": help,
            "inactive": find_inactive_tickets,
            "ping": ping,
            "t-refresh-database": update_database,
            "say": say,
            "purge": purge,
            "t-crash": crash,
            "verify": verify,
            "ign": get_ign,
            "panel-add": panel_add,
            "panel-remove": panel_remove,
            "panel-list": panel_list,
            "panels":panel_list,
            "panel-info": panel_info,
            "panel-help": panel_help,
            "panel-edit": panel_edit,
            "panel": panel,
            "panel-send":panel_send,
            "pet-calc": pet_calc,
            "pet":pet_calc,
            "ticket-msg": send_default_ticket_msg,
            "about":about,
            "eventping":eventping
        }
        command = commands.get(content[len(prefix):].split()[0])
        if command != None:
            await command(ctx=ctx)

async def eventping(ctx):
  event_manager=discord.utils.get(ctx.guild.roles, id=1026195273149587568)
  if event_manager not in ctx.author.roles:
    await ctx.channel.send("You do not have the permissions required for this command.")
  else:
    await ctx.channel.send("<@&980385233360785498>")


@bot.event
async def on_member_remove(member):
    prepare = f"DELETE FROM `ign` WHERE `user_id`='{member.id}'"
    Cursor.execute(prepare)
    prepare = f"""SELECT * From `Tickets` WHERE `user_id`='{member.id}'"""
    database_info = Cursor.execute(prepare, return_fetchall=True)
    for channel_id in database_info:
        channel_id = channel_id[1]
        channel = await bot.fetch_channel(int(channel_id))
        msg = await channel.send(content=prefix + "close")
        await msg.delete()
    prepare = f"""SELECT * From `Tickets` WHERE `claim_id`='{member.id}'"""
    database_info = Cursor.execute(prepare, return_fetchall=True)
    for channel_id in database_info:
        channel_id = channel_id[1]
        channel = await bot.fetch_channel(int(channel_id))
        msg = await channel.send(content=prefix + "unclaim")
        await msg.delete()


bot.run(TOKEN)

#813149690610450442
#813230015868305408
#813242472616165446
#813152257838153728
#812740067184869426

#416385958544670741 - 813149690610450442 - AFKing - NONE - 0
#725752774591250554 - 813230015868305408 - Leveling Services (Pet Leveling) - NONE - 1
#735294947300868158 - 813242472616165446 - Item Rental - NONE - 1
#568137086226661379 - 813152257838153728 - Essence Crafting - NONE - 1
#644688461051330561 - 812740067184869426 - Leveling Services (Pet Leveling) - NONE- 1
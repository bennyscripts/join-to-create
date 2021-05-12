import discord
import asyncio
import json
import os
from discord.ext import commands

# COPYRIGHT: Arty, Benny.

TOKEN = json.load(open("config.json"))["token"]
DEFAULTPREFIX = json.load(open("config.json"))["default_prefix"]
INVITE = "https://discord.com/api/oauth2/authorize?client_id=838084070986350642&permissions=8&scope=bot"

EMBEDFOOTER = "Developed by Arty & Benny"

STATUSTEXT = f"{DEFAULTPREFIX}help | Arty™️"

def add_privateChannel(ownerId, channelId, private: bool):
    privateChannels = json.load(open("data/privateChannels.json"))
    privateChannels[str(ownerId)] = {}
    privateChannels[str(ownerId)]["channelId"] = str(channelId)
    privateChannels[str(ownerId)]["private"] = bool(private)
    json.dump(privateChannels, open('data/privateChannels.json', 'w'))    

def remove_privateChannel(ownerId):
    privateChannels = json.load(open("data/privateChannels.json"))
    privateChannels.pop(str(ownerId), True)
    json.dump(privateChannels, open('data/privateChannels.json', 'w'))   

def get_privateChannels(ownerId = None):
    if ownerId is not None:
        return json.load(open("data/privateChannels.json"))[str(ownerId)]

    else:
        return json.load(open("data/privateChannels.json"))

def get_channel(guildId):
    return json.load(open("data/channels.json"))[str(guildId)]

def set_channel(guildId, channelId):
    channels = json.load(open("data/channels.json"))
    channels[str(guildId)] = str(channelId)
    json.dump(channels, open('data/channels.json', 'w'))

def get_category(guildId):
    return json.load(open("data/categories.json"))[str(guildId)]

def set_category(guildId, categoryId):
    categories = json.load(open("data/categories.json"))
    categories[str(guildId)] = str(categoryId)
    json.dump(categories, open('data/categories.json', 'w'))    

def get_prefix2(bot, message):
    return json.load(open("data/prefixes.json", "r"))[str(message.guild.id)]

def get_prefix(guildId):
    return json.load(open("data/prefixes.json", "r"))[str(guildId)]

def set_prefix(guildId, prefix):
    prefixes = json.load(open("data/prefixes.json"))
    prefixes[str(guildId)] = str(prefix)
    json.dump(prefixes, open('data/prefixes.json', 'w'))

bot = commands.Bot(command_prefix=get_prefix2, activity=discord.Game(STATUSTEXT))
bot.remove_command("help")

@bot.event
async def on_ready():
    print("bot online")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        embed = discord.Embed(title="\❌ Error", description="That command doesn't exist.")
        embed.set_footer(text=EMBEDFOOTER)
        
        await ctx.send(embed=embed)

    elif isinstance(error, commands.BadArgument):
        embed = discord.Embed(title="\❌ Error", description="Missing an argument.")
        embed.set_footer(text=EMBEDFOOTER)
        
        await ctx.send(embed=embed)

    else:
        embed = discord.Embed(title="\❌ Error", description="There was a big error that I can't handle* \😩")
        embed.set_footer(text=EMBEDFOOTER)        
        
        await ctx.send(embed=embed)
        print("[ERROR]", str(error))

@bot.event
async def on_guild_join(guild):
    category = await guild.create_category(name='Private Channels')
    channel = await category.create_voice_channel("➕ New Room")
    set_channel(guild.id, channel.id)
    set_category(guild.id, category.id)
    set_prefix(guild.id, DEFAULTPREFIX)

@bot.event
async def on_voice_state_update(member, before, after):    
    if before.channel is None and after.channel is not None:
        if after.channel.id == int(get_channel(member.guild.id)):
            if str(member.id) not in json.load(open("data/privateChannels.json")):
                category = discord.utils.get(member.guild.categories, id=int(get_category(member.guild.id)))
                privateChannel = await category.create_voice_channel(f"{member}'s room")
                add_privateChannel(f"{member.id}", f"{privateChannel.id}", False)
                await member.move_to(privateChannel)                

@bot.command(aliases=["cmds", "commands"])
async def help(ctx):    
    prefix = get_prefix(ctx.guild.id)
    helpmsg = f"""
- `{prefix}`invite : The bots invite link.
- `{prefix}`setup : Setup the bot.
- `{prefix}`vc : Voice channel commands.
"""

    embed = discord.Embed(title="\📖 Commands", description=helpmsg)
    embed.set_footer(text=EMBEDFOOTER)

    await ctx.send(embed=embed)

@bot.command()
async def invite(ctx):
    msg = f"""
Invite me with the link below!
- <{INVITE}>
    """

    embed = discord.Embed(title="\💨 Invite", description=msg)
    embed.set_footer(text=EMBEDFOOTER)

    await ctx.send(embed=embed)

@bot.group()
async def vc(ctx):
    if str(ctx.author.id) in json.load(open("data/privateChannels.json")):
        if ctx.invoked_subcommand is None:
            prefix = get_prefix(ctx.guild.id)
            embed = discord.Embed(title="\🎙️ Voice Channel", description=f"Commands:\n- *`{prefix}vc me`*\n- *`{prefix}vc close`*\n- *`{prefix}vc private`*")
            embed.set_footer(text=EMBEDFOOTER)

            await ctx.send(embed=embed)

    else:
        embed = discord.Embed(title="\❌ Error", description="You dont own a voice channel.")
        embed.set_footer(text=EMBEDFOOTER)

        await ctx.send(embed=embed)

@vc.command()
async def me(ctx):
    if str(ctx.author.id) in json.load(open("data/privateChannels.json")):
        private = json.load(open("data/privateChannels.json"))[f"{ctx.author.id}"]["private"]
        channel = discord.utils.get(ctx.guild.channels, id=int(json.load(open("data/privateChannels.json"))[f"{ctx.author.id}"]["channelId"]))

        embed = discord.Embed(title="\🎙️ Your Channel", description=f"*Channel : `{channel.name}`*\n- *Private : `{private}`*")
        embed.set_footer(text=EMBEDFOOTER)

        await ctx.send(embed=embed)

@vc.command()
async def close(ctx):
    if str(ctx.author.id) in json.load(open("data/privateChannels.json")):
        channel = discord.utils.get(ctx.guild.channels, id=int(json.load(open("data/privateChannels.json"))[f"{ctx.author.id}"]["channelId"]))
        await channel.delete()

        remove_privateChannel(ctx.author.id)

        embed = discord.Embed(title="\✔️ Success", description="Closed your channel successfully.")
        embed.set_footer(text=EMBEDFOOTER)

        await ctx.send(embed=embed)

@vc.command()
async def private(ctx):
    if str(ctx.author.id) in json.load(open("data/privateChannels.json")):
        channel = discord.utils.get(ctx.guild.channels, id=int(json.load(open("data/privateChannels.json"))[f"{ctx.author.id}"]["channelId"]))
        private = json.load(open("data/privateChannels.json"))[f"{ctx.author.id}"]["private"]
        if private is False:
            await channel.set_permissions(ctx.guild.default_role, connect=False)
            await channel.set_permissions(ctx.author, connect=True)

            remove_privateChannel(str(ctx.author.id))
            add_privateChannel(str(ctx.author.id), str(channel.id), True)
            
            embed = discord.Embed(title="\✔️ Success", description="Your voice channel is now private.")
            embed.set_footer(text=EMBEDFOOTER)

            await ctx.send(embed=embed)       
        else:
            await channel.set_permissions(ctx.guild.default_role, connect=True)

            remove_privateChannel(str(ctx.author.id))
            add_privateChannel(str(ctx.author.id), str(channel.id), False)

            embed = discord.Embed(title="\✔️ Success", description="Your voice channel is no longer private.")
            embed.set_footer(text=EMBEDFOOTER)

            await ctx.send(embed=embed)

@bot.group()
async def setup(ctx):
    if ctx.author.guild_permissions.administrator:
        if ctx.invoked_subcommand is None:
            prefix = get_prefix(ctx.guild.id)
            
            embed = discord.Embed(title="\⚙️ Setup", description=f"Commands:\n- *`{prefix}setup channel (id)`*\n- *`{prefix}setup category (id)`*\n- *`{prefix}setup prefix (prefix)`*")
            embed.set_footer(text=EMBEDFOOTER)

            await ctx.send(embed=embed)            

    else:
        embed = discord.Embed(title="\❌ Invalid Permissions", description="Contact and admin if you believe this is incorrect.")
        embed.set_footer(text=EMBEDFOOTER)

        await ctx.send(embed=embed)

@setup.command()
async def channel(ctx, channelId: int = None):
    if ctx.author.guild_permissions.administrator:
        if channelId is not None:
            set_channel(ctx.guild.id, channelId)
            channel = discord.utils.get(ctx.guild.voice_channels, id=int(get_channel(ctx.guild.id)))
            
            embed = discord.Embed(title="\✔️ Channel Set", description=f"Successfully set channel to `{channel.name}`")
            embed.set_footer(text=EMBEDFOOTER)

            await ctx.send(embed=embed)              

        else:
            prefix = get_prefix(ctx.guild.id)
            
            embed = discord.Embed(title="\❌ Invalid Usage", description=f"Try: `{prefix}setup channel (id)`")
            embed.set_footer(text=EMBEDFOOTER)

            await ctx.send(embed=embed)            

@setup.command()
async def category(ctx, categoryId: int = None):
    if ctx.author.guild_permissions.administrator:
        if categoryId is not None:
            set_category(ctx.guild.id, categoryId)
            category = discord.utils.get(ctx.guild.categories, id=int(get_category(ctx.guild.id)))
            
            embed = discord.Embed(title="\✔️ Category Set", description=f"Successfully set category to `{category.name}`")
            embed.set_footer(text=EMBEDFOOTER)

            await ctx.send(embed=embed) 

        else:
            prefix = get_prefix(ctx.guild.id)
            
            embed = discord.Embed(title="\❌ Invalid Usage", description=f"Try: `{prefix}setup category (id)`")
            embed.set_footer(text=EMBEDFOOTER)

            await ctx.send(embed=embed)

@setup.command()
async def prefix(ctx, customPrefix: str = None):
    if ctx.author.guild_permissions.administrator:
        if customPrefix is not None:
            set_prefix(ctx.guild.id, customPrefix)
            prefix = get_prefix(ctx.guild.id)
            
            embed = discord.Embed(title="\✔️ Prefix Set", description=f"Successfully set prefix to `{prefix}`")
            embed.set_footer(text=EMBEDFOOTER)

            await ctx.send(embed=embed)

        else:
            prefix = get_prefix(ctx.guild.id)
            
            embed = discord.Embed(title="\❌ Invalid Usage", description=f"Try: `{prefix}setup prefix (prefix)`")
            embed.set_footer(text=EMBEDFOOTER)

            await ctx.send(embed=embed)

bot.run(TOKEN)
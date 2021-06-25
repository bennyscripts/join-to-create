import discord
import asyncio
import json
import os
from discord.ext import commands

from utils import category as categories
from utils import channel as channels
from utils import prefix as prefixes
from utils import privateChannel as privateChannels

# COPYRIGHT: Arty, Benny.

CONFIG = json.load(open("config.json"))
TOKEN = CONFIG["token"]
DEFAULTPREFIX = CONFIG["default_prefix"]
INVITE = "https://discord.com/api/oauth2/authorize?client_id=838084070986350642&permissions=8&scope=bot"
EMBEDFOOTER = "Developed by Arty & Benny"
STATUSTEXT = f"{DEFAULTPREFIX}help | Arty™️"

bot = commands.Bot(command_prefix=prefixes.get2, activity=discord.Game(STATUSTEXT))
bot.remove_command("help")

@bot.event
async def on_ready():
    print("bot online")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        embed = discord.Embed(title="\❌ Error", description="That command doesn't exist.", color=discord.Color.red())
        embed.set_footer(text=EMBEDFOOTER)
        
        await ctx.send(embed=embed)

    elif isinstance(error, commands.BadArgument):
        embed = discord.Embed(title="\❌ Error", description="Missing an argument.", color=discord.Color.red())
        embed.set_footer(text=EMBEDFOOTER)
        
        await ctx.send(embed=embed)

    else:
        embed = discord.Embed(title="\❌ Error", description="There was a big error that I can't handle* \😩", color=discord.Color.red())
        embed.set_footer(text=EMBEDFOOTER)        
        
        await ctx.send(embed=embed)
        print("[ERROR]", str(error))

@bot.event
async def on_guild_join(guild):
    category = await guild.create_category(name='Private Channels')
    channel = await category.create_voice_channel("➕ New Room")
    channels.set(guild.id, channel.id)
    categories.set(guild.id, category.id)
    prefixes.set(guild.id, DEFAULTPREFIX)

@bot.event
async def on_voice_state_update(member, before, after):    
    if before.channel is None and after.channel is not None:
        if after.channel.id == int(channels.get(member.guild.id)):
            if str(member.id) not in json.load(open("data/privateChannels.json")):
                category = discord.utils.get(member.guild.categories, id=int(categories.get(member.guild.id)))
                privChannel = await category.create_voice_channel(f"{member}'s room")
                privateChannels.add(f"{member.id}", f"{privChannel.id}", False)
                await member.move_to(privChannel)     

@bot.command(aliases=["cmds", "commands"])
async def help(ctx):    
    prefix = prefixes.get(ctx.guild.id)
    helpmsg = f"""
- `{prefix}`invite : The bots invite link.
- `{prefix}`setup : Setup the bot.
- `{prefix}`vc : Voice channel commands.
"""

    embed = discord.Embed(title="\📖 Commands", description=helpmsg, color=discord.Color.blurple())
    embed.set_footer(text=EMBEDFOOTER)

    await ctx.send(embed=embed)

@bot.command()
async def invite(ctx):
    msg = f"""
Invite me with the link below!
- <{INVITE}>
    """

    embed = discord.Embed(title="\💨 Invite", description=msg, color=discord.Color.blurple())
    embed.set_footer(text=EMBEDFOOTER)

    await ctx.send(embed=embed)

@bot.group()
async def vc(ctx):
    if str(ctx.author.id) in json.load(open("data/privateChannels.json")):
        if ctx.invoked_subcommand is None:
            prefix = prefixes.get(ctx.guild.id)
            embed = discord.Embed(title="\🎙️ Voice Channel", description=f"- `{prefix}`vc me\n- `{prefix}`vc close\n- `{prefix}`vc private", color=discord.Color.blurple())
            embed.set_footer(text=EMBEDFOOTER)

            await ctx.send(embed=embed)

    else:
        embed = discord.Embed(title="\❌ Error", description="You dont own a voice channel.", color=discord.Color.red())
        embed.set_footer(text=EMBEDFOOTER)

        await ctx.send(embed=embed)

@vc.command()
async def me(ctx):
    if str(ctx.author.id) in json.load(open("data/privateChannels.json")):
        private = json.load(open("data/privateChannels.json"))[f"{ctx.author.id}"]["private"]
        channel = discord.utils.get(ctx.guild.channels, id=int(json.load(open("data/privateChannels.json"))[f"{ctx.author.id}"]["channelId"]))

        embed = discord.Embed(title="\🎙️ Your Channel", description=f"*Channel : `{channel.name}`*\n*Private : `{private}`*", color=discord.Color.blurple())
        embed.set_footer(text=EMBEDFOOTER)

        await ctx.send(embed=embed)

@vc.command()
async def close(ctx):
    if str(ctx.author.id) in json.load(open("data/privateChannels.json")):
        channel = discord.utils.get(ctx.guild.channels, id=int(json.load(open("data/privateChannels.json"))[f"{ctx.author.id}"]["channelId"]))
        await channel.delete()

        privateChannels.remove(ctx.author.id)

        embed = discord.Embed(title="\✔️ Success", description="Closed your channel successfully.", color=discord.Color.green())
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

            privateChannels.remove(ctx.author.id)
            privateChannels.add(ctx.author.id, channel.id, True)
            
            embed = discord.Embed(title="\✔️ Success", description="Your voice channel is now private.", color=discord.Color.green())
            embed.set_footer(text=EMBEDFOOTER)

            await ctx.send(embed=embed)       
        else:
            await channel.set_permissions(ctx.guild.default_role, connect=True)

            privateChannels.remove(ctx.author.id)
            privateChannels.add(ctx.author.id, channel.id, False)

            embed = discord.Embed(title="\✔️ Success", description="Your voice channel is no longer private.", color=discord.Color.green())
            embed.set_footer(text=EMBEDFOOTER)

            await ctx.send(embed=embed)

@bot.group()
async def setup(ctx):
    if ctx.author.guild_permissions.administrator:
        if ctx.invoked_subcommand is None:
            prefix = prefixes.get(ctx.guild.id)
            
            embed = discord.Embed(title="\⚙️ Setup", description=f"- `{prefix}`setup channel (id)\n- `{prefix}`setup category (id)\n- `{prefix}`setup prefix (prefix)", color=discord.Color.blurple())
            embed.set_footer(text=EMBEDFOOTER)

            await ctx.send(embed=embed)            

    else:
        embed = discord.Embed(title="\❌ Invalid Permissions", description="Contact and admin if you believe this is incorrect.", color=discord.Color.red())
        embed.set_footer(text=EMBEDFOOTER)

        await ctx.send(embed=embed)

@setup.command()
async def channel(ctx, channelId: int = None):
    if ctx.author.guild_permissions.administrator:
        if channelId is not None:
            channels.set(ctx.guild.id, channelId)
            channel = discord.utils.get(ctx.guild.voice_channels, id=int(channels.get(ctx.guild.id)))
            
            embed = discord.Embed(title="\✔️ Channel Set", description=f"Successfully set channel to `{channel.name}`", color=discord.Color.green())
            embed.set_footer(text=EMBEDFOOTER)

            await ctx.send(embed=embed)              

        else:
            prefix = prefixes.get(ctx.guild.id)
            
            embed = discord.Embed(title="\❌ Invalid Usage", description=f"Try: `{prefix}setup channel (id)`", color=discord.Color.red())
            embed.set_footer(text=EMBEDFOOTER)

            await ctx.send(embed=embed)            

@setup.command()
async def category(ctx, categoryId: int = None):
    if ctx.author.guild_permissions.administrator:
        if categoryId is not None:
            categories.set(ctx.guild.id, categoryId)
            category = discord.utils.get(ctx.guild.categories, id=int(categories.get(ctx.guild.id)))
            
            embed = discord.Embed(title="\✔️ Category Set", description=f"Successfully set category to `{category.name}`", color=discord.Color.green())
            embed.set_footer(text=EMBEDFOOTER)

            await ctx.send(embed=embed) 

        else:
            prefix = prefixes.get(ctx.guild.id)
            
            embed = discord.Embed(title="\❌ Invalid Usage", description=f"Try: `{prefix}setup category (id)`", color=discord.Color.red())
            embed.set_footer(text=EMBEDFOOTER)

            await ctx.send(embed=embed)

@setup.command()
async def prefix(ctx, customPrefix: str = None):
    if ctx.author.guild_permissions.administrator:
        if customPrefix is not None:
            prefixes.set(ctx.guild.id, customPrefix)
            prefix = prefixes.get(ctx.guild.id)
            
            embed = discord.Embed(title="\✔️ Prefix Set", description=f"Successfully set prefix to `{prefix}`", color=discord.Color.green())
            embed.set_footer(text=EMBEDFOOTER)

            await ctx.send(embed=embed)

        else:
            prefix = prefixes.get(ctx.guild.id)
            
            embed = discord.Embed(title="\❌ Invalid Usage", description=f"Try: `{prefix}setup prefix (prefix)`", color=discord.Color.red())
            embed.set_footer(text=EMBEDFOOTER)

            await ctx.send(embed=embed)

bot.run(TOKEN)
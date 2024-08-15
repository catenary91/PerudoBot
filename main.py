import discord
from discord.ext import commands

import os
from dotenv import load_dotenv

from perudo import Perudo

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='/', intents=intents)

@bot.event
async def on_ready():
    await bot.add_cog(Perudo(bot))
    print('ready')

@bot.command(name='del')
async def delete(ctx: commands.Context, n: int = 0):
    await ctx.channel.purge(limit=n+1)

@bot.command(name='sync')
async def sync(ctx: commands.Context):
    print('sync start')
    await bot.tree.sync(guild=ctx.guild)
    print('sync complete')
    

@bot.command(name='thread-test')
async def embed_test(ctx: commands.Context):
    msg = await ctx.send('test')
    await ctx.channel.create_thread(name='test thread', message=msg)

load_dotenv()
bot.run(os.environ.get('TOKEN'))
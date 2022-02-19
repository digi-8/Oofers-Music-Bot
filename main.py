import os
import keep_alive
import discord
import asyncio
import re
from discord.ext import commands
from discord.utils import get
from discord import FFmpegPCMAudio
from discord import TextChannel
from youtube_dl import YoutubeDL
from asyncio import sleep

# Version 2.0

client = commands.Bot(command_prefix='!')
queue = []

@client.command()
async def play(ctx, url):
  voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
  voice_channel = ctx.author.voice.channel

  if voice_channel is None:
    await ctx.send("Connect to a voice channel!")
  else:
    if voice and voice.is_connected():
        await voice.move_to(voice_channel)
    else:
      await voice_channel.connect()
    
    YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
    FFMPEG_OPTIONS = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
    voice = get(client.voice_clients, guild=ctx.guild)
    with YoutubeDL(YDL_OPTIONS) as ydl:
        info = ydl.extract_info(url, download=False)
        title = info.get('title', None)
    URL = info['url']   
    queue.append(URL)
    if not voice.is_playing():
      while len(queue) >= 1:
        voice.play(FFmpegPCMAudio(queue[0], **FFMPEG_OPTIONS))
        await ctx.send(f'Playing {title}')
        queue.pop(0)
        voice.is_playing()
        while voice.is_playing():
          await sleep(5)
      await sleep(60)
      await voice.disconnect()
    else:
      await ctx.send(f'Added {title} to queue')


@client.command()
async def skip(ctx):
    YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
    FFMPEG_OPTIONS = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
    voice = get(client.voice_clients, guild=ctx.guild)
    voice.stop()
    while len(queue) >= 1:
      voice.play(FFmpegPCMAudio(queue[0], **FFMPEG_OPTIONS))
      await ctx.send(f'Playing {title}')
      queue.pop(0)
      voice.is_playing()
      while voice.is_playing():
        await sleep(5)
    await sleep(60)
    await voice.disconnect()
    
@client.command()
async def stop(ctx):
    voice = get(client.voice_clients, guild=ctx.guild)

    if voice.is_playing():
        voice.stop()
        await ctx.send('Stopping...')

@client.command()
async def resume(ctx):
    voice = get(client.voice_clients, guild=ctx.guild)

    if not voice.is_playing():
        voice.resume()
        await ctx.send('Music is resuming')

@client.command()
async def pause(ctx):
    voice = get(client.voice_clients, guild=ctx.guild)

    if voice.is_playing():
        voice.pause()
        await ctx.send('Music has been paused')

@client.command(aliases=['disconnect'])
async def dc(ctx):
    voice = get(client.voice_clients, guild=ctx.guild)
    if voice.is_connected():
      await voice.disconnect()
    else:
      await voice.disconnect()

@client.command()
async def clear(ctx, amount=5):
    await ctx.channel.purge(limit=amount)

keep_alive.keep_alive()
mytoken = os.environ['token']
client.run(mytoken)

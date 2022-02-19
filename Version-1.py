import keep_alive
import discord
from discord.ext import commands
from discord.utils import get
from discord import FFmpegPCMAudio
from discord import TextChannel
from youtube_dl import YoutubeDL
from asyncio import sleep

#Version 1.0

client = commands.Bot(command_prefix='!')

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
    if not voice.is_playing():
      with YoutubeDL(YDL_OPTIONS) as ydl:
        info = ydl.extract_info(url, download=False)
        URL = info['url']
        voice.play(FFmpegPCMAudio(URL, **FFMPEG_OPTIONS))
        voice.is_playing()
        await ctx.send('Bot is playing')
        while voice.is_playing():
          await sleep(60)
          await voice.disconnect()
    else: 
      voice.stop()
      with YoutubeDL(YDL_OPTIONS) as ydl:
        info = ydl.extract_info(url, download=False)
        URL = info['url']
        voice.play(FFmpegPCMAudio(URL, **FFMPEG_OPTIONS))
        voice.is_playing()
        await ctx.send('Bot is playing')
        while voice.is_playing():
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

@client.command()
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
client.run(mytoken)

import os
import keep_alive
import discord
import re
from discord.ext import commands
from discord.utils import get
from discord import FFmpegPCMAudio
from youtube_dl import YoutubeDL
from asyncio import sleep

# Version 2.2

# Here you can change the prefix of the commands. Example: & makes the commands &play
client = commands.Bot(command_prefix='&')
# Here is the queue where all the links get added
queue = []

# Play command: This command Plays music, queues music or searches the string and queues the first result.
@client.command()
async def play(ctx, *, url):
  voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
  voice_channel = ctx.author.voice.channel
  YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
  # Check if the user is connected to a channel. If connected to a Voice channel the bot joins the channel
  if voice_channel is None:
    await ctx.send("Connect to a voice channel!")
  else:
    if voice and voice.is_connected():
      await voice.move_to(voice_channel)
    else:
      await voice_channel.connect()
      
    ytregex = '^((?:https?:)?\/\/)?((?:www|m)\.)?((?:youtube\.com|youtu.be))(\/(?:[\w\-]+\?v=|embed\/|v\/)?)([\w\-]+)(\S+)?$'

    # Check if the string is a link else it seaches the string on YT
    if re.match(ytregex, url):
      queue.append(url)   
    else:
      with YoutubeDL(YDL_OPTIONS) as ydl:
          info = ydl.extract_info(f"ytsearch:{url}", download=False)['entries'][0]
          url = info.get('webpage_url', None)
      queue.append(url)
      
    # Check if bot is playing music. If playing add the link to the queue, else play the song
    if not voice.is_playing():
      FFMPEG_OPTIONS = {
          'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
      while len(queue) >= 1:      
        with YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(queue[0], download=False)
            title = info.get('title', None)
        URL = info['url']
        voice.play(FFmpegPCMAudio(URL, **FFMPEG_OPTIONS))
        await ctx.send(f'Playing {title}')
        queue.pop(0)
        voice.is_playing()
        while voice.is_playing():
          await sleep(5)
      await sleep(60)
      await voice.disconnect()    
    else:
      with YoutubeDL(YDL_OPTIONS) as ydl:
          info = ydl.extract_info(queue[0], download=False)
          title = info.get('title', None)
      await ctx.send(f'Added {title} to queue')
      
# Skip command: Stops the current song and playes the next in queue 
@client.command()
async def skip(ctx):
    FFMPEG_OPTIONS = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
    voice = get(client.voice_clients, guild=ctx.guild)
    voice.stop()
    while len(queue) >= 1:      
      YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
      with YoutubeDL(YDL_OPTIONS) as ydl:
          info = ydl.extract_info(queue[0], download=False)
          title = info.get('title', None)
      URL = info['url']
      voice.play(FFmpegPCMAudio(URL, **FFMPEG_OPTIONS))
      await ctx.send(f'Playing {title}')
      queue.pop(0)
      voice.is_playing()
      while voice.is_playing():
        await sleep(5)
    await sleep(60)
    await voice.disconnect()    

# Stop command: Stops the current song, I think
@client.command()
async def stop(ctx):
    voice = get(client.voice_clients, guild=ctx.guild)

    if voice.is_playing():
        voice.stop()
        await ctx.send('Stopping...')

# Pauses command: Pauses the song
@client.command()
async def pause(ctx):
    voice = get(client.voice_clients, guild=ctx.guild)

    if voice.is_playing():
        voice.pause()
        await ctx.send('Music has been paused')
      
# Resume command: Resumes the song
@client.command()
async def resume(ctx):
    voice = get(client.voice_clients, guild=ctx.guild)

    if not voice.is_playing():
        voice.resume()
        await ctx.send('Music is resuming')

# Disconnect command: Disconnects the bot
@client.command(aliases=['disconnect'])
async def dc(ctx):
    voice = get(client.voice_clients, guild=ctx.guild)
    
    if voice.is_connected():
      await voice.disconnect()
      await ctx.send('Disconnected')
    else:
      await voice.disconnect()

# Clear command: Clears the 5 previous messages in the text channel
@client.command()
async def clear(ctx, amount=5):
    await ctx.channel.purge(limit=amount)

# Function to keep the bot live
keep_alive.keep_alive()

# This gets the token key, sets it as a variable
mytoken = os.environ['token']

#Here is where the bot token is set
client.run(mytoken)

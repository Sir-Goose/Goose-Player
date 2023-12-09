import asyncio

import discord
from discord.ext import commands
from discord.utils import get
import yt_dlp
import re
import json

# Get API key
with open('api_key.txt', 'r') as f:
    api_key = f.read()

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.voice_states = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Keep track of state
is_playing_or_paused = False
file_path = 'bowie.mp3'  # old
song_queue = []
skip_queue = []
skipped = [False]


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    print(bot.guilds)


@bot.command()
async def join(ctx):
    channel = ctx.author.voice.channel
    await channel.connect()


@bot.command(name='enqueue', help='Add song to queue')
async def enqueue(ctx):
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\'(),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'

    # url is provided, assume it is a playlist
    if re.search(url_pattern, ' '.join(ctx.message.content.split(' ')[1:])):
        url = ' '.join(ctx.message.content.split(' ')[1:])
        with yt_dlp.YoutubeDL({'format': 'bestaudio',
                               'extract_flat': True}) as ydl:
            info = ydl.extract_info(url, download=False)
            json_string = json.dumps(info)
            with open('data.json', 'w') as outfile:
                outfile.write(json_string)

            print(info)
            for entry in info['entries']:
                song_queue.append(entry['url'])
        print(song_queue)

    # not a url, search YouTube
    else:
        search_string = ' '.join(ctx.message.content.split(' ')[1:])
        print(search_string)
        ydl_opts = {
            'default_search': 'ytsearch',
            'format': 'bestaudio/best',  # Fetches the best audio
            'quiet': False,  # Set to False to see download progress
            'no_warnings': False,
            # 'extract_flat': True,
            'outtmpl': '%(title)s.%(ext)s'  # Sets the name of the file as the title of the video
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                # The download flag is True by default, so it will download the video
                info = ydl.extract_info(search_string, download=True)
                json_string = json.dumps(info)
                with open('data.json', 'w') as outfile:
                    outfile.write(json_string)
                audio = info['entries'][0]
                title = audio.get('title')
                ext = audio.get('ext', 'mp3')  # Default extension is mp3
                filename = f"{title}.{ext}"
                print("Downloaded:", filename)
                song_queue.append(filename)
            except Exception as e:
                print("Error:", e)


def download_audio_and_return_filename(url):
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\'(),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    if not re.search(url_pattern, url):
        return url

    # Set up the configuration for yt-dlp
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': '%(title)s.%(ext)s',
        'keepvideo': True,
        'extract_flat': True,
    }

    # Download the video
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        video_title = info_dict.get('title', None)
        file_name = f"{video_title}.mp3" if video_title else "Unknown.mp3"

    return file_name


@bot.command(name='play', help='To play song from a local file')
async def play(ctx):
    if len(ctx.message.content.split(' ')) > 1:
        await enqueue(ctx)

    if skipped[0]:
        skipped[0] = False
        for song in skip_queue:
            song_queue.append(song)

    if not song_queue:
        await ctx.send("The song queue is empty.")
        return
    try:
        server = ctx.message.guild
        voice_channel = server.voice_client
        if not voice_channel:
            await ctx.send("Bot is not connected to a voice channel.")
            return

        async with ctx.typing():
            # Call back function
            def play_next_song(error):
                if error:
                    print(f"Error playing song: {error}")
                    ctx.send(f"An error occurred: {error}")
                if song_queue:  # Check if there are more songs in the queue
                    next_song = download_audio_and_return_filename(song_queue.pop(0))  # Get the next song
                    voice_channel.play(discord.FFmpegPCMAudio(executable="ffmpeg", source=next_song),
                                       after=play_next_song)
                    asyncio.run_coroutine_threadsafe(ctx.send(f'**Now playing:** {next_song}'), bot.loop)
                else:
                    asyncio.run_coroutine_threadsafe(ctx.send('End of queue reached.'), bot.loop)

            # Play the first song with the callback
            voice_channel.play(
                discord.FFmpegPCMAudio(executable="ffmpeg",
                                       source=download_audio_and_return_filename(song_queue[0])),
                after=play_next_song)
        await ctx.send(f'**Now playing:** {song_queue[0]}')
        song_queue.pop(0)  # Remove the song that is currently playing

    except Exception as e:
        await ctx.send(f"An error occurred: {e}")


@bot.command(name='pause', help='This command pauses the song')
async def pause(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        await voice_client.pause()
    else:
        await ctx.send("The bot is not playing anything at the moment.")


@bot.command(name='resume', help='Resumes the song')
async def resume(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_paused():
        await voice_client.resume()
    else:
        await ctx.send("The bot was not playing anything before this. Use play_song command")


@bot.command(name='stop', help='Stops the song')
async def stop(ctx):
    voice_client = ctx.message.guild.voice_client
    if song_queue:
        song_queue.clear()
    if voice_client.is_playing():
        await voice_client.stop()
    else:
        await ctx.send("The bot is not playing anything at the moment.")


@bot.command(name='queue', help='Shows the current queue')
async def queue(ctx):
    if song_queue:
        # trim to 3500 characters
        song_queue_string = str(song_queue)
        if len(song_queue_string) > 3500:
            song_queue_string = song_queue_string[:3500]
        await ctx.send(f"Current queue: {song_queue_string}")
    else:
        await ctx.send("The queue is empty.")


@bot.command(name='clear', help='Clears the queue')
async def clear(ctx):
    song_queue.clear()
    await ctx.send("The queue has been cleared.")


async def skip_helper(ctx):
    pass


@bot.command(name='skip', help='Ski'
                               'ps the current song')
async def skip(ctx):
    # This is an awful hacky work around that needs to be changed at some point
    print("Skipping song")
    await ctx.send("Skipping song")
    skip_queue.clear()
    for song in song_queue:
        skip_queue.append(song)
    try:
        await stop(ctx)
    except:
        skipped.clear()
        skipped.append(True)
        for song in skip_queue:
            song_queue.append(song)
        # await play(ctx)
    # song_queue_temp = song_queue.copy()
    # print(song_queue_temp)
    # await stop(ctx)
    # for song in song_queue_temp:
    # print(song)
    # song_queue.append(song)
    # await play(ctx)


@bot.command()
async def leave(ctx):
    guild = ctx.guild
    voice_client = get(bot.voice_clients, guild=guild)
    if voice_client:
        await voice_client.disconnect()


bot.run(api_key)

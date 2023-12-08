@bot.command(name='play_song', help='To play song from a local file')
async def play(ctx):
    try:
        server = ctx.message.guild
        voice_channel = server.voice_client

        async with ctx.typing():
            voice_channel.play(discord.FFmpegPCMAudio(executable="ffmpeg", source=song_queue[0]))
        await ctx.send('**Now playing:** {}'.format(song_queue[0]))
        song_queue.pop(0)
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")
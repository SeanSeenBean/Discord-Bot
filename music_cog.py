import discord
from discord.ext import commands
from ast import alias
import numpy as np

from youtube_dl import YoutubeDL

class music_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        #all music related stuff
        self.is_playing = False
        self.is_paused = False

        #2d array containing [song, channel]
        self.music_queue = []
        self.YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
        self.FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5','options': '-vn'}

        self.vc = None

    #search for item on youtube
    def search_yt(self, item):
        with YoutubeDL(self.YDL_OPTIONS) as ydl:
            try:
                info = ydl.extract_info("ytsearch:%s" % item, download = False)['entries'][0]
            except Exception:
                return False

        return {'source': info['formats'][0]['url'], 'title': info['title']}

    def play_next(self):
        if len(self.music_queue) > 0:
            self.is_playing = True

            #get the first url
            m_url = self.music_queue[0][0]['source']

            #remove the first element as you are currently playing it
            self.music_queue.pop(0)

            self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next())
        else:
            self.is_playing = False
        
    #infinite loop checking
    async def play_music(self, ctx):
        if len(self.music_queue) > 0:
            self.is_playing = True

            m_url = self.music_queue[0][0]['source']

            #try to connect to voice if you are not already connected
            if self.vc == None or not self.vc.is_connected():
                self.vc = await self.music_queue[0][1].connect()

                #in case we fail to connect
                if  self.vc == None:
                    await ctx.send("Could not connect to the voice channel")
                    return
            else:
                await self.vc.move_to(self.music_queue[0][1])
            #remove the first element as you are currently playing it
            self.music_queue.pop(0)

            self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next())

        else:
            self.is_playing = False
            self.leave(ctx)

    @commands.command(name= "play", aliases=["p", "playing"], help = "Play a song from youtube")
    async def play(self, ctx, *args):
        query = " ".join(args)

        voice_channel = ctx.author.voice.channel
        if voice_channel is None:
            #you need to be connected so that the bot knows where to go
            await ctx.send("Connect to a voice channel first!")
        elif self.is_paused:
            self.vc.resume()
        else:
            song = self.search_yt(query)
            if type(song) == type(True):
                await ctx.send("Failed to download song. Incorrect search format, try a differnt search term")
            else:
                await ctx.send("Song added to queue")
                self.music_queue.append([song, voice_channel])

                if self.is_playing == False:
                    await self.play_music(ctx)

    @commands.command(name='pause', help='Pauses current song')
    async def pause(self, ctx, *args):
        if self.is_playing:
            self.is_playing = False
            self.is_paused = True
            self.vc.pause()
        elif self.is_paused:
            self.vc.resume()
    
    @commands.command(name='resume', aliases=['r'], help='Resumes playing the current song')
    async def resume(self, ctx, *args):
        if self.is_paused:
            self.is_playing = True
            self.is_paused = False
            self.vc.resume()
    
    
    @commands.command(name = 'skip', aliases=['s'], help = 'Skips the current song')
    async def skip(self, ctx, *args):
        if self.vc != None and self.vc:
            self.vc.stop()
            await self.play_music(ctx)

    
    @commands.command(name='queue', aliases=['q', 'que'], help='Displays songs currently in queue')
    async def queue(self, ctx):
        retval= ''
        for i in range(0, len(self.music_queue)):
            #display a max of 10 songs in the queue
            if i > 10: break
            retval += self.music_queue[i][0]['title'] + '\n'
        
        if retval != '':
            await ctx.send(retval)
        else:
            await ctx.send("No music in the queue.")


    @commands.command(name='shuffle', alias=['random'], help='Shuffles queue into a random order')
    async def shuffle(self, ctx):
        np.random.shuffle(self.music_queue)
        #debug line to make sure shuffle is working, can also be enabled to give shuffled
        #queue if desired
        # await self.queue(ctx)


        
    @commands.command(name='clear', aliases=['c', 'bin'], help='Stops the current song and clears the queue')
    async def clear(self, ctx):
        if self.vc != None and self.is_playing:
            self.vc.stop()
        self.music_queue = []
        await ctx.send('Music queue cleared')
    
    @commands.command(name='leave', aliases=['disconnect', 'l', 'd'], help='Kick the bot from the voice channel')
    async def leave(self, ctx):
        self.is_playing = False
        self.is_paused = False
        await self.vc.disconnect()
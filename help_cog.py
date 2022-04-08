import discord
from discord.ext import commands

class help_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.help_message = """
```
General commands:
/help - display all the available commands
/p <search> or /play <search> - finds the song on youtube and plays it in your current channel. Will resume playing the current song if it was paused
/q or /queue - displays the current music queue
/shuffle or /random - Shuffles current music queue into a random order
/skip - skips the current song being played
/clear - Stops the music and clears the queue
/leave - Disconnect the bot from the voice channel
/pause - Pauses the current song being played or resumes if already paused
/resume - Resumes playing the current song

```
"""
        self.text_channel_list = []
    
    #some debug info so that we know the bot started
    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            for channel in guild.text_channels:
                #debugging line for seeing channel names
                # print(channel.name)
                if channel.name == 'general':
                    await channel.send('Nice to meet you comrades, I am Botsky')
                    await channel.send(self.help_message)
    #this logic could be cleaned up, does what it needs to though        
     #   await self.send_to_all(self.help_message)

    @commands.command(name='help', help='Displays all the avaiable commands')
    async def help(self, ctx):
        await ctx.send(self.help_message)

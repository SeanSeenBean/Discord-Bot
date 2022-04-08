#import dependencies
import discord
from discord.ext import commands
import os
from help_cog import help_cog
from music_cog import music_cog


#import bot token
from apikeys import *

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix='/')

#remove the default help command so that we can write out own
bot.remove_command('help')

#register the class with the bot
bot.add_cog(help_cog(bot))
bot.add_cog(music_cog(bot))

print("Botksy is active Comrade")
print('------------------------------')
bot.run(BOTSKY_TOKEN)




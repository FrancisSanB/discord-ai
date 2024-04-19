import discord
from discord.ext import commands

bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
    print("The bot is ready!")

@bot.command()
async def hello(ctx):
    await ctx.send("Hello!")

bot.run('MTIwMzA4ODczNzUxMzUwNDgzOA.G9u9qg.fScWy0b8GSqvZWNaGO3j3WZCTzMKj0fLFNfLBA')  # Don't reveal your bot token, regenerate it asap if you do
import os

from dotenv import load_dotenv
from discord.ext import commands


load_dotenv()
token = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='!')


@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')


@bot.command(name="add")
async def add(context):
    await context.send("Add functionality coming soon!")


@bot.command(name="list")
async def list(context):
    await context.send("List functionality coming soon!")


bot.run(token)

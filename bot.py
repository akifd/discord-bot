import os
import sqlite3

from dotenv import load_dotenv
from discord.ext import commands


load_dotenv()
token = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='!')


def create_connection():
    return sqlite3.connect("sqlite.db")


@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')


@bot.command(name="add")
async def add(context, timestamp):
    connection = create_connection()

    with connection:
        cursor = connection.cursor()
        cursor.execute("INSERT INTO event (timestamp) VALUES (?)", (timestamp,))
        event_id = cursor.lastrowid

    message = f"Added event #{event_id} on {timestamp}."

    print(message)
    await context.send(message)


@bot.command(name="list")
async def list(context):
    await context.send("List functionality coming soon!")


bot.run(token)

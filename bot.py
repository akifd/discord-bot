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
async def add(context, *timestamp):
    connection = create_connection()
    timestamp = " ".join(timestamp)

    with connection:
        cursor = connection.cursor()

        cursor.execute(
            "INSERT INTO event (id, timestamp) VALUES (?, ?)",
            (None, timestamp),
        )
        event_id = cursor.lastrowid

        cursor.execute(
            "INSERT INTO participant (id, event_id, name) VALUES (?, ?, ?)",
            (None, event_id, context.author.name),
        )

    message = f"Added event #{event_id} on {timestamp}."

    print(message)
    await context.send(message)


@bot.command(name="list")
async def list(context):
    connection = create_connection()

    with connection:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM event")
        rows = cursor.fetchall()

    messages = []
    for row in rows:
        messages.append(f"#{row[0]} {row[1]} [1/5]")

    message = "\n".join(messages)

    if not message:
        message = "No active events."

    print(message)
    await context.send(message)


bot.run(token)

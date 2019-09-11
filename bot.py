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
        event_rows = cursor.fetchall()

    messages = []
    for event in event_rows:
        with connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM participant WHERE event_id = ?", (event[0],))
            participant_rows = cursor.fetchall()

        messages.append(
            f"#{event[0]} {event[1]} [{len(participant_rows)}/5]\n" +
            "\n".join(["- {}".format(participant[2]) for participant in participant_rows])
        )

    message = "Listing active events:\n" + "\n\n".join(messages)

    if not message:
        message = "No active events."

    print(message)
    await context.send(message)


@bot.command(name="accept")
async def accept(context, event_id):
    if not event_id.isnumeric():
        message = "Please give ID as number only."
        print(message)
        await context.send(message)
        return

    connection = create_connection()

    with connection:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM participant WHERE event_id = ? AND name = ?",
                       (event_id, context.author.name))
        participant_rows = cursor.fetchall()
        if len(participant_rows) > 0:
            message = "You have already accepted the event."
            print(message)
            await context.send(message)
            return

        cursor.execute("INSERT INTO participant (event_id, name) VALUES (?, ?)",
                       (event_id, context.author.name))

    message = f"{context.author.name} added to event #{event_id}"
    print(message)
    await context.send(message)


bot.run(token)

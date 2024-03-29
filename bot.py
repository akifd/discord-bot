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


@bot.command(name="create", help="Create new event with given name.")
async def create(context, *timestamp):
    timestamp = " ".join(timestamp)

    if len(timestamp) < 8:
        await context.send("Give the event a longer name.")
        return

    connection = create_connection()

    with connection:
        cursor = connection.cursor()
        cursor.execute("INSERT INTO event (timestamp) VALUES (?)", (timestamp,))
        event_id = cursor.lastrowid

        cursor.execute("INSERT INTO participant (event_id, name) VALUES (?, ?)",
                       (event_id, context.author.name))

    await context.send(f"Added event #{event_id} on {timestamp}.")


@bot.command(name="delete", help="Delete event with given ID.")
async def delete(context, event_id):
    if not event_id.isnumeric():
        await context.send("Please give ID as a number.")
        return

    connection = create_connection()

    with connection:
        cursor = connection.cursor()
        cursor.execute("PRAGMA foreign_keys = ON")
        cursor.execute("DELETE FROM event WHERE id = (?)", (event_id,))

    await context.send(f"Deleted event #{event_id}.")


@bot.command(name="list", help="List active events.")
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

    await context.send(message)


@bot.command(name="accept", help="Accept event with given ID.")
async def accept(context, event_id):
    if not event_id.isnumeric():
        await context.send("Please give ID as a number.")
        return

    connection = create_connection()

    with connection:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM participant WHERE event_id = ? AND name = ?",
                       (event_id, context.author.name))
        participant_rows = cursor.fetchall()
        if len(participant_rows) > 0:
            await context.send("You have already accepted the event.")
            return

        cursor.execute("INSERT INTO participant (event_id, name) VALUES (?, ?)",
                       (event_id, context.author.name))

    await context.send(f"{context.author.name} added to event #{event_id}")


@bot.command(name="cancel", help="Cancel accepting event with given ID.")
async def cancel(context, event_id):
    if not event_id.isnumeric():
        await context.send("Please give ID as a number.")
        return

    connection = create_connection()

    with connection:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM participant WHERE event_id = ? AND name = ?",
                       (event_id, context.author.name))

    await context.send(f"{context.author.name} removed from event #{event_id}")

    with connection:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM participant WHERE event_id = ?", (event_id,))
        participant_rows = cursor.fetchall()

        if len(participant_rows) == 0:
            cursor.execute("DELETE FROM event WHERE id = ?", (event_id))
            await context.send(
                f"Event {event_id} deleted, because all participants parted."
            )


bot.run(token)

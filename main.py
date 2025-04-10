import sys

import discord

from actions import process_csv_add, process_csv_remove, process_moodle, process_stats
from config import TOKEN

# Check command-line arguments for operation mode.
if len(sys.argv) < 2 or sys.argv[1] not in ["--add", "--remove", "--stats", "--moodle"]:
    print("Usage: python3 main.py --add, --remove, --stats, or --moodle")
    sys.exit(1)
OPERATION_MODE = sys.argv[1]

# Set up the Discord client with the required intents.
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True  # Needed for reading message content
client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    if OPERATION_MODE == "--add":
        await process_csv_add(client)
    elif OPERATION_MODE == "--remove":
        await process_csv_remove(client)
    elif OPERATION_MODE == "--stats":
        await process_stats(client)
    elif OPERATION_MODE == "--moodle":
        await process_moodle(client)
    await client.close()


assert TOKEN is not None, "Please set the TOKEN in config.py"
client.run(TOKEN)

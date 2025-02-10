import csv
import os
import sys
from datetime import datetime

import discord
from discord.utils import get
from dotenv import load_dotenv

# Check command-line arguments for operation mode.
if len(sys.argv) < 2 or sys.argv[1] not in ["--add", "--remove"]:
    print("Usage: python3 your_bot_file.py --add or --remove")
    sys.exit(1)
OPERATION_MODE = sys.argv[1]

# Load environment variables from the .env file.
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))
CSV_FILE = os.getenv("CSV_FILE")  # e.g., "data.csv"

# Set up the Discord client with the required intents.
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = (
    True  # Needed for reading message content in newer discord.py versions
)
client = discord.Client(intents=intents)


async def process_csv_add():
    """
    Reads the CSV and for each record:
      - Parses the date (e.g., "Monday, April 7, 2025")
      - Creates (or reuses) a category named "{Month} Presentations"
      - If the "Discord Channel Name" is provided:
          - If the channel doesn't exist, creates it, sends a message, and pins it.
          - If the channel exists, checks for a pinned message from the bot:
              - If no such message exists or its content differs from the expected content,
                deletes the old message (if any) and sends & pins the new message.
              - Otherwise, it skips updating that channel.
    The message now also includes the presentation date with a calendar emoji.
    """
    guild = client.get_guild(GUILD_ID)
    if guild is None:
        print("Guild not found!")
        return

    # Dictionary to cache category objects.
    categories = {}

    try:
        with open(CSV_FILE, newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for record in reader:
                # Get and parse the date.
                date_str = record.get("Date", "").strip()
                if not date_str:
                    continue  # Skip rows without a date.

                try:
                    dt = datetime.strptime(date_str, "%A, %B %d, %Y")
                except Exception as e:
                    print(f"Error parsing date '{date_str}': {e}")
                    continue

                # Build the category name (e.g., "April Presentations").
                month_name = dt.strftime("%B")
                category_name = f"{month_name} Presentations"

                # Retrieve or create the category.
                if category_name in categories:
                    category = categories[category_name]
                else:
                    category = get(guild.categories, name=category_name)
                    if category is None:
                        print(f"Creating category: {category_name}")
                        category = await guild.create_category(category_name)
                    categories[category_name] = category

                # Process channel creation/update if a "Discord Channel Name" is provided.
                discord_channel_name = record.get("Discord Channel Name", "").strip()
                if discord_channel_name:
                    channel_id = record.get("ID", "").strip()
                    if not channel_id:
                        print(
                            "No ID provided for this record; skipping channel creation/update."
                        )
                        continue

                    # Build the channel name (e.g., "p1-fedhyper-a-universal-and-robust").
                    channel_name = f"p{channel_id}-{discord_channel_name}"

                    # Build the expected message content using the new format.
                    paper_title = record.get("Paper Title", "No Title").strip()
                    paper_link = record.get("Paper Link", "No Link").strip()
                    presenter = record.get("Presenters", "N/A").strip()
                    topic_category = record.get("Topic", "N/A").strip()
                    # Include the presentation date with a calendar emoji.
                    presentation_date = dt.strftime("%A, %B %d, %Y")
                    new_message_content = (
                        f"**📜 Paper being presented**: {paper_title}\n"
                        f"**🌐 Paper Link**: {paper_link}\n"
                        f"**📅 Presentation Date**: {presentation_date}\n"
                        f"**🗣️ Presenter(s)**: {presenter}\n"
                        f"**🗃️ Topic Category**: {topic_category}"
                    )

                    # Try to get the existing channel in the category.
                    existing_channel = get(category.channels, name=channel_name)
                    if existing_channel is None:
                        # Create the new channel.
                        print(
                            f"Creating text channel: {channel_name} in category {category_name}"
                        )
                        channel = await guild.create_text_channel(
                            channel_name, category=category
                        )
                        try:
                            msg = await channel.send(new_message_content)
                            await msg.pin()
                            print(
                                f"Sent and pinned message in channel '{channel_name}'."
                            )
                        except Exception as e:
                            print(
                                f"Error sending or pinning message in channel '{channel_name}': {e}"
                            )
                    else:
                        # Channel exists. Check for a pinned message by the bot.
                        channel = existing_channel
                        try:
                            pinned_messages = await channel.pins()
                        except Exception as e:
                            print(
                                f"Error retrieving pinned messages in channel '{channel_name}': {e}"
                            )
                            pinned_messages = []

                        target_message = None
                        for m in pinned_messages:
                            if m.author.id == client.user.id:
                                target_message = m
                                break

                        if target_message is None:
                            # No message was pinned by the bot. Send the new message.
                            try:
                                msg = await channel.send(new_message_content)
                                await msg.pin()
                                print(
                                    f"Sent and pinned new message in channel '{channel_name}'."
                                )
                            except Exception as e:
                                print(
                                    f"Error sending or pinning message in channel '{channel_name}': {e}"
                                )
                        elif target_message.content != new_message_content:
                            # The existing pinned message differs from the expected content.
                            try:
                                await target_message.delete()
                                msg = await channel.send(new_message_content)
                                await msg.pin()
                                print(
                                    f"Updated pinned message in channel '{channel_name}'."
                                )
                            except Exception as e:
                                print(
                                    f"Error updating message in channel '{channel_name}': {e}"
                                )
                        else:
                            print(
                                f"Channel '{channel_name}' already exists with the correct message. Skipping."
                            )
    except FileNotFoundError:
        print(
            f"CSV file '{CSV_FILE}' not found. Please check the CSV_FILE environment variable."
        )


async def process_csv_remove():
    """
    Reads the CSV and for each record:
      - Parses the date and builds the corresponding category name.
      - If the channel specified by "p{ID}-{Discord Channel Name}" exists in that category,
        removes the channel.
    After processing all records, checks each affected category; if it is empty, removes the category.
    """
    guild = client.get_guild(GUILD_ID)
    if guild is None:
        print("Guild not found!")
        return

    # Dictionary to keep track of categories encountered.
    categories = {}

    try:
        with open(CSV_FILE, newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for record in reader:
                date_str = record.get("Date", "").strip()
                if not date_str:
                    continue

                try:
                    dt = datetime.strptime(date_str, "%A, %B %d, %Y")
                except Exception as e:
                    print(f"Error parsing date '{date_str}': {e}")
                    continue

                month_name = dt.strftime("%B")
                category_name = f"{month_name} Presentations"

                # Get the category from the guild if it exists.
                category = get(guild.categories, name=category_name)
                if category is None:
                    print(
                        f"Category '{category_name}' does not exist. Skipping removal for this record."
                    )
                    continue

                # Cache the category for later empty-check.
                categories[category_name] = category

                # Process channel removal if "Discord Channel Name" is provided.
                discord_channel_name = record.get("Discord Channel Name", "").strip()
                if discord_channel_name:
                    channel_id = record.get("ID", "").strip()
                    if not channel_id:
                        print(
                            "No ID provided for this record; skipping channel removal."
                        )
                        continue

                    channel_name = f"p{channel_id}-{discord_channel_name}"
                    channel = get(category.channels, name=channel_name)
                    if channel is not None:
                        try:
                            print(
                                f"Removing channel '{channel_name}' from category '{category_name}'."
                            )
                            await channel.delete()
                        except Exception as e:
                            print(f"Error removing channel '{channel_name}': {e}")
                    else:
                        print(
                            f"Channel '{channel_name}' does not exist in category '{category_name}'. Skipping."
                        )
    except FileNotFoundError:
        print(
            f"CSV file '{CSV_FILE}' not found. Please check the CSV_FILE environment variable."
        )

    # After channel removals, remove any category that is now empty.
    for category_name, category in categories.items():
        if len(category.channels) == 0:
            try:
                print(f"Category '{category_name}' is empty. Removing category.")
                await category.delete()
            except Exception as e:
                print(f"Error removing category '{category_name}': {e}")


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    if OPERATION_MODE == "--add":
        await process_csv_add()
    elif OPERATION_MODE == "--remove":
        await process_csv_remove()
    # Shut down the bot once processing is complete.
    await client.close()


client.run(TOKEN)

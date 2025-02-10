import csv
from datetime import datetime

from discord.utils import get

from config import CSV_FILE, GUILD_ID


async def process_csv_add(client):
    """
    Reads the CSV file and for each record:
      - Parses the date (e.g., "Monday, April 7, 2025")
      - Creates or reuses a category named "{Month} Presentations"
      - If "Discord Channel Name" is provided:
          - Creates the channel if it doesn't exist, or
          - If the channel exists, checks for a pinned message from the bot.
            If no message is pinned or if the pinned message's content differs from
            the expected content, updates it.
      - The message includes the presentation date (with a calendar emoji) along with other details.
    """
    guild = client.get_guild(GUILD_ID)
    if guild is None:
        print("Guild not found!")
        return

    categories = {}  # Cache for category objects

    try:
        with open(CSV_FILE, newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for record in reader:
                date_str = record.get("Date", "").strip()
                if not date_str:
                    continue  # Skip if no date

                try:
                    dt = datetime.strptime(date_str, "%A, %B %d, %Y")
                except Exception as e:
                    print(f"Error parsing date '{date_str}': {e}")
                    continue

                month_name = dt.strftime("%B")
                category_name = f"{month_name} Presentations"

                # Retrieve or create the category
                if category_name in categories:
                    category = categories[category_name]
                else:
                    category = get(guild.categories, name=category_name)
                    if category is None:
                        print(f"Creating category: {category_name}")
                        category = await guild.create_category(category_name)
                    categories[category_name] = category

                discord_channel_name = record.get("Discord Channel Name", "").strip()
                if discord_channel_name:
                    channel_id = record.get("ID", "").strip()
                    if not channel_id:
                        print("No ID provided; skipping record.")
                        continue

                    channel_name = f"p{channel_id}-{discord_channel_name}"

                    paper_title = record.get("Paper Title", "No Title").strip()
                    paper_link = record.get("Paper Link", "No Link").strip()
                    presenter = record.get("Presenters", "N/A").strip()
                    topic_category = record.get("Topic", "N/A").strip()
                    presentation_date = dt.strftime("%A, %B %d, %Y")
                    new_message_content = (
                        f"**📜 Paper being presented**: {paper_title}\n"
                        f"**🌐 Paper Link**: {paper_link}\n"
                        f"**📅 Presentation Date**: {presentation_date}\n"
                        f"**🗣️ Presenter(s)**: {presenter}\n"
                        f"**🗃️ Topic Category**: {topic_category}"
                    )

                    existing_channel = get(category.channels, name=channel_name)
                    if existing_channel is None:
                        print(f"Creating channel: {channel_name} in {category_name}")
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
                            print(f"Error in channel '{channel_name}': {e}")
                    else:
                        channel = existing_channel
                        try:
                            pinned_messages = await channel.pins()
                        except Exception as e:
                            print(f"Error retrieving pins in '{channel_name}': {e}")
                            pinned_messages = []

                        target_message = None
                        for m in pinned_messages:
                            if m.author.id == client.user.id:
                                target_message = m
                                break

                        if target_message is None:
                            try:
                                msg = await channel.send(new_message_content)
                                await msg.pin()
                                print(
                                    f"Sent and pinned new message in '{channel_name}'."
                                )
                            except Exception as e:
                                print(f"Error in '{channel_name}': {e}")
                        elif target_message.content != new_message_content:
                            try:
                                await target_message.delete()
                                msg = await channel.send(new_message_content)
                                await msg.pin()
                                print(f"Updated pinned message in '{channel_name}'.")
                            except Exception as e:
                                print(
                                    f"Error updating message in '{channel_name}': {e}"
                                )
                        else:
                            print(f"Channel '{channel_name}' is up-to-date. Skipping.")
    except FileNotFoundError:
        print(f"CSV file '{CSV_FILE}' not found.")


async def process_csv_remove(client):
    """
    Reads the CSV file and for each record:
      - Parses the date and determines the category.
      - If the channel "p{ID}-{Discord Channel Name}" exists, removes it.
    Then, removes any empty categories.
    """
    guild = client.get_guild(GUILD_ID)
    if guild is None:
        print("Guild not found!")
        return

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
                category = get(guild.categories, name=category_name)
                if category is None:
                    print(f"Category '{category_name}' not found; skipping record.")
                    continue
                categories[category_name] = category

                discord_channel_name = record.get("Discord Channel Name", "").strip()
                if discord_channel_name:
                    channel_id = record.get("ID", "").strip()
                    if not channel_id:
                        print("No ID provided; skipping record.")
                        continue

                    channel_name = f"p{channel_id}-{discord_channel_name}"
                    channel = get(category.channels, name=channel_name)
                    if channel is not None:
                        try:
                            print(
                                f"Removing channel '{channel_name}' from '{category_name}'."
                            )
                            await channel.delete()
                        except Exception as e:
                            print(f"Error removing channel '{channel_name}': {e}")
                    else:
                        print(
                            f"Channel '{channel_name}' not found in '{category_name}'."
                        )
    except FileNotFoundError:
        print(f"CSV file '{CSV_FILE}' not found.")

    # Remove empty categories
    for category_name, category in categories.items():
        if len(category.channels) == 0:
            try:
                print(f"Removing empty category '{category_name}'.")
                await category.delete()
            except Exception as e:
                print(f"Error removing category '{category_name}': {e}")
                await category.delete()
            except Exception as e:
                print(f"Error removing category '{category_name}': {e}")

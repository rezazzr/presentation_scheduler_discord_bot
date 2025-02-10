import os

from dotenv import load_dotenv

load_dotenv()  # Load variables from the .env file

TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))  # type: ignore
CSV_FILE = os.getenv("CSV_FILE")  # e.g., "data.csv"

assert TOKEN is not None, "DISCORD_TOKEN environment variable is required."
assert GUILD_ID is not None, "GUILD_ID environment variable is required."
assert CSV_FILE is not None, "CSV_FILE environment variable is required."

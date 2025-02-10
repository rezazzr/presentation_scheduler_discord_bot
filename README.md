# Presentation Scheduler Discord Bot

A Discord bot that automates the process of managing presentation channels on your Discord server. The bot reads a CSV file containing details about upcoming presentations and then either creates or removes text channels based on that data.

## Features

- **Automated Channel Management:** Creates categories (by month) and text channels for each presentation.
- **Formatted Presentation Details:** Sends and pins a message with details (paper title, link, presentation date, presenters, and topic) in each channel.
- **Update and Removal:** Updates pinned messages if changes are detected and removes channels (and empty categories) when needed.
- **CSV Driven:** Uses a CSV file to manage presentations, making it easy to update schedules.

## Prerequisites

- **Python 3.10 or newer**  
- **Poetry:** A dependency management and packaging tool for Python.  
  [Installation instructions here](https://python-poetry.org/docs/#installation)
- **Discord Bot Token:** Create a bot via the [Discord Developer Portal](https://discord.com/developers/applications) and obtain your token.
- **Discord Server (Guild):** You must have a Discord server where the bot has permissions to create channels and categories.
- **CSV File:** A CSV file with the presentation schedule.

## Getting Started

Follow these steps to set up and run the bot.

### 1. Clone the Repository

Clone the repository to your local machine using Git:

```bash
git clone https://github.com/yourusername/presentation-scheduler-discord-bot.git
cd presentation-scheduler-discord-bot
```

### 2. Install Dependencies with Poetry

If you don't have Poetry installed, please install it first by following [Poetry’s installation guide](https://python-poetry.org/docs/#installation).

Then, install the project dependencies:

```bash
poetry install
```

### 3. Configure Environment Variables

Create a `.env` file in the root directory of the project. This file will store your sensitive credentials and file paths. Open your favorite text editor and add the following lines:

```dotenv
DISCORD_TOKEN=your_discord_bot_token_here
GUILD_ID=your_discord_server_id_here
CSV_FILE=path/to/your/presentation_schedule.csv
```

- **DISCORD_TOKEN:** Replace `your_discord_bot_token_here` with the token you obtained from the Discord Developer Portal.
- **GUILD_ID:** Replace `your_discord_server_id_here` with the numerical ID of your Discord server.
- **CSV_FILE:** Provide the path to your CSV file that contains the presentation schedule.

### 4. Prepare Your CSV File

Ensure that your CSV file is formatted correctly and encoded in UTF-8. It should include the following columns:

- **Date:** The presentation date in the format `Monday, April 7, 2025`.
- **ID:** A unique identifier for the presentation.
- **Discord Channel Name:** The base name for the Discord channel (the bot will prefix this with `p{ID}-`).
- **Paper Title:** The title of the paper being presented.
- **Paper Link:** A URL linking to the paper.
- **Presenters:** The name(s) of the presenter(s).
- **Topic:** The topic or category of the presentation.

### 5. Running the Bot

The bot supports two operation modes: **add** and **remove**. You choose the mode by passing the appropriate command-line argument.

#### Adding Channels

To create or update categories and channels as per your CSV schedule, run:

```bash
poetry run python main.py --add
```

The bot will:
- Read the CSV file.
- Create a category for each month (if it doesn't exist).
- Create a text channel for each presentation where a channel name is provided.
- Send and pin a formatted message in each channel containing the presentation details.

#### Removing Channels

To remove channels and delete any empty categories, run:

```bash
poetry run python main.py --remove
```

The bot will:
- Read the CSV file.
- Remove the text channels corresponding to each presentation.
- Delete any categories that become empty after the channel removals.

### 6. Troubleshooting

- **Guild Not Found:**  
  Verify that the `GUILD_ID` in your `.env` file is correct and that the bot has access to the Discord server.

- **CSV File Not Found:**  
  Double-check the file path provided in the `CSV_FILE` variable in your `.env` file.

- **Bot Permissions:**  
  Ensure the bot has the following permissions on your Discord server:
  - Manage Channels
  - Send Messages
  - Pin Messages

- **Date Parsing Errors:**  
  Make sure that the dates in your CSV file strictly follow the format: `Monday, April 7, 2025`.

## Additional Notes

- The bot will automatically shut down after completing its task.
- Check the console output for detailed messages and error information during execution.
- For any issues or improvements, feel free to open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

For questions or support, please contact the author at [rezazzr@hotmail.com](mailto:rezazzr@hotmail.com).

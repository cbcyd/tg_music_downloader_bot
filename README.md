# Telegram Music Downloader Bot

This project is a Telegram bot for downloading music from Qobuz and Deezer.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

- Python 3.6 or higher
- A Telegram account
- Qobuz or Deezer account

### Installing

1. Clone the repository
```git clone https://github.com/yourusername/tg_music_downloader_bot.git```

2. Navigate to the project directory
```cd tg_music_downloader_bot```

3. Install the required Python packages
```pip install -r requirements.txt```

### Configuration

- Fill in config.ini your Telegram bot token, Qobuz email or user id, password or token and Deezer ARL.

### Running the bot

Run the bot using the following command: 
```python bot.py```

## Built With

- [Python Telegram Bot](https://github.com/python-telegram-bot/python-telegram-bot) - The framework used
- [streamrip](https://github.com/nathom/streamrip) - Used to download music from Qobuz and Deezer

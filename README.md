# Beatmap Downloader

This Python script downloads beatmaps for a given user from the osu! game. It uses osu!'s fetch requests to download the beatmaps based on their play counts and saves them to a specified directory. The script leverages concurrent downloads for efficiency.

## Features

- **User Identification**: Handles both osu! user IDs and usernames. If a username is provided, it automatically converts it to the corresponding user ID.
- **Beatmap Fetching**: Retrieves a list of the most played beatmaps for the user.
- **Concurrent Downloads**: Downloads beatmaps using multiple threads to speed up the process.
- **Multiple Sources**: Downloads beatmaps from various mirrors to ensure availability.

## Installation

To get started, clone this repository and install the necessary Python packages.

```bash
git clone https://github.com/crmulent/osu-beatmap-downloader.git
cd osu-beatmap-downloader
pip install -r requirements.txt
```

## Usage

```bash
python main.py
```

# Kijiji Image Scraper & Matcher

This project scrapes Kijiji listings, downloads images, and matches them based on specified criteria. It includes optional notifications via email and Discord.

## Project Structure
...

## Setup

Install dependencies:

pip install -r requirements.txt

## Usage

Run the main script:

python main.py


## Notes

- Configure `config.py` with API keys, thresholds, and other settings.
- Cached Kijiji search results are stored in `data/cache/`.
- Processed listings are tracked in `storage/checked.json`.
- Matches are saved in `storage/matches.json`.
- Notifications work via `notify/discord.py` and `notify/email.py`.

## To-Do

- Add unit tests
- Improve matching accuracy
- Add CLI arguments
- Dockerize the app

## License

MIT License

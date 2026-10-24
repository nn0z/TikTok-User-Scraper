# TikTok-User-Scraper

A simple Python tool that searches TikTok for users by keyword and extracts their public information such as username, display name, followers count, likes count, and profile URL.

The tool uses `undetected-chromedriver` to bypass TikTok's bot detection and scrolls automatically to load more results.

---

## Features

- Search TikTok users by any keyword
- Extract:
  - Display name
  - Username
  - Followers count
  - Likes count
  - Profile URL
- Auto-scroll to load more results (human-like scrolling)
- Saves only usernames to a `.txt` file (one per line)
- Headless mode enabled by default
- Handles repeated searches by creating numbered files:
  - `Example.txt`
  - `Example(2).txt`
  - `Example(3).txt`
- Output folder is created automatically

---

## Requirements

- Python 3.8 or higher
- Google Chrome installed
- Internet connection

---

## ⚠️ Disclaimer

This tool is provided for educational and research purposes only. Scraping data from TikTok may violate their Terms of Service. The developer assumes no liability for any misuse or consequences resulting from the use of this tool. Use it responsibly and at your own risk.

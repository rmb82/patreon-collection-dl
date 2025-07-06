# Patreon Collection Downloader (yt-dlp Helper)

This script lets you **automatically download all videos (or media) from a Patreon collection page**, even when the page uses a "Load more" (or "Charger plus", etc.) button to display all posts.

It combines [yt-dlp](https://github.com/yt-dlp/yt-dlp) for downloads, [Playwright](https://playwright.dev/python/) for browser automation, and [browser-cookie3](https://github.com/borisbabic/browser_cookie3) for Chrome session cookies.

---

## ✨ Features

- Opens your Patreon collection with your **Chrome session cookies**
- **Clicks all "Load more" (or equivalent) buttons** automatically until all posts are visible
- **Extracts all post links** and downloads them with `yt-dlp`
- Multi-language: you can **specify the button text** to search for (default: `"charger plus"`)

---

## 🛠️ Requirements

- Python 3.8+
- Google Chrome (for cookies)

Install dependencies:
```bash
pip install playwright browser-cookie3
playwright install

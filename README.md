If you want to download all videos from a Patreon **collection page** (e.g. https://www.patreon.com/collection/...), here's a working workaround using Playwright + browser cookies.

This script:
- Opens the collection page with your **Chrome session cookies**
- Scrolls down to load all posts
- Extracts post URLs
- Downloads each video using yt-dlp

### 🛠 Requirements

```bash
pip install yt-dlp playwright browser-cookie3
playwright install
```

#!/usr/bin/env python3

import sys
import re
import subprocess
import time
from playwright.sync_api import sync_playwright
import browser_cookie3

#YT_DLP_CMD = "yt-dlp --cookies-from-browser chrome --impersonate chrome"
YT_DLP_CMD = "yt-dlp --cookies-from-browser chrome --impersonate chrome --no-playlist --no-write-info-json --no-write-comments --no-write-subs"

def extract_cookies_for_playwright():
    cj = browser_cookie3.chrome(domain_name="patreon.com")
    cookies = []
    for c in cj:
        if "patreon.com" in c.domain:
            cookies.append({
                "name": c.name,
                "value": c.value,
                "domain": c.domain,
                "path": c.path,
                "httpOnly": bool(c._rest.get("HttpOnly", False)),
                "secure": bool(c.secure),
                "sameSite": "Lax"
            })
    return cookies

def scroll_and_extract_links(collection_url):
    cookies = extract_cookies_for_playwright()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # headless=True si tu veux en fond
        context = browser.new_context()
        context.add_cookies(cookies)
        page = context.new_page()
        page.goto(collection_url)

        print("Scrolling pour charger les posts...")
        previous_height = 0
        same_height_count = 0

        for _ in range(20):  # max 20 scrolls
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(2)
            current_height = page.evaluate("document.body.scrollHeight")
            if current_height == previous_height:
                same_height_count += 1
                if same_height_count >= 3:
                    break
            else:
                same_height_count = 0
                previous_height = current_height

        print("Extraction des liens...")
        content = page.content()
        browser.close()

        # Récupère tous les liens de posts (filtrés)
        post_links = set(re.findall(r'https://www\.patreon\.com/posts/\d+', content))
        return list(post_links)

def download_with_ytdlp(post_url):
    cmd = f"{YT_DLP_CMD} \"{post_url}\""
    print(f"==> Téléchargement : {post_url}")
    subprocess.run(cmd, shell=True)

def main():
    if len(sys.argv) != 2:
        print("Usage : python3 get_posts_links.py <url_de_collection>")
        sys.exit(1)

    collection_url = sys.argv[1]
    if "patreon.com/collection/" not in collection_url:
        print("Erreur : l'URL fournie ne semble pas être une collection Patreon.")
        sys.exit(2)

    post_links = scroll_and_extract_links(collection_url)

    if not post_links:
        print("Aucun lien de post trouvé.")
        sys.exit(0)

    print(f"{len(post_links)} post(s) trouvé(s) dans la collection.")
    for url in post_links:
        download_with_ytdlp(url)

if __name__ == "__main__":
    main()


#!/usr/bin/env python3

import sys
import re
import subprocess
import time
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import browser_cookie3

BTN_TEXT = "charger plus"
YT_DLP_CMD = "yt-dlp --cookies-from-browser chrome --no-playlist --no-write-info-json --no-write-comments --no-write-subs --no-write-auto-subs --no-write-thumbnail --impersonate chrome"

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

def wait_for_button(page, timeout=5):
    """Attend l'apparition du bouton BTN_TEXT jusqu'à timeout secondes."""
    print(f"Attente du bouton '{BTN_TEXT}' (jusqu'à {timeout} secondes si besoin)...")
    for _ in range(timeout * 2):  # toutes les 0.5s jusqu'à timeout
        buttons = page.query_selector_all("button")
        for button in buttons:
            try:
                text = button.inner_text().strip().lower()
                if BTN_TEXT.lower() in text and button.is_enabled() and button.is_visible():
                    print(f"→ Bouton détecté : '{text}'")
                    return True
            except Exception:
                continue
        time.sleep(0.5)
    print(f"→ Aucun bouton '{BTN_TEXT}' détecté dans les {timeout}s.")
    return False

def click_load_more_buttons(page):
    click_count = 0
    while True:
        if not wait_for_button(page, timeout=5):
            break  # pas de bouton, fin
        buttons = page.query_selector_all("button")
        found = False
        for button in buttons:
            try:
                text = button.inner_text().strip().lower()
                if BTN_TEXT.lower() in text and button.is_enabled() and button.is_visible():
                    print(f"→ Bouton trouvé avec texte : '{text}', clic en cours...")
                    button.click()
                    found = True
                    click_count += 1
                    time.sleep(2.5)
                    break  # recherche du DOM après chaque clic
            except Exception:
                continue
        if not found:
            print(f"→ Aucun bouton '{BTN_TEXT}' visible, on arrête (clics : {click_count}).")
            break

def scroll_and_extract_links(collection_url):
    cookies = extract_cookies_for_playwright()
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        context.add_cookies(cookies)
        page = context.new_page()
        page.goto(collection_url)
        # attend que la liste des posts soit présente (div de collection ou premier post)
        print("Attente du chargement initial de la page...")
        page.wait_for_load_state("domcontentloaded")
        # Optionnel : attend 2s de plus pour être sûr que tout est là
        time.sleep(2)
        print(f"Clique automatique sur tous les boutons '{BTN_TEXT}' (case-insensitive)...")
        click_load_more_buttons(page)

        print("Extraction des liens...")
        content = page.content()
        browser.close()
        post_links = set(re.findall(r'https://www\.patreon\.com/posts/\d+', content))
        clean_links = set(link.split('?')[0] for link in post_links)
        return list(clean_links)

def download_with_ytdlp(post_url):
    cmd = f"{YT_DLP_CMD} \"{post_url}\""
    print(f"==> Téléchargement : {post_url}")
    subprocess.run(cmd, shell=True)

def main():
    if len(sys.argv) != 2:
        print("Usage : python3 get_posts_links.py <url_de_collection>")
        sys.exit(1)

    collection_url = sys.argv[1]
    if "patreon.com/collection/" not in collection_url:
        print("Erreur : l'URL fournie ne semble pas être une collection Patreon.")
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

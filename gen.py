import requests, re, os, datetime
from bs4 import BeautifulSoup
from colorama import Fore

e = datetime.datetime.now()
current_date = e.strftime("%Y-%m-%d-%H-%M-%S")
output_file = f"combos/scrapedcombos-{current_date}.txt"
agent = {'User-Agent': 'Mozilla/5.0'}

def save_combos(data, source):
    filtered = [line.strip() for line in data if ':' in line and len(line.strip()) <= 64]
    if filtered:
        print(Fore.GREEN + f"[+] {len(filtered)} combos scraped from {source}")
        with open(output_file, 'a', encoding='utf-8') as f:
            f.write(f"\n=== Source: {source} ===\n")
            f.write('\n'.join(filtered) + '\n')
    else:
        print(Fore.YELLOW + f"[!] No combos found at {source}")

def scrape_pastebin_clone():
    try:
        print(Fore.CYAN + "[~] Scraping from textbin.net (public pastes)")
        for i in range(1, 3):
            url = f"https://textbin.net/public-paste/{i}"
            html = requests.get(url, headers=agent, timeout=10).text
            soup = BeautifulSoup(html, 'html.parser')
            links = soup.find_all('a', href=True)
            for link in links:
                href = link['href']
                if href.startswith("/paste/"):
                    raw_url = f"https://textbin.net/raw{href}"
                    try:
                        content = requests.get(raw_url, headers=agent, timeout=10).text
                        data = content.splitlines()
                        save_combos(data, "textbin.net")
                    except: pass
    except Exception as e:
        print(Fore.RED + f"[!] Error: {e}")

def start():
    if not os.path.exists("combos"):
        os.makedirs("combos/")
    print(Fore.MAGENTA + "🔥 UltraLite Combo Scraper Started 🔥")
    scrape_pastebin_clone()
    print(Fore.GREEN + f"\n✅ Done! Combos saved to {output_file}")

start()

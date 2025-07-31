import requests, re, os, urllib3, datetime, threading, time
from bs4 import BeautifulSoup
from colorama import Fore, init
from pathvalidate import sanitize_filename

init(autoreset=True)
urllib3.disable_warnings()

agent = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'}
e = datetime.datetime.now()
current_date = e.strftime("%Y-%m-%d-%H-%M-%S")
scraped = 0
output_file = f'combos/scrapedcombos-{current_date}.txt'

if not os.path.exists("combos"):
    os.makedirs("combos/")

lock = threading.Lock()

def save_combos(data, source):
    global scraped
    filtered = [line.strip() for line in data if ':' in line and len(line.strip()) <= 64]
    scraped += len(filtered)

    with lock:
        with open(output_file, 'a', encoding='utf-8') as f:
            f.write(f"\n=== Source: {source} ===\n")
            for line in filtered:
                f.write(f"{line}\n")
    print(Fore.GREEN + f"[+] Scraped {len(filtered)} from {source}")

def get_links_from_forum(url, base, tag='a', class_name=None):
    links = []
    try:
        page = requests.get(url, headers=agent, timeout=10)
        soup = BeautifulSoup(page.text, 'html.parser')
        elements = soup.find_all(tag, class_=class_name) if class_name else soup.find_all(tag)
        for a in elements:
            href = a.get('href')
            if href and "/threads/" in href or "/topic/" in href:
                full_link = href if href.startswith("http") else base + href
                if full_link not in links:
                    links.append(full_link)
    except Exception as e:
        print(Fore.RED + f"[!] Error fetching links from {url}: {e}")
    return links

def extract_and_save_from_page(url, source):
    try:
        page = requests.get(url, headers=agent, timeout=10)
        soup = BeautifulSoup(page.text, 'html.parser')
        text_blocks = soup.find_all(text=re.compile(r'.+:.+'))
        lines = [line.strip() for line in text_blocks if ':' in line]
        save_combos(lines, source)
    except Exception as e:
        print(Fore.RED + f"[!] Error parsing page {url}: {e}")

def scrape_source(name, forum_url, base_url):
    print(Fore.CYAN + f"[~] Scraping {name}")
    links = get_links_from_forum(forum_url, base_url)
    for link in links[:5]:  # max 5 per site to limit overload
        extract_and_save_from_page(link, name)

def pastefo():
    print(Fore.CYAN + "[~] Scraping paste.fo")
    try:
        for page in range(1, 3):
            req = requests.get(f"https://paste.fo/recent/{page}", timeout=10)
            soup = BeautifulSoup(req.text, 'html.parser')
            tables = soup.find_all('tr', class_=False)
            for table in tables:
                a_tags = table.find_all('a')
                for a in a_tags:
                    link = f"https://paste.fo/raw{a.get('href')}"
                    try:
                        data = requests.get(link, timeout=10).text.splitlines()
                        if data:
                            save_combos(data, "paste.fo")
                    except: pass
    except Exception as e:
        print(Fore.RED + f"[!] paste.fo error: {e}")

def start():
    print(Fore.MAGENTA + "⚡ Combo Scraper Started ⚡\n")

    threads = [
        threading.Thread(target=scrape_source, args=("heypass.net", "https://heypass.net/forums/combo-lists.69/", "https://heypass.net")),
        threading.Thread(target=scrape_source, args=("nohide.space", "https://nohide.space/forums/free-email-pass.3/", "https://nohide.space")),
        threading.Thread(target=scrape_source, args=("nulled.to", "https://www.nulled.to/forum/74-combolists/", "https://www.nulled.to")),
        threading.Thread(target=scrape_source, args=("crackingx.com", "https://crackingx.com/forums/5/", "https://crackingx.com")),
        threading.Thread(target=scrape_source, args=("leaks.ro", "https://www.leaks.ro/forum/308-combolists/", "https://www.leaks.ro")),
        threading.Thread(target=scrape_source, args=("hellofhackers.com", "https://hellofhackers.com/forums/combolists.18/", "https://hellofhackers.com")),
        threading.Thread(target=scrape_source, args=("crackingpro.com", "https://www.crackingpro.com/forum/23-combos/", "https://www.crackingpro.com")),
        threading.Thread(target=pastefo)
    ]

    for t in threads:
        t.start()

    for t in threads:
        t.join()

    print(Fore.YELLOW + f"\n✅ Done! Scraped total: {scraped} combos.")
    print(Fore.GREEN + f"📁 Saved to: {output_file}")
    input("Press Enter to exit...")

if __name__ == "__main__":
    start()

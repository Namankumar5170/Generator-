import requests, re, subprocess, os, urllib3, datetime, threading, time, platform
from bs4 import BeautifulSoup
from colorama import Fore
from pathvalidate import sanitize_filename

# Disable SSL warnings
urllib3.disable_warnings()

# Global variables
e = datetime.datetime.now()
current_date = e.strftime("%Y-%m-%d-%H-%M-%S")
agent = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'}
pages = 0
scraped = 0

class leech():
    def save(output, thread, host, alr=False):
        global scraped
        if not alr:
            filtered = [line.strip() for line in output.split('\n')
                        if re.compile(r'([^\s|]+[@][^\s|]+[.][^\s|]+[:][^\s|]+)').match(line.strip())
                        and len(line.strip()) <= 64 and line.strip()]
        else:
            filtered = output

        filtered = [f"{line.split(':')[-2]}:{line.split(':')[-1]}" if line.startswith("http") else line for line in filtered]
        scraped += len(filtered)
        print(Fore.GREEN + f"Scraped [{len(filtered)}] from [{thread}] at [{host}]")
        open(f'combos/scrapedcombos-{current_date}.txt', 'a', encoding='utf-8').write('\n'.join(map(str, filtered)) + "\n")

    def gofile(link, thread, content_id=None):
        try:
            if content_id:
                token = requests.post("https://api.gofile.io/accounts").json()["data"]["token"]
                wt = requests.get("https://gofile.io/dist/js/alljs.js").text.split('wt: "')[1].split('"')[0]
                data = requests.get(
                    f"https://api.gofile.io/contents/{content_id}?wt={wt}&cache=true",
                    headers={"Authorization": "Bearer " + token}
                ).json()
                if data["status"] == "ok" and data["data"].get("passwordStatus", "passwordOk") == "passwordOk":
                    dir = os.path.join(link, sanitize_filename(data["data"]["name"]))
                    if data["data"]["type"] == "folder":
                        for cid in data["data"]["childrenIds"]:
                            child = data["data"]["children"][cid]
                            if child["type"] == "folder":
                                leech.gofile(dir, thread, content_id=cid)
                            else:
                                leech.save(requests.get(child["link"], headers={"Cookie": f"accountToken={token}"}).text, thread, "gofile.io")
                    else:
                        leech.save(requests.get(data["data"]["link"], headers={"Cookie": f"accountToken={token}"}).text, thread, "gofile.io")
            else:
                leech.gofile(link, thread, link.split("/")[-1])
        except:
            pass

    def handle(link, thread):
        try:
            if link.startswith('https://www.upload.ee/files/'):
                f = BeautifulSoup(requests.get(link, headers=agent).text, 'html.parser')
                dlink = f.find('a', id='d_l').get('href')
                leech.save(requests.get(dlink, headers=agent).text, thread, "upload.ee")

            elif link.startswith('https://www.mediafire.com/file/'):
                f = BeautifulSoup(requests.get(link, headers=agent).text, 'html.parser')
                dlink = f.find('a', id='downloadButton').get('href')
                leech.save(requests.get(dlink, headers=agent).text, thread, "mediafire.com")

            elif link.startswith('https://pixeldrain.com/u/'):
                leech.save(requests.get(link.replace("/u/", "/api/file/") + "?download", headers=agent).text, thread, "pixeldrain.com")

            elif link.startswith('https://mega.nz/file/'):
                if platform.system() == "Windows" and os.path.exists("megatools\\megatools.exe"):
                    process = subprocess.Popen(f"megatools\\megatools.exe dl {link} --no-ask-password --print-names", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
                    output = process.stdout.readlines()
                    process.wait()
                    if output:
                        saved = output[-1].strip()
                        with open(saved, 'r', encoding='utf-8') as f:
                            leech.save(f.read(), thread, "mega.nz")
                        os.remove(saved)
                else:
                    print(Fore.RED + "MEGA link skipped (megatools not available on this platform)")

            elif link.startswith('https://www.sendspace.com/file/'):
                soup = BeautifulSoup(requests.get(link, headers=agent).text, 'html.parser')
                download_link = soup.find('a', {'id': 'download_button'})['href']
                leech.save(requests.get(download_link, verify=False, headers=agent).text, thread, "sendspace.com")

            elif link.startswith('https://gofile.io/d/'):
                leech.gofile(link, thread)

        except Exception as e:
            print(Fore.RED + f"[handle] Error: {e}")

def title():
    try:
        import sys
        sys.stdout.write(f"\33]0;Combo Scraper by KillinMachine | Scraped: {scraped}\a")
        sys.stdout.flush()
    except:
        pass
    time.sleep(1)
    threading.Thread(target=title).start()

def start():
    global pages
    print(Fore.CYAN + "Combo Scraper by KillinMachine")
    pages = int(input(Fore.LIGHTGREEN_EX + "Pages to Scrape: ")) + 1
    if not os.path.exists("combos"):
        os.makedirs("combos/")
    title()

    # TODO: Add back actual scraping functions (like leech.heypass) here
    # Right now, we are only testing handle manually
    functions = [
        # Example: lambda: leech.handle("https://example.com/download.txt", "Manual")
    ]

    threads = []
    for func in functions:
        thread = threading.Thread(target=func)
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    print(Fore.YELLOW + f"Scraped [{scraped}] combos from [{len(functions) * pages}] pages.")
    input("Press Enter to exit...")

start()

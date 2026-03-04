import yt_dlp
import os
import requests
import time
import random

DISCORD_WEBHOOK = os.getenv('DISCORD_WEBHOOK')
FILE_PATH = 'urls.txt'

def check_videos():
    dead_links = []
    
    if not os.path.exists(FILE_PATH):
        return None, 0
    
    with open(FILE_PATH, "r", encoding="utf-8") as f:
        urls = [line.strip() for line in f if line.strip().startswith('http')]

    total_links = len(urls)
    print(f"Starting slow scan: {total_links} links...")
    
    ydl_opts = {
        'quiet': True, 
        'no_warnings': True, 
        'simulate': True, 
        'no_playlist': True,
        'extract_flat': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        for i, url in enumerate(urls):
            try:
                ydl.extract_info(url, download=False)
                print(f"[{i+1}/{total_links}] ✅ OK")
            except Exception as e:
                error_msg = str(e).lower()
                # On ne cible QUE les vrais morts (Privé, Supprimé)
                if any(word in error_msg for word in ["unavailable", "private", "removed", "deleted"]):
                    print(f"[{i+1}/{total_links}] ❌ DEAD")
                    dead_links.append(url)
                else:
                    # Tout le reste (Login, Bot check) est considéré comme OK
                    print(f"[{i+1}/{total_links}] ✅ OK (Security Check bypass)")
            
            # Pause de 10 secondes pour rester discret
            time.sleep(10 + random.uniform(0, 2))
            
    return dead_links, total_links

def send_to_discord(msg):
    if DISCORD_WEBHOOK:
        if len(msg) > 2000:
            msg = msg[:1990] + "..."
        requests.post(DISCORD_WEBHOOK, json={"content": msg})

# Lancement du scan
dead_results, total_count = check_videos()

if dead_results:
    header = f"@everyone 💫 **Woo Report** 💫\nFound **{len(dead_results)}** dead link(s) out of **{total_count}**:\n\n"
    report = header + "\n".join(dead_results)
    send_to_discord(report)
else:
    # Ton message personnalisé "Woo Hero" avec les emojis
    success_msg = "Woo Hero reporting for duty! Everything is safe. My job is to stalk links 24/7 under Cassius' basement to make sure they are still up and running 🏃. Hopefully I don't have to ping @everyone bc if so that means something got deleted 🙁"
    send_to_discord(success_msg)

import yt_dlp
import os
import requests
import time
import random

DISCORD_WEBHOOK = os.getenv('DISCORD_WEBHOOK')
FILE_PATH = 'urls.txt'

def check_videos():
    dead_links = []
    skipped_count = 0
    
    if not os.path.exists(FILE_PATH):
        return None, 0, 0
    
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
        # On utilise un User-Agent de navigateur très classique
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        for i, url in enumerate(urls):
            try:
                ydl.extract_info(url, download=False)
                print(f"[{i+1}/{total_links}] ✅ OK")
            except Exception as e:
                error_msg = str(e).lower()
                # On ne cible QUE les vrais liens morts
                if any(word in error_msg for word in ["unavailable", "private", "removed", "deleted"]):
                    print(f"[{i+1}/{total_links}] ❌ DEAD")
                    dead_links.append(url)
                else:
                    # Si c'est un message "Sign in", on l'ignore juste
                    print(f"[{i+1}/{total_links}] ⚠️ SKIP (Security Check)")
                    skipped_count += 1
            
            # 🕒 PAUSE DE 10 SECONDES (plus un petit chouia aléatoire pour faire humain)
            time.sleep(10 + random.uniform(0, 2))
            
    return dead_links, total_links, skipped_count

def send_to_discord(msg):
    if DISCORD_WEBHOOK:
        # Découpe le message si la liste de liens morts est trop longue (limite Discord 2000 chars)
        if len(msg) > 2000:
            msg = msg[:1990] + "..."
        requests.post(DISCORD_WEBHOOK, json={"content": msg})

# Lancement du scan
dead_results, total_count, skipped = check_videos()

if dead_results:
    header = f"@everyone 💫 **Woo Report** 💫\nFound **{len(dead_results)}** dead link(s) out of **{total_count}**:\n\n"
    report = header + "\n".join(dead_results)
    send_to_discord(report)
elif skipped > (total_count / 2):
    send_to_discord(f"⚠️ **Woo Report** ⚠️\nLe scan a été perturbé par YouTube. Résultat incomplet.")
else:
    send_to_discord(f"✅ **Woo Report** ✅\nAll **{total_count}** videos are online. Everything is safe! 🔥")

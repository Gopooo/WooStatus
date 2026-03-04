import yt_dlp
import os
import requests
import time
import random

DISCORD_WEBHOOK = os.getenv('DISCORD_WEBHOOK')
FILE_PATH = 'urls.txt'

def check_videos():
    dead_links = []
    skipped_links = 0
    
    if not os.path.exists(FILE_PATH):
        return None, 0, 0
    
    with open(FILE_PATH, 'r') as f:
        urls = [line.strip() for line in f if line.strip().startswith('http')]

    total_links = len(urls)
    print(f"Scanning {total_links} links with OAuth authentication...")
    
    ydl_opts = {
        'quiet': True, 
        'no_warnings': True, 
        'simulate': True, 
        'no_playlist': True,
        'extract_flat': True,
        # 🔑 CETTE LIGNE EST LA CLÉ
        'username': 'oauth2',
        'password': '',
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        for i, url in enumerate(urls):
            try:
                ydl.extract_info(url, download=False)
                print(f"[{i+1}/{total_links}] ✅ Active")
            except Exception as e:
                error_msg = str(e).lower()
                if any(word in error_msg for word in ["unavailable", "private", "removed", "deleted"]):
                    dead_links.append(url)
                    print(f"[{i+1}/{total_links}] ❌ Dead")
                else:
                    skipped_links += 1
                    print(f"[{i+1}/{total_links}] ⚠️ Skip: {error_msg[:50]}")
            
            # Délai aléatoire pour pas se faire flag
            time.sleep(random.uniform(3, 6))
            
    return dead_links, total_links, skipped_links

def send_to_discord(msg):
    if DISCORD_WEBHOOK:
        requests.post(DISCORD_WEBHOOK, json={"content": msg})

dead_results, total_count, skipped_count = check_videos()

if skipped_count > (total_count / 2):
    send_to_discord(f"⚠️ **Woo Report : Alerte Blocage** ⚠️\nLe bot est bloqué par YouTube ({skipped_count}/{total_count} erreurs).\nLe scan est faussé, il faut vérifier les logs GitHub.")
elif dead_results:
    report = f"@everyone 💫 **Woo Report** 💫\nFound **{len(dead_results)}** dead link(s):\n" + "\n".join(dead_results)
    send_to_discord(report)
else:
    send_to_discord(f"✅ **Woo Report** ✅\nScan complet. Les **{total_count}** vidéos sont safe! 🔥")

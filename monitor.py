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
    print(f"Scanning {total_links} links...")
    
    ydl_opts = {
        'quiet': True, 
        'no_warnings': True, 
        'simulate': True, 
        'no_playlist': True,
        'extract_flat': True,
        # Utilisation d'un User-Agent plus récent
        'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        for i, url in enumerate(urls):
            try:
                ydl.extract_info(url, download=False)
                print(f"[{i+1}/{total_links}] ✅ Active")
            except Exception as e:
                error_msg = str(e).lower()
                # On check si c'est vraiment mort
                if any(word in error_msg for word in ["unavailable", "private", "removed", "deleted"]):
                    dead_links.append(url)
                    print(f"[{i+1}/{total_links}] ❌ Dead")
                else:
                    # Si c'est un blocage "Bot", on compte comme skipped
                    skipped_links += 1
                    print(f"[{i+1}/{total_links}] ⚠️ Blocked by YouTube")
            
            # Délai aléatoire plus long pour 130+ liens
            time.sleep(random.uniform(4, 8))
            
    return dead_links, total_links, skipped_links

def send_to_discord(msg):
    if DISCORD_WEBHOOK:
        requests.post(DISCORD_WEBHOOK, json={"content": msg})

dead_results, total_count, skipped_count = check_videos()

# Nouveau système de message plus honnête
if skipped_count > (total_count / 2):
    # Si plus de la moitié est bloquée, le scan a échoué
    send_to_discord(f"⚠️ **Woo Report : Scan Interrompu** ⚠️\nYouTube a bloqué le bot (Bot Detection). Le rapport est incomplet.\nBloqués : {skipped_count}/{total_count}")
elif dead_results:
    report = f"@everyone 💫 **Woo Report** 💫\nFound **{len(dead_results)}** verified dead link(s):\n" + "\n".join(dead_results)
    send_to_discord(report)
else:
    send_to_discord(f"✅ **Woo Report** ✅\nAll **{total_count}** videos checked. Everything is safe! 🔥")

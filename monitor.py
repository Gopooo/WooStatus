import yt_dlp
import os
import requests
import time

# Get Webhook from GitHub Secrets
DISCORD_WEBHOOK = os.getenv('DISCORD_WEBHOOK')
FILE_PATH = 'urls.txt'

def check_videos():
    dead_links = []
    if not os.path.exists(FILE_PATH):
        return None
    
    with open(FILE_PATH, 'r') as f:
        urls = [line.strip() for line in f if line.strip().startswith('http')]

    print(f"Scanning {len(urls)} links...")
    
    # Configuration pour paraître "humain"
    ydl_opts = {
        'quiet': True, 
        'no_warnings': True, 
        'simulate': True, 
        'no_playlist': True,
        'extract_flat': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        for url in urls:
            try:
                # On essaie juste de récupérer les infos de base
                ydl.extract_info(url, download=False)
                print(f"✅ Active: {url}")
            except Exception as e:
                # On ne marque comme mort que si c'est vraiment une erreur de vidéo supprimée/privée
                error_msg = str(e)
                if "Video unavailable" in error_msg or "private" in error_msg or "removed" in error_msg:
                    print(f"❌ Dead: {url}")
                    dead_links.append(url)
                else:
                    # Si c'est un blocage de YouTube (Sign in, Bot detection), on ignore pour l'instant
                    print(f"⚠️ Blocked/Unknown: {url}")
            
            # Petite pause pour ne pas se faire bannir par YouTube
            time.sleep(1)
            
    return dead_links

def send_to_discord(msg):
    if DISCORD_WEBHOOK:
        # On découpe le message si trop long
        if len(msg) > 2000:
            msg = msg[:1990] + "..."
        requests.post(DISCORD_WEBHOOK, json={"content": msg})

# Execution
dead_results = check_videos()

if dead_results:
    report = f"⚠️ **YouTube Health Report** ⚠️\nFound **{len(dead_results)}** verified dead link(s):\n\n"
    report += "\n".join(dead_results)
    send_to_discord(report)
else:
    print("No dead links confirmed.")

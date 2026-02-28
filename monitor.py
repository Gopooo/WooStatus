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
        print(f"Error: {FILE_PATH} not found.")
        return None
    
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
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        for url in urls:
            try:
                ydl.extract_info(url, download=False)
                print(f"✅ Active: {url}")
            except Exception as e:
                error_msg = str(e).lower()
                if any(word in error_msg for word in ["unavailable", "private", "removed", "deleted"]):
                    print(f"❌ Dead: {url}")
                    dead_links.append(url)
                else:
                    print(f"⚠️ Blocked/Unknown: {url}")
            
            time.sleep(1.5)
            
    return dead_links, total_links

def send_to_discord(msg):
    if DISCORD_WEBHOOK:
        if len(msg) > 2000:
            msg = msg[:1990] + "..."
        requests.post(DISCORD_WEBHOOK, json={"content": msg})

# Execution
dead_results, total_count = check_videos()

if dead_results:
    # Rapport s'il y a des morts
    header = f"@everyone 💫 **Woo Report** 💫\nFound **{len(dead_results)}** dead link(s) out of **{total_count}**:\n\n"
    report = header + "\n".join(dead_results)
    send_to_discord(report)
else:
    # Nouveau : Rapport si TOUT est OK (On ne ping pas @everyone ici pour ne pas déranger inutilement)
    success_report = f"✅ **Woo Report** ✅\nAll **{total_count}** videos are online. Everything is safe! 🔥"
    send_to_discord(success_report)

import yt_dlp
import os
import requests

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

    print(f"Scanning {len(urls)} links...")
    
    ydl_opts = {
        'quiet': True, 
        'no_warnings': True, 
        'simulate': True, 
        'no_playlist': True,
        'extract_flat': True
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        for url in urls:
            try:
                ydl.extract_info(url, download=False)
            except:
                dead_links.append(url)
    return dead_links

def send_to_discord(msg):
    if DISCORD_WEBHOOK:
        requests.post(DISCORD_WEBHOOK, json={"content": msg})
    else:
        print("No Webhook configured, printing to console:\n", msg)

# Execution
dead_results = check_videos()

if dead_results:
    report = f"⚠️ **YouTube Health Report** ⚠️\nFound **{len(dead_results)}** dead link(s) in `urls.txt`:\n\n"
    report += "\n".join(dead_results)
    send_to_discord(report)
else:
    print("All links are active. No message sent.")
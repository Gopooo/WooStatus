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
        # On nettoie les liens (on enlève les espaces et les lignes vides)
        urls = [line.strip() for line in f if line.strip().startswith('http')]

    print(f"Scanning {len(urls)} links...")
    
    # Configuration pour éviter les blocs de YouTube
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
                # On tente de récupérer les infos sans télécharger
                ydl.extract_info(url, download=False)
                print(f"✅ Active: {url}")
            except Exception as e:
                error_msg = str(e).lower()
                # On vérifie si le message contient les mots-clés de suppression
                if any(word in error_msg for word in ["unavailable", "private", "removed", "deleted"]):
                    print(f"❌ Dead: {url}")
                    dead_links.append(url)
                else:
                    # En cas de blocage IP ou bot detection, on ne compte pas comme "dead"
                    print(f"⚠️ Blocked/Unknown: {url}")
            
            # Pause de 1.5s pour rester discret vis-à-vis de YouTube
            time.sleep(1.5)
            
    return dead_links

def send_to_discord(msg):
    if DISCORD_WEBHOOK:
        # Discord limite à 2000 caractères par message
        if len(msg) > 2000:
            msg = msg[:1990] + "..."
        requests.post(DISCORD_WEBHOOK, json={"content": msg})

# Execution
dead_results = check_videos()

if dead_results:
    # Ping everyone + Titre personnalisé
    header = f"@everyone 💫 **Woo Report** 💫\nFound **{len(dead_results)}** verified dead link(s) in the list:\n\n"
    report = header + "\n".join(dead_results)
    send_to_discord(report)
else:
    print("All links are active. Woo is safe.")

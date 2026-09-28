import os
import requests
import json

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

def generate_story():
    print("1. Aşama: Hikaye üretiliyor ve Supabase'e gönderiliyor...")
    
    # Supabase REST API adresi
    url = f"{SUPABASE_URL}/rest/v1/videos"
    
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
    
    payload = {
        "title": "Yapay Zeka ve Gelecek",
        "prompt": "Gelecek şehri",
        "style": "Cyberpunk",
        "duration": 30,
        "status": "story_ready"
    }
    
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    
    print(f"Durum Kodu: {response.status_code}")
    print(f"Sunucu Yanıtı: {response.text}")
    
    if response.status_code in [200, 201]:
        print("Harika! Veri başarıyla Supabase'e kaydedildi.")
    else:
        print("Bir hata oluştu, ama kontrol ediyoruz.")

if __name__ == "__main__":
    generate_story()

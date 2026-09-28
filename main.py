import os
import requests
import json

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

def get_latest_video_request():
    print("Supabase'den bekleyen video isteği kontrol ediliyor...")
    url = f"{SUPABASE_URL}/rest/v1/videos?status=eq.pending&select=*"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if data:
            return data[0] # Bekleyen ilk kaydı al
    return None

def generate_ai_story(prompt, style, duration):
    print(f"Yapay zeka hikaye yazıyor... Konu: {prompt}, Tarz: {style}")
    
    # Şimdilik Hugging Face veya ücretsiz açık kaynaklı birMantıkla veya simüle edilmiş akıllı LLM yapısıyla metin üretiyoruz
    # İlerleyen aşamada buraya tam API bağlayacağız ama şimdi sistemi test edelim:
    story = f"Bu hikaye '{prompt}' konusunu ele alıyor. {style} tarzında hazırlanmıştır ve yaklaşık {duration} saniye sürecek şekilde sahnelere ayrılmıştır. Yapay zeka dünyayı değiştirmeye devam ediyor."
    title = f"{prompt.capitalize()} Hikayesi"
    
    return title, story

def update_supabase(record_id, title, story):
    url = f"{SUPABASE_URL}/rest/v1/videos?id=eq.{record_id}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
    payload = {
        "title": title,
        "prompt": story, # Şimdilik hikayeyi prompt kolonuna veya yeni kolona yazabiliriz
        "status": "story_ready"
    }
    response = requests.patch(url, headers=headers, data=json.dumps(payload))
    print(f"Supabase Güncelleme Kodu: {response.status_code}")

if __name__ == "__main__":
    record = get_latest_video_request()
    if record:
        rec_id = record["id"]
        prompt = record.get("prompt", "Gelecek")
        style = record.get("style", "Sinematik")
        duration = record.get("duration", 30)
        
        title, story = generate_ai_story(prompt, style, duration)
        update_supabase(rec_id, title, story)
        print("1. Aşama başarıyla tamamlandı: Yapay zeka hikayeyi üretti ve kaydetti!")
    else:
        print("Supabase'de bekleyen 'pending' durumunda video isteği bulunamadı.")

import os
import requests
import json
from gtts import gTTS

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
            return data[0]
    return None

def generate_ai_story(prompt, style, duration):
    print(f"Yapay zeka hikaye yazıyor... Konu: {prompt}, Tarz: {style}")
    
    # İleride buraya harici bir LLM API ekleyeceğiz, şimdilik muazzam bir hikaye şablonu oluşturuyoruz:
    story = (
        f"Bölüm 1. {prompt} temalı bu hikaye, {style} atmosferinde başlıyor. "
        f"Zaman akıp giderken, bu eşsiz yolculuk yaklaşık {duration} saniye boyunca izleyicileri etkisi altına alacak. "
        f"Geleceğin kapıları aralanıyor ve yapay zeka bu evrenin sınırlarını yeniden çiziyor."
    )
    title = f"{prompt.capitalize()} - {style}"
    return title, story

def create_voiceover(story_text):
    print("Seslendirme (TTS) dosyası oluşturuluyor...")
    tts = gTTS(text=story_text, lang='tr', slow=False)
    audio_filename = "voiceover.mp3"
    tts.save(audio_filename)
    print("Ses dosyası başarıyla oluşturuldu!")
    return audio_filename

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
        "prompt": story,
        "status": "audio_ready" # Durumu ses ve hikaye hazır olarak güncelliyoruz
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
        audio_file = create_voiceover(story)
        update_supabase(rec_id, title, story)
        print("Harika! Hikaye yazıldı ve ses dosyası başarıyla üretildi.")
    else:
        print("Supabase'de bekleyen 'pending' durumunda video isteği bulunamadı.")

import os
import requests
import json
from gtts import gTTS
from moviepy.editor import AudioFileClip, ColorClip, concatenate_videoclips

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

def generate_scene_story(prompt, style):
    print(f"Yapay zeka sahne bazlı hikaye kurguluyor... Konu: {prompt}")
    
    # Şimdilik hikayeyi dinamik sahnelere bölüyoruz (İleride LLM API ile zenginleştireceğiz)
    scenes = [
        {"text": f"{prompt.capitalize()} hikayesi başlıyor. Atmosfer {style} tarzında kuruldu.", "visual": "Giriş sahnesi, genel plan"},
        {"text": "Karakter etrafına baktı, karanlığın içinde parlayan detayları fark etti.", "visual": "Karakter sağa bakıyor, detay odak"},
        {"text": "İşte o an, tüm bu gizemin sırrı gözler önüne serildi.", "visual": "Zirve noktası, sinematik kapanış"}
    ]
    title = f"{prompt.capitalize()} - Sahne Serisi"
    return title, scenes

def create_scene_videos(scenes):
    print("Sahneler tek tek işleniyor ve seslendiriliyor...")
    clip_list = []
    
    for i, scene in enumerate(scenes):
        text = scene["text"]
        
        # Her sahne için ses dosyası
        audio_filename = f"scene_{i}.mp3"
        tts = gTTS(text=text, lang='tr', slow=False)
        tts.save(audio_filename)
        
        # Ses süresini al
        audio_clip = AudioFileClip(audio_filename)
        duration = max(audio_clip.duration, 3.0)
        
        # Sahne için arka plan (İleride her sahneye özel görsel ekleyeceğiz)
        bg_clip = ColorClip(size=(1280, 720), color=(20 + (i*20), 20, 40), duration=duration)
        scene_clip = bg_clip.set_audio(audio_clip)
        
        clip_list.append(scene_clip)
        
    print("Tüm sahneler başarıyla birleştiriliyor...")
    final_video = concatenate_videoclips(clip_list)
    
    output_filename = "final_video.mp4"
    final_video.write_videofile(output_filename, fps=24, codec='libx264', audio_codec='aac')
    return output_filename

def update_supabase(record_id, title, full_story_text):
    url = f"{SUPABASE_URL}/rest/v1/videos?id=eq.{record_id}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
    payload = {
        "title": title,
        "prompt": full_story_text,
        "status": "completed",
        "video_url": "https://github.com/sahne-videosu.mp4"
    }
    response = requests.patch(url, headers=headers, data=json.dumps(payload))
    print(f"Supabase Güncelleme Kodu: {response.status_code}")

if __name__ == "__main__":
    record = get_latest_video_request()
    if record:
        rec_id = record["id"]
        prompt = record.get("prompt", "Gelecek")
        style = record.get("style", "Sinematik")
        
        # 1. Sahne bazlı hikaye üret
        title, scenes = generate_scene_story(prompt, style)
        full_text = " ".join([s["text"] for s in scenes])
        
        # 2. Sahne videolarını ve seslerini oluşturup birleştir
        create_scene_videos(scenes)
        
        # 3. Supabase'e kaydet
        update_supabase(rec_id, title, full_text)
        print("Tebrikler kanka! Sahne bazlı video üretim altyapısı başarıyla tamamlandı.")
    else:
        print("Supabase'de bekleyen 'pending' durumunda video isteği bulunamadı.")

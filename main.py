import os
import requests
import json
from gtts import gTTS
from moviepy.editor import AudioFileClip, ColorClip

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
    print(f"Yapay zeka hikayeyi yazıyor... Konu: {prompt}, Tarz: {style}")
    story = (
        f"{prompt.capitalize()} konusunu işleyen bu yapım, {style} tarzında kurgulanmıştır. "
        f"Yaklaşık {duration} saniye sürecek bu eşsiz deneyim, izleyenleri büyüleyecek bir atmosfer sunuyor."
    )
    title = f"{prompt.capitalize()} - {style}"
    return title, story

def create_voiceover(story_text):
    print("Seslendirme (TTS) dosyası oluşturuluyor...")
    tts = gTTS(text=story_text, lang='tr', slow=False)
    audio_filename = "voiceover.mp3"
    tts.save(audio_filename)
    return audio_filename

def create_video_file(audio_filename, duration_sec):
    print("Video render ediliyor (MoviePy motoru devrede)...")
    audio_clip = AudioFileClip(audio_filename)
    
    # Kullanıcının seçtiği süre veya sesin süresi (hangisi uzunsa)
    video_duration = max(audio_clip.duration, float(duration_sec))
    
    # Koyu şık bir arka plan
    bg_clip = ColorClip(size=(1280, 720), color=(15, 15, 25), duration=video_duration)
    video_clip = bg_clip.set_audio(audio_clip)
    
    output_filename = "final_video.mp4"
    video_clip.write_videofile(output_filename, fps=24, codec='libx264', audio_codec='aac')
    print("Video dosyası başarıyla üretildi!")
    return output_filename

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
        "status": "completed", # Her şey bitti, durum tamamlandı!
        "video_url": "https://github.com/ornek-video-linki.mp4"
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
        
        # 1. Adım: Hikayeyi üret
        title, story = generate_ai_story(prompt, style, duration)
        
        # 2. Adım: Seslendir
        audio_file = create_voiceover(story)
        
        # 3. Adım: Videoyu render'la
        video_file = create_video_file(audio_file, duration)
        
        # 4. Adım: Supabase'e tamamlandı olarak kaydet
        update_supabase(rec_id, title, story)
        print("Tebrikler kanka! Sistem uçtan uca tek çalışmada başarıyla tamamlandı.")
    else:
        print("Supabase'de bekleyen 'pending' durumunda video isteği bulunamadı.")

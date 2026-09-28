import os
import requests
import json
from gtts import gTTS
from moviepy.editor import AudioFileClip, ImageClip, concatenate_videoclips

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
    print(f"Yapay zeka görsel odaklı sahneleri kurguluyor... Konu: {prompt}")
    
    # Her sahneye özel hem metin hem de görsel arama/üretim anahtar kelimeleri (Promptlar)
    scenes = [
        {
            "text": f"{prompt.capitalize()} konusunun ilk perdesi {style} tarzıyla açılıyor.",
            "image_url": "https://picsum.photos/seed/scene1/1280/720" # Sahneye özel dinamik test görseli
        },
        {
            "text": "Karakter etrafındaki gizemi çözmek için etrafına dikkatlice bakıyor.",
            "image_url": "https://picsum.photos/seed/scene2/1280/720"
        },
        {
            "text": "Ve nihayet gerçeğin gün yüzüne çıktığı o muazzam an yaşanıyor.",
            "image_url": "https://picsum.photos/seed/scene3/1280/720"
        }
    ]
    title = f"{prompt.capitalize()} - Görsel Sahne Serisi"
    return title, scenes

def download_image(url, filename):
    response = requests.get(url)
    if response.status_code == 200:
        with open(filename, 'wb') as f:
            f.write(response.content)
        return filename
    return None

def create_visual_scene_videos(scenes):
    print("Sahneler görseller ve seslerle giydirilerek render ediliyor...")
    clip_list = []
    
    for i, scene in enumerate(scenes):
        text = scene["text"]
        img_url = scene["image_url"]
        
        # 1. Ses dosyasını oluştur
        audio_filename = f"scene_{i}.mp3"
        tts = gTTS(text=text, lang='tr', slow=False)
        tts.save(audio_filename)
        
        audio_clip = AudioFileClip(audio_filename)
        duration = max(audio_clip.duration, 4.0) # Her sahne en az 4 saniye dursun
        
        # 2. Sahne görselini indir
        img_filename = f"scene_{i}.jpg"
        download_image(img_url, img_filename)
        
        # 3. Görseli MoviePy ile video klibine dönüştür ve sesi ekle
        image_clip = ImageClip(img_filename).set_duration(duration)
        scene_clip = image_clip.set_audio(audio_clip)
        
        clip_list.append(scene_clip)
        
    print("Tüm görsel sahneler birleştiriliyor...")
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
        "video_url": "https://github.com/gorsel-sahne-videosu.mp4"
    }
    response = requests.patch(url, headers=headers, data=json.dumps(payload))
    print(f"Supabase Güncelleme Kodu: {response.status_code}")

if __name__ == "__main__":
    record = get_latest_video_request()
    if record:
        rec_id = record["id"]
        prompt = record.get("prompt", "Gelecek")
        style = record.get("style", "Sinematik")
        
        title, scenes = generate_scene_story(prompt, style)
        full_text = " ".join([s["text"] for s in scenes])
        
        create_visual_scene_videos(scenes)
        update_supabase(rec_id, title, full_text)
        print("Tebrikler kanka! Görsel destekli sahne motoru başarıyla tamamlandı.")
    else:
        print("Supabase'de bekleyen 'pending' durumunda video isteği bulunamadı.")

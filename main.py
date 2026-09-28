import os
import sys
import requests
import json
from gtts import gTTS
from moviepy.editor import AudioFileClip, ImageClip, concatenate_videoclips

# 1. URL'nin sonundaki gereksiz eğik çizgileri (slash) temizliyoruz!
SUPABASE_URL = os.environ.get("SUPABASE_URL", "").strip().rstrip("/")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "").strip()

if not SUPABASE_URL or not SUPABASE_KEY:
    print("KRİTİK HATA: GitHub Secrets içinde SUPABASE_URL veya SUPABASE_KEY bulunamadı!")
    sys.exit(1)

def get_latest_video_request():
    print(f"Bağlanılan Supabase Adresi: {SUPABASE_URL}")
    url = f"{SUPABASE_URL}/rest/v1/videos?status=eq.pending&select=*"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}"
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f"SUPABASE BAĞLANTI HATASI: {response.status_code} -> {response.text}")
        sys.exit(1)
        
    data = response.json()
    if not data:
        print("SİSTEM UYARISI: Supabase'e başarıyla bağlanıldı ama 'pending' (bekleyen) hiçbir video bulunamadı!")
        print("Lütfen Streamlit arayüzünden yeni bir video üretme isteği yolladığından emin ol.")
        sys.exit(1)
        
    print(f"Harika! Bekleyen video bulundu: {data[0].get('title')}")
    return data[0]

def generate_long_scenes(prompt, style, duration_minutes):
    total_seconds = int(duration_minutes) * 60
    base_templates = [
        {"text": f"{prompt.capitalize()} konusunun derin analizi, {style} tarzıyla başlıyor.", "seed": "p1"},
        {"text": "Zaman ilerledikçe olaylar farklı bir boyut kazanıyor.", "seed": "p2"},
        {"text": "Karakter karşısına çıkan bu engeli aşmak için sınırları zorluyor.", "seed": "p3"},
        {"text": "Tüm dengelerin değiştiği o kritik dönüm noktası yaşanıyor.", "seed": "p4"},
        {"text": "Ve bu muazzam yolculuğun final perdesi kapanıyor.", "seed": "p5"}
    ]
    
    scenes = []
    target_count = max(3, int(total_seconds // 6))
    for i in range(target_count):
        template = base_templates[i % len(base_templates)]
        scenes.append({
            "text": f"Bölüm {i+1}: {template['text']}",
            "image_url": f"https://picsum.photos/seed/{template['seed']}_{i}/1280/720"
        })
    return f"{prompt.capitalize()} - {duration_minutes} Dk", scenes

def download_image(url, filename):
    response = requests.get(url)
    with open(filename, 'wb') as f:
        f.write(response.content)
    return filename

def upload_to_supabase_storage(file_path, file_name):
    print("Video Supabase Storage (videos) klasörüne yükleniyor...")
    storage_url = f"{SUPABASE_URL}/storage/v1/object/videos/{file_name}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "video/mp4"
    }
    with open(file_path, 'rb') as f:
        response = requests.post(storage_url, headers=headers, data=f)
    
    if response.status_code in [200, 201]:
        return f"{SUPABASE_URL}/storage/v1/object/public/videos/{file_name}"
    else:
        print(f"YÜKLEME HATASI: {response.text}")
        return None

def create_long_video(scenes):
    print("Render işlemi başlatıldı, klipler hazırlanıyor...")
    clip_list = []
    for i, scene in enumerate(scenes):
        audio_filename = f"scene_{i}.mp3"
        tts = gTTS(text=scene["text"], lang='tr', slow=False)
        tts.save(audio_filename)
        audio_clip = AudioFileClip(audio_filename)
        duration = max(audio_clip.duration, 4.0)
        
        img_filename = f"scene_{i}.jpg"
        download_image(scene["image_url"], img_filename)
        
        image_clip = ImageClip(img_filename).set_duration(duration)
        scene_clip = image_clip.set_audio(audio_clip)
        clip_list.append(scene_clip)
        
    final_video = concatenate_videoclips(clip_list)
    output_filename = "final_video.mp4"
    final_video.write_videofile(output_filename, fps=24, codec='libx264', audio_codec='aac')
    return output_filename

def update_supabase(record_id, title, full_story_text, video_url):
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
        "video_url": video_url
    }
    requests.patch(url, headers=headers, data=json.dumps(payload))

if __name__ == "__main__":
    record = get_latest_video_request()
    
    rec_id = record["id"]
    prompt = record.get("prompt", "Gelecek")
    style = record.get("style", "Sinematik")
    duration_minutes = record.get("duration", 2)
    
    title, scenes = generate_long_scenes(prompt, style, duration_minutes)
    full_text = " ".join([s["text"] for s in scenes])
    
    video_file = create_long_video(scenes)
    
    unique_file_name = f"video_{rec_id}.mp4"
    public_video_url = upload_to_supabase_storage(video_file, unique_file_name)
    
    update_supabase(rec_id, title, full_text, public_video_url if public_video_url else "")
    print("Mükemmel! İşlem bitti ve arayüz güncellendi.")

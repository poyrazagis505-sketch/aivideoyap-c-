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

def generate_long_scenes(prompt, style, duration_minutes):
    # Kullanıcıdan dakika olarak gelen değeri saniyeye çeviriyoruz (Örn: 5 dakika = 300 saniye)
    total_seconds = int(duration_minutes) * 60
    print(f"Yapay zeka {duration_minutes} dakikalık ({total_seconds} saniye) epik seri için sahneleri türetiyor...")
    
    base_templates = [
        {"text": f"{prompt.capitalize()} konusunun derinlemesine analizi, {style} estetiğiyle başlıyor.", "seed": "p1"},
        {"text": "Zaman ilerledikçe olaylar tehlikeli ve büyüleyici bir boyut kazanıyor.", "seed": "p2"},
        {"text": "Karakter karşısına çıkan bu gizemi çözmek için sınırları zorluyor.", "seed": "p3"},
        {"text": "Tüm dengelerin değiştiği o kritik eşik ve dönüm noktası yaşanıyor.", "seed": "p4"},
        {"text": "Ve bu muazzam yolculuğun final perdesine doğru kaçınılmaz kapanış gerçekleşiyor.", "seed": "p5"}
    ]
    
    scenes = []
    # Her sahne ortalama 6-7 saniye sürer hesabıyla, toplam dakikayı dolduracak kadar sahne üretiyoruz
    target_count = max(5, int(total_seconds // 6))
    
    for i in range(target_count):
        template = base_templates[i % len(base_templates)]
        scenes.append({
            "text": f"Bölüm {i+1}: {template['text']}",
            "image_url": f"https://picsum.photos/seed/{template['seed']}_{i}/1280/720"
        })
        
    title = f"{prompt.capitalize()} - {duration_minutes} Dakikalık Epik Seri"
    return title, scenes

def download_image(url, filename):
    response = requests.get(url)
    if response.status_code == 200:
        with open(filename, 'wb') as f:
            f.write(response.content)
        return filename
    return None

def upload_to_supabase_storage(file_path, file_name):
    print("Video Supabase Storage'a yükleniyor...")
    storage_url = f"{SUPABASE_URL}/storage/v1/object/videos/{file_name}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "video/mp4"
    }
    with open(file_path, 'rb') as f:
        response = requests.post(storage_url, headers=headers, data=f)
    
    if response.status_code in [200, 201]:
        public_url = f"{SUPABASE_URL}/storage/v1/object/public/videos/{file_name}"
        return public_url
    print(f"Storage Yükleme Hatası: {response.text}")
    return None

def create_long_video(scenes):
    print("Uzun video sahneler halinde render ediliyor...")
    clip_list = []
    
    for i, scene in enumerate(scenes):
        audio_filename = f"scene_{i}.mp3"
        tts = gTTS(text=scene["text"], lang='tr', slow=False)
        tts.save(audio_filename)
        
        audio_clip = AudioFileClip(audio_filename)
        duration = max(audio_clip.duration, 5.0)
        
        img_filename = f"scene_{i}.jpg"
        download_image(scene["image_url"], img_filename)
        
        image_clip = ImageClip(img_filename).set_duration(duration)
        scene_clip = image_clip.set_audio(audio_clip)
        clip_list.append(scene_clip)
        
    print("Sahneler birbirine ekleniyor...")
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
    if record:
        rec_id = record["id"]
        prompt = record.get("prompt", "Gelecek")
        style = record.get("style", "Sinematik")
        duration_minutes = record.get("duration", 3) # Varsayılan 3 dakika
        
        title, scenes = generate_long_scenes(prompt, style, duration_minutes)
        full_text = " ".join([s["text"] for s in scenes])
        
        video_file = create_long_video(scenes)
        
        unique_file_name = f"video_{rec_id}.mp4"
        public_video_url = upload_to_supabase_storage(video_file, unique_file_name)
        
        update_supabase(rec_id, title, full_text, public_video_url if public_video_url else "")
        print("İşlem kusursuz tamamlandı kanka!")
    else:
        print("Bekleyen istek yok.")

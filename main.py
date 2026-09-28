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

def generate_long_scenes(prompt, style, duration):
    print(f"Yapay zeka uzun soluklu video için sahneleri türetiyor... Hedef Süre: {duration}s")
    
    # Süreye bağlı olarak sahne sayısını dinamik olarak artırıyoruz (20 dakikalık hedefe doğru ilk adım)
    # Her sahne ortalama 5-6 saniye sürer varsayımıyla sahne listesini çoğaltıyoruz
    base_scenes = [
        {"text": f"{prompt.capitalize()} konusunun derinliklerine iniyoruz. Tarz: {style}.", "img_seed": "part1"},
        {"text": "Zaman akıp gidiyor ve olaylar beklenmedik bir yöne evriliyor.", "img_seed": "part2"},
        {"text": "Karakter karşısına çıkan engelleri aşmak için yeni bir yol arıyor.", "img_seed": "part3"},
        {"text": "Gerçeğin perdesi aralanıyor ve sır perdesi çözülmeye başlıyor.", "img_seed": "part4"},
        {"text": "Ve bu eşsiz yolculuğun final sahnesine doğru yaklaşıyoruz.", "img_seed": "part5"}
    ]
    
    # Süre uzunsa sahneleri döngüye sokup uzatabiliriz
    scenes = []
    target_count = max(3, int(duration // 10))
    for i in range(target_count):
        template = base_scenes[i % len(base_scenes)]
        scenes.append({
            "text": f"Bölüm {i+1}: {template['text']}",
            "image_url": f"https://picsum.photos/seed/{template['img_seed']}_{i}/1280/720"
        })
        
    title = f"{prompt.capitalize()} - Uzun Soluklu Seri"
    return title, scenes

def download_image(url, filename):
    response = requests.get(url)
    if response.status_code == 200:
        with open(filename, 'wb') as f:
            f.write(response.content)
        return filename
    return None

def create_long_video(scenes):
    print("Uzun video için sahneler render ediliyor...")
    clip_list = []
    
    for i, scene in enumerate(scenes):
        text = scene["text"]
        img_url = scene["image_url"]
        
        audio_filename = f"scene_{i}.mp3"
        tts = gTTS(text=text, lang='tr', slow=False)
        tts.save(audio_filename)
        
        audio_clip = AudioFileClip(audio_filename)
        duration = max(audio_clip.duration, 5.0)
        
        img_filename = f"scene_{i}.jpg"
        download_image(img_url, img_filename)
        
        image_clip = ImageClip(img_filename).set_duration(duration)
        scene_clip = image_clip.set_audio(audio_clip)
        clip_list.append(scene_clip)
        
    print("Tüm sahneler birleştirilerek final video oluşturuluyor...")
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
        "video_url": "https://github.com/uzun-video.mp4"
    }
    requests.patch(url, headers=headers, data=json.dumps(payload))

if __name__ == "__main__":
    record = get_latest_video_request()
    if record:
        rec_id = record["id"]
        prompt = record.get("prompt", "Gelecek")
        style = record.get("style", "Sinematik")
        duration = record.get("duration", 30)
        
        title, scenes = generate_long_scenes(prompt, style, duration)
        full_text = " ".join([s["text"] for s in scenes])
        
        create_long_video(scenes)
        update_supabase(rec_id, title, full_text)
        print("İşlem tamamdır kanka!")
    else:
        print("Bekleyen istek yok.")

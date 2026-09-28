import os
from supabase import create_client, Client

# Supabase bağlantı bilgilerini GitHub gizli anahtarlarından (secrets) alacağız
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def generate_story():
    print("1. Aşama: Hikaye üretiliyor...")
    # Şimdilik örnek bir hikaye metni oluşturalım (İlerleyen aşamalarda buraya AI entegre edeceğiz)
    title = "Yapay Zeka ve Gelecek"
    story = "Gelecekte yapay zeka insanlığın en büyük dostu haline geldi. Şehirler uçan arabalarla doluydu ve herkes mutluydu."
    
    # Bilgileri Supabase'e kaydedelim
    data = {
        "title": title,
        "prompt": "Gelecek şehri",
        "style": "Cyberpunk",
        "duration": 30,
        "status": "story_ready"
    }
    
    response = supabase.table("videos").insert(data).execute()
    print("Hikaye başarıyla Supabase'e kaydedildi!", response)

if __name__ == "__main__":
    generate_story()

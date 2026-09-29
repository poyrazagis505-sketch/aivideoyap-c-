import streamlit as st
import os
import requests
import json

st.set_page_config(page_title="AI Video Fabrikası", page_icon="🎬", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .stButton>button {
        background: linear-gradient(90deg, #FF4B2B 0%, #FF416C 100%);
        color: white; border: none; border-radius: 8px;
        padding: 12px 24px; font-weight: bold; width: 100%;
    }
    .stTextInput>div>div>input, .stSelectbox>div>div>select {
        background-color: #262730; color: white; border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🎬 AI Video Fabrikası - Dakika Esaslı Sürüm")
st.write("Kanka süre artık tamamen **dakika** bazlı! 1 dakikadan 20 dakikaya kadar dilediğin gibi ayarla.")

prompt = st.text_input("Videomuzun konusu ne olsun?", placeholder="Örn: Yapay zekanın gizli evreni ve geleceği")
style = st.selectbox("Görsel / Anlatım Tarzı Seç:", ["Sinematik", "Cyberpunk", "Anime", "Realistik", "Karanlık ve Gizemli"])
duration_minutes = st.slider("Video Süresi (Dakika):", 1, 20, 3)

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL and "SUPABASE_URL" in st.secrets:
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

if st.button("🚀 Epik Videoyu Üretmeye Başla!"):
    if not prompt:
        st.warning("Lütfen önce bir konu yaz kanka!")
    else:
        with st.spinner("İstek Supabase veritabanına işleniyor..."):
            url = f"{SUPABASE_URL}/rest/v1/videos"
            headers = {
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "application/json",
                "Prefer": "return=representation"
            }
            payload = {
                "title": prompt[:30] + f" ({duration_minutes} dk)",
                "prompt": prompt,
                "style": style,
                "duration": duration_minutes,
                "status": "pending"
            }
            response = requests.post(url, headers=headers, data=json.dumps(payload))
            if response.status_code in [200, 201]:
                st.success(f"Harika! {duration_minutes} dakikalık üretim emri verildi. GitHub Actions'tan çalıştırabilirsin.")
                st.balloons()
            else:
                st.error(f"Hata: {response.text}")

st.markdown("---")
st.subheader("📊 Son Üretilen Videolar ve Durumları")

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}"
}

response = requests.get(f"{SUPABASE_URL}/rest/v1/videos?select=*&order=created_at.desc&limit=3", headers=headers)
if response.status_code == 200:
    videos = response.json()
    if not videos:
        st.info("Henüz veritabanında kayıtlı video yok.")
    for v in videos:
        status = v.get('status')
        status_icon = "🟢" if status == 'completed' else "🟡"
        st.write(f"{status_icon} **Başlık:** {v.get('title')} | **Durum:** `{status}`")
        
        # Hata ayıklama için veritabanından gelen URL'yi direkt ekrana basalım görelim
        v_url = v.get('video_url')
        st.text(f"Kayıtlı Link: {v_url if v_url else 'Boş (Henüz yüklenmedi)'}")
        
        if status == 'completed' and v_url and v_url.startswith("http"):
            st.video(v_url)
            st.markdown(f"📥 [Videoyu Doğrudan İndir]({v_url})")
        
        st.markdown("---")

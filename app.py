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

st.title("🎬 AI Video Fabrikası - Kişisel Kontrol Paneli")
st.write("Kanka sistem tamamen senin kontrolünde. Konuyu gir, videonu üret ve aşağıdan yönet!")

prompt = st.text_input("Videomuzun konusu ne olsun?", placeholder="Örn: Yapay zekanın geleceği ve evren")
style = st.selectbox("Görsel / Anlatım Tarzı Seç:", ["Sinematik", "Cyberpunk", "Anime", "Realistik", "Karanlık ve Gizemli"])
duration = st.slider("Video Süresi (Saniye):", 15, 120, 30)

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL and "SUPABASE_URL" in st.secrets:
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

if st.button("🚀 Videoyu Üretmeye Başla!"):
    if not prompt:
        st.warning("Lütfen önce bir konu yaz kanka!")
    else:
        with st.spinner("İstek Supabase'e işleniyor..."):
            url = f"{SUPABASE_URL}/rest/v1/videos"
            headers = {
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "application/json",
                "Prefer": "return=representation"
            }
            payload = {
                "title": prompt[:30] + "...",
                "prompt": prompt,
                "style": style,
                "duration": duration,
                "status": "pending"
            }
            response = requests.post(url, headers=headers, data=json.dumps(payload))
            if response.status_code in [200, 201]:
                st.success("Harika! İstek işleme alındı. GitHub Actions üzerinden çalıştırıp videonu üretebilirsin.")
                st.balloons()
            else:
                st.error(f"Hata: {response.text}")

st.markdown("---")
st.subheader("📊 Üretilen Videolar ve Medya Oynatıcı")

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}"
}
response = requests.get(f"{SUPABASE_URL}/rest/v1/videos?select=*&order=created_desc", headers=headers)
if response.status_code == 200:
    videos = response.json()
    for v in videos:
        status = v.get('status')
        status_icon = "🟢" if status == 'completed' else "🟡"
        st.write(f"{status_icon} **Başlık:** {v.get('title')} | **Durum:** `{status}`")
        
        if v.get('prompt'):
            with st.expander("Hikaye ve Sahne Detaylarını Gör"):
                st.write(v.get('prompt'))
                
        # Eğer video tamamlandıysa oynatıcı ve indirme alanını göster
        if status == 'completed':
            video_url = v.get('video_url')
            if video_url and video_url.startswith("http"):
                st.video(video_url)
            else:
                st.info("Video render edildi ancak harici link henüz eklenmedi. (İleride buraya Supabase Storage linkini basacağız)")
                
        st.markdown("---")

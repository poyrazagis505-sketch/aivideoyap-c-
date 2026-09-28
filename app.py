import streamlit as st
import os
import requests
import json

# Sayfa Ayarları ve Şık Tasarım
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

st.title("🎬 AI Video Fabrikası - Kontrol Paneli")
st.write("Kanka hoş geldin! Tek tıkla yapay zeka video üretim motorunu tetikle.")

# Kullanıcı Girdileri
prompt = st.text_input("Videomuzun konusu ne olsun?", placeholder="Örn: Yapay zekanın geleceği ve uzay yolculuğu")
style = st.selectbox("Görsel / Anlatım Tarzı Seç:", ["Sinematik", "Cyberpunk", "Anime", "Realistik", "Karanlık ve Gizemli"])
duration = st.slider("Video Süresi (Saniye):", 15, 60, 30)

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL and "SUPABASE_URL" in st.secrets:
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

if st.button("🚀 Videoyu Tek Tuşla Üretmeye Başla!"):
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
                "title": prompt[:30] + "...",
                "prompt": prompt,
                "style": style,
                "duration": duration,
                "status": "pending"
            }
            
            response = requests.post(url, headers=headers, data=json.dumps(payload))
            
            if response.status_code in [200, 201]:
                st.success("Harika! İstek sisteme düştü. Şimdi GitHub Actions üzerinden çalıştırıp videoyu üretebilirsin!")
                st.balloons()
            else:
                st.error(f"Bir hata oluştu kanka: {response.text}")

st.markdown("---")
st.subheader("📊 Sistem Durumu ve Geçmiş Üretimler")

# Supabase'den kayıtları çekip gösterelim
headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}"
}
response = requests.get(f"{SUPABASE_URL}/rest/v1/videos?select=*", headers=headers)
if response.status_code == 200:
    videos = response.json()
    for v in videos:
        status = v.get('status')
        status_icon = "🟢" if status == 'completed' else "🟡"
        st.write(f"{status_icon} **Başlık:** {v.get('title')} | **Durum:** `{status}`")
        if v.get('prompt'):
            with st.expander("Hikaye ve Detayları Gör"):
                st.write(v.get('prompt'))
        st.markdown("---")

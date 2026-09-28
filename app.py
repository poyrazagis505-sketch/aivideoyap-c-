import streamlit as st
import os
import requests
import json

# Sayfa Ayarları ve Şık Tasarım (CSS)
st.set_page_config(page_title="AI Video Fabrikası", page_icon="🎬", layout="centered")

st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
        color: #ffffff;
    }
    .stButton>button {
        background: linear-gradient(90deg, #FF4B2B 0%, #FF416C 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 24px;
        font-weight: bold;
        width: 100%;
    }
    .stTextInput>div>div>input, .stSelectbox>div>div>select {
        background-color: #262730;
        color: white;
        border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🎬 AI Video Üretim Paneli")
st.write("Kanka hoş geldin! Buradan konuyu gir, yapay zeka senin için hikayeyi ve videoyu hazırlasın.")

# Kullanıcıdan Girdileri Alalım
prompt = st.text_input("Videomuzun konusu ne olsun?", placeholder="Örn: Uzayda yalnız kalan bir astronotun hikayesi")
style = st.selectbox("Görsel / Anlatım Tarzı Seç:", ["Sinematik", "Cyberpunk", "Anime", "Realistik", "Karanlık ve Gizemli"])
duration = st.slider("Video Süresi (Saniye):", 15, 60, 30)

if st.button("🚀 Videoyu Üretmeye Başla!"):
    if not prompt:
        st.warning("Lütfen önce bir konu (prompt) yaz kanka!")
    else:
        with st.spinner("Yapay zeka sisteme işleniyor ve Supabase'e kaydediliyor..."):
            SUPABASE_URL = os.environ.get("SUPABASE_URL")
            SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
            
            # Eğer localde çalıştırıyorsan Streamlit secrets'tan alır, GitHub'da Actions ile çalışır
            if not SUPABASE_URL and "SUPABASE_URL" in st.secrets:
                SUPABASE_URL = st.secrets["SUPABASE_URL"]
                SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

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
                st.success("Harika! İstek Supabase veritabanına başarıyla iletildi! Arka planda işleme alınıyor.")
                st.balloons()
            else:
                st.error(f"Bir hata oluştu kanka: {response.text}")

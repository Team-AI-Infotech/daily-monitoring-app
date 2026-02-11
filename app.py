import streamlit as st
from github import Github
import pandas as pd

# 1. Konfigurasi Halaman
st.set_page_config(
    page_title="Team Daily Monitoring",
    page_icon="📊",
    layout="wide"
)

# 2. Keamanan: Mengambil Token dari Secrets Streamlit Cloud
# Jangan tulis token langsung di sini! Masukkan di menu 'Settings > Secrets' di Streamlit Cloud
try:
    GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
    # Ganti dengan format: "Nama-Organisasi/Nama-Repo"
    REPO_NAME = "NAMA_ORGANISASI_ANDA/NAMA_REPO_ANDA" 
except:
    st.error("Konfigurasi GITHUB_TOKEN tidak ditemukan di Secrets!")
    st.stop()

def get_reports():
    try:
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(REPO_NAME)
        # Mengambil issue yang masih terbuka
        issues = repo.get_issues(state='open')
        
        data = []
        for issue in issues:
            # Kita filter agar hanya mengambil issue yang punya label 'daily-report' atau sesuai template
            data.append({
                "Tanggal": issue.created_at.strftime("%d %b %Y"),
                "User": issue.user.login,
                "Avatar": issue.user.avatar_url,
                "Judul": issue.title,
                "Detail": issue.body,
                "Link": issue.html_url,
                "Labels": [l.name for l in issue.labels]
            })
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"Gagal menarik data: {e}")
        return pd.DataFrame()

# --- UI DASHBOARD ---
st.title("🚀 Team Progress Dashboard")
st.subheader(f"Project: {REPO_NAME}")

if st.button('🔄 Refresh Laporan Terbaru'):
    df = get_reports()
    
    if not df.empty:
        # Ringkasan Anggota
        st.markdown("### 👥 Kontribusi Tim")
        unique_users = df['User'].unique()
        cols = st.columns(len(unique_users))
        
        for i, user in enumerate(unique_users):
            user_data = df[df['User'] == user]
            with cols[i]:
                st.image(user_data.iloc[0]['Avatar'], width=80)
                st.metric(label=user, value=f"{len(user_data)} Report")
        
        st.divider()

        # List Laporan
        st.markdown("### 📝 Detail Progres & Isu")
        for _, row in df.iterrows():
            with st.expander(f"{row['Tanggal']} - {row['Judul']} (oleh {row['User']})"):
                st.markdown(row['Detail'])
                st.info(f"Tag: {', '.join(row['Labels'])}")
                st.link_button("Buka di GitHub", row['Link'])
    else:
        st.info("Belum ada laporan (Issue) yang dibuat di repositori ini.")

else:
    st.write("Klik tombol 'Refresh' untuk melihat progres tim Anda.")

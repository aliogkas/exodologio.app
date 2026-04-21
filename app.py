import streamlit as st
import requests
import datetime
import unicodedata

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

# ==============================
# 🔐 CONFIG
# ==============================

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

SPREADSHEET_ID = "1yKVCbakKRLRGJIkv0SIJ3ujy7rhOZ_n64rEwDDNglLM"

# ✅ ΤΟ ΣΩΣΤΟ ΟΝΟΜΑ ΤΟΥ SHEET
SHEET_NAME = "exodologio"

# ==============================
# 🔐 GOOGLE AUTH
# ==============================

scope = ["https://www.googleapis.com/auth/spreadsheets"]

creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=scope
)

service = build("sheets", "v4", credentials=creds)
sheet = service.spreadsheets()

# ==============================
# 🧹 CLEAN FILENAME
# ==============================

def clean_filename(name):
    return unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()

# ==============================
# ☁️ UPLOAD TO SUPABASE
# ==============================

def upload_to_supabase(file):
    safe_name = clean_filename(file.name)

    url = f"{SUPABASE_URL}/storage/v1/object/public/files/{safe_name}"

    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}"
    }

    files = {
        "file": (safe_name, file, file.type)
    }

    response = requests.post(url, headers=headers, files=files)

    if response.status_code in [200, 201]:
        return f"{SUPABASE_URL}/storage/v1/object/public/files/{safe_name}"
    else:
        st.error(f"Upload error: {response.text}")
        return ""

# ==============================
# 🎨 UI
# ==============================

st.title("📊 Εξοδολόγιο")

with st.form("form"):
    user = st.text_input("Όνομα χρήστη")
    date = st.date_input("Ημερομηνία", datetime.date.today())
    category = st.text_input("Κατηγορία")
    amount = st.number_input("Ποσό", min_value=0.0, step=0.1)
    notes = st.text_input("Σημειώσεις")
    uploaded_file = st.file_uploader("Αρχείο (εικόνα/pdf)", type=["jpg", "png", "pdf"])

    submit = st.form_submit_button("Καταχώρηση")

# ==============================
# 🚀 SUBMIT
# ==============================

if submit:

    if user.strip() == "":
        st.error("Βάλε όνομα χρήστη")
    else:
        file_link = ""

        if uploaded_file:
            file_link = upload_to_supabase(uploaded_file)

        values = [[
            user,
            str(date),
            category,
            amount,
            notes,
            file_link
        ]]

        try:
            sheet.values().append(
                spreadsheetId=SPREADSHEET_ID,
                range=f"{SHEET_NAME}!A1",
                valueInputOption="USER_ENTERED",
                insertDataOption="INSERT_ROWS",
                body={"values": values}
            ).execute()

            st.success("✅ Καταχωρήθηκε!")

        except Exception as e:
            st.error(f"Σφάλμα Google Sheets: {str(e)}")

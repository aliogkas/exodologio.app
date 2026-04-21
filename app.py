import streamlit as st
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
import requests
import time

# ========================
# SETTINGS
# ========================

SHEET_ID = "1yKVCbakKRLRGJIkv0SIJ3ujy7rhOZ_n64rEwDDNglLM"

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

scope = ["https://www.googleapis.com/auth/spreadsheets"]

creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=scope
)

client = gspread.authorize(creds)
sheet = client.open_by_key(SHEET_ID).sheet1

# ========================
# UPLOAD FUNCTION
# ========================

def upload_to_supabase(file):
    timestamp = int(time.time())
    file_name = f"{timestamp}_{file.name}"

    url = f"{SUPABASE_URL}/storage/v1/object/receipts/{file_name}"

    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": file.type
    }

    response = requests.post(url, headers=headers, data=file.read())

    if response.status_code in [200, 201]:
        public_url = f"{SUPABASE_URL}/storage/v1/object/public/receipts/{file_name}"
        return public_url
    else:
        st.error(response.text)
        return ""

# ========================
# UI
# ========================

st.title("Καταχώριση Εξόδων")

name = st.text_input("Όνομα εργαζόμενου")
date = st.date_input("Ημερομηνία", datetime.today())
description = st.text_input("Περιγραφή")
amount = st.number_input("Ποσό", min_value=0.0)
uploaded_file = st.file_uploader("Επισύναψη αρχείου")

if st.button("Καταχώριση"):
    if name and description and amount:

        file_link = ""

        if uploaded_file is not None:
            file_link = upload_to_supabase(uploaded_file)

        new_row = [
            name,
            str(date),
            description,
            amount,
            file_link
        ]

        sheet.append_row(new_row)

        st.success("Η καταχώριση αποθηκεύτηκε!")

    else:
        st.error("Συμπλήρωσε όλα τα πεδία!")

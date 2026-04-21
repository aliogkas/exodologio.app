import streamlit as st
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io

# ========================
# SETTINGS
# ========================

SHEET_ID = "1yKVCbakKRLRGJIkv0SIJ3ujy7rhOZ_n64rEwDDNglLM"
YOUR_EMAIL = "jaliogkas2@gmail.com"

scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=scope
)

# Google Sheets
client = gspread.authorize(creds)
sheet = client.open_by_key(SHEET_ID).sheet1

# Google Drive
drive_service = build('drive', 'v3', credentials=creds)

# ========================
# UI
# ========================

st.title("Καταχώριση Εξόδων")

name = st.text_input("Όνομα εργαζόμενου")
date = st.date_input("Ημερομηνία", datetime.today())
description = st.text_input("Περιγραφή")
amount = st.number_input("Ποσό", min_value=0.0)
uploaded_file = st.file_uploader("Επισύναψη αρχείου (φωτογραφία ή pdf)")

if st.button("Καταχώριση"):
    if name and description and amount:

        file_link = ""

        try:
            if uploaded_file is not None:
                file_bytes = uploaded_file.read()
                file_stream = io.BytesIO(file_bytes)

                file_metadata = {
                    'name': uploaded_file.name
                }

                media = MediaIoBaseUpload(file_stream, mimetype=uploaded_file.type)

                # Upload file
                file = drive_service.files().create(
                    body=file_metadata,
                    media_body=media,
                    fields='id'
                ).execute()

                file_id = file.get('id')

                # Share ONLY to your email
                drive_service.permissions().create(
                    fileId=file_id,
                    body={
                        "role": "reader",
                        "type": "user",
                        "emailAddress": YOUR_EMAIL
                    }
                ).execute()

                # File link
                file_link = f"https://drive.google.com/file/d/{file_id}/view"

            # Save to sheet
            new_row = [
                name,
                str(date),
                description,
                amount,
                file_link
            ]

            sheet.append_row(new_row)

            st.success("Η καταχώριση αποθηκεύτηκε!")

        except Exception as e:
            st.error(f"Σφάλμα: {e}")

    else:
        st.error("Συμπλήρωσε όλα τα πεδία!")

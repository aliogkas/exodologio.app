import streamlit as st
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
import os

# ========================
# SETTINGS
# ========================

SHEET_ID = "1yKVCbakKRLRGJIkv0SIJ3ujy7rhOZ_n64rEwDDNglLM"

scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=scope
)

client = gspread.authorize(creds)
sheet = client.open_by_key(SHEET_ID).sheet1

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

        file_name = ""

        if uploaded_file is not None:
            os.makedirs("uploads", exist_ok=True)
            file_path = os.path.join("uploads", uploaded_file.name)

            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            file_name = uploaded_file.name

        new_row = [
            name,
            str(date),
            description,
            amount,
            file_name
        ]

        sheet.append_row(new_row)

        st.success("Η καταχώριση αποθηκεύτηκε!")

    else:
        st.error("Συμπλήρωσε όλα τα πεδία!")

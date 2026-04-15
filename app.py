import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- Φάκελοι ---
DATA_FOLDER = "data"
ATTACHMENTS_FOLDER = "attachments"
EXCEL_FILE = os.path.join(DATA_FOLDER, "expenses.xlsx")

os.makedirs(DATA_FOLDER, exist_ok=True)
os.makedirs(ATTACHMENTS_FOLDER, exist_ok=True)

# --- Τίτλος εφαρμογής ---
st.title("Καταχώριση Εξόδων")

# --- Φόρμα για νέο έξοδο ---
with st.form("new_expense"):
    date = st.date_input("Ημερομηνία", datetime.today())
    description = st.text_input("Περιγραφή")
    amount = st.number_input("Ποσό", min_value=0.0, format="%.2f")
    uploaded_file = st.file_uploader("Επισύναψη αρχείου (φωτογραφία ή pdf)", type=["jpg","jpeg","png","pdf"])
    submit = st.form_submit_button("Καταχώριση")

    if submit:
        # --- Ανέβασμα επισυναπτόμενου ---
        attachment_path = ""
        if uploaded_file:
            attachment_path = os.path.join(ATTACHMENTS_FOLDER, uploaded_file.name)
            with open(attachment_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

        # --- Διαχείριση Excel ---
        if os.path.exists(EXCEL_FILE):
            df = pd.read_excel(EXCEL_FILE)
        else:
            df = pd.DataFrame(columns=["Ημερομηνία", "Περιγραφή", "Ποσό", "Αρχείο"])

        df = pd.concat([df, pd.DataFrame([{
            "Ημερομηνία": date,
            "Περιγραφή": description,
            "Ποσό": amount,
            "Αρχείο": attachment_path
        }])], ignore_index=True)

        df.to_excel(EXCEL_FILE, index=False)
        st.success("Η καταχώριση προστέθηκε!")

# --- Προβολή καταχωρίσεων ---
st.subheader("Καταχωρισμένα έξοδα")
if os.path.exists(EXCEL_FILE):
    df = pd.read_excel(EXCEL_FILE)
    for i, row in df.iterrows():
        file_link = ""
        if pd.notna(row["Αρχείο"]) and os.path.exists(row["Αρχείο"]):
            file_link = f"[Άνοιγμα αρχείου]({row['Αρχείο']})"
        st.markdown(f"- {row['Ημερομηνία']} | {row['Περιγραφή']} | {row['Ποσό']} € {file_link}")
else:
    st.info("Δεν υπάρχουν καταχωρίσεις ακόμη.")
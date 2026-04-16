import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Φάκελοι
data_folder = "data"
attachments_folder = "attachments"

os.makedirs(data_folder, exist_ok=True)
os.makedirs(attachments_folder, exist_ok=True)

excel_file = os.path.join(data_folder, "expenses.xlsx")

st.title("Καταχώριση Εξόδων")

# Πεδία
name = st.text_input("Όνομα εργαζόμενου")
date = st.date_input("Ημερομηνία")
description = st.text_input("Περιγραφή")
amount = st.number_input("Ποσό", min_value=0.0)
uploaded_file = st.file_uploader("Επισύναψη αρχείου", type=["jpg", "jpeg", "png", "pdf"])

if st.button("Καταχώριση"):
    file_path = ""

    if uploaded_file is not None:
        file_path = os.path.join(attachments_folder, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

    new_data = {
        "Ημερομηνία": str(date),
        "Όνομα": name,
        "Περιγραφή": description,
        "Ποσό": amount,
        "Απόδειξη": file_path
    }

    # Αν υπάρχει ήδη το Excel
    if os.path.exists(excel_file):
        df = pd.read_excel(excel_file)
        df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
    else:
        df = pd.DataFrame([new_data])

    df.to_excel(excel_file, index=False)

    st.success("Η καταχώριση αποθηκεύτηκε!")

# Προβολή δεδομένων
if os.path.exists(excel_file):
    df = pd.read_excel(excel_file)
    st.subheader("Καταχωρίσεις")
    st.dataframe(df)

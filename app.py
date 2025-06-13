# app.py
import streamlit as st
import pandas as pd
from logic import load_icrs_nomogram, process_eye_data, detect_form_fruste, generate_pdf_summary

st.set_page_config(layout="wide")
st.title("Keratoconus Management Planning Tool")

# Load nomogram
df_nomogram = load_icrs_nomogram()

# Shared age input
age = st.number_input("Patient Age", min_value=5, max_value=100, value=18, step=1)

st.markdown("### Input Parameters")

col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Left Eye")
    left_eye = {
        'sphere': st.number_input("Sphere (Left)", value=0.0),
        'cylinder': st.number_input("Cylinder (Left)", value=0.0),
        'k1': st.number_input("K1 (Left)", value=46.0),
        'k2': st.number_input("K2 (Left)", value=48.0),
        'kmax': st.number_input("Kmax (Left)", value=48.0),
        'pachy': st.number_input("Pachymetry (Left)", value=480),
        'bcva': st.number_input("BCVA (Left)", value=0.5),
        'cone_distribution': st.selectbox("Cone Distribution (Left)", [
            "100 % cone on one side",
            "80 % :20 % ",
            "60 % :40 % ",
            "50 % :50 % "
        ]),
        'age': age
    }

with col_right:
    st.subheader("Right Eye")
    right_eye = {
        'sphere': st.number_input("Sphere (Right)", value=0.0),
        'cylinder': st.number_input("Cylinder (Right)", value=0.0),
        'k1': st.number_input("K1 (Right)", value=46.0),
        'k2': st.number_input("K2 (Right)", value=48.0),
        'kmax': st.number_input("Kmax (Right)", value=48.0),
        'pachy': st.number_input("Pachymetry (Right)", value=480),
        'bcva': st.number_input("BCVA (Right)", value=0.5),
        'cone_distribution': st.selectbox("Cone Distribution (Right)", [
            "100 % cone on one side",
            "80 % :20 % ",
            "60 % :40 % ",
            "50 % :50 % "
        ]),
        'age': age
    }

if st.button("Generate Management Plan"):
    left_plan = process_eye_data(left_eye, df_nomogram)
    right_plan = process_eye_data(right_eye, df_nomogram)
    fruste = detect_form_fruste(left_eye, right_eye)

    st.subheader("📋 Management Plan")

    cols = st.columns(2)
    with cols[0]:
        st.markdown("#### Right Eye")
        for line in right_plan:
            st.write("-", line)
    with cols[1]:
        st.markdown("#### Left Eye")
        for line in left_plan:
            st.write("-", line)

    if fruste:
        st.markdown("---")
        st.markdown("⚠️ **Form fruste keratoconus detected in one eye — high risk of progression. CXL advised if eligible.**")

    # PDF export
    pdf = generate_pdf_summary(left_plan, right_plan, fruste)
    pdf.output("keratoconus_report.pdf")
    with open("keratoconus_report.pdf", "rb") as f:
        st.download_button("Download PDF Report", f, file_name="keratoconus_report.pdf")

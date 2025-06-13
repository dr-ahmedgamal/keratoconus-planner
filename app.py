# app.py
import streamlit as st
from logic import load_icrs_nomogram, process_eye_data

st.set_page_config(page_title="Keratoconus Management Planner", layout="wide")
st.title("Keratoconus Management Planning App")

nomogram_df = load_icrs_nomogram()

st.markdown("### Enter Patient Data for Both Eyes")

cols = st.columns(2)

def eye_inputs(label_prefix, col):
    with col:
        st.subheader(f"{label_prefix} Eye")
        age = st.number_input(f"{label_prefix} Age", min_value=10, max_value=80, value=25)
        sphere = st.number_input(f"{label_prefix} Sphere (D)", value=-3.0, step=0.25)
        cylinder = st.number_input(f"{label_prefix} Cylinder (D)", value=-2.0, step=0.25)
        k1 = st.number_input(f"{label_prefix} K1 (D)", value=42.0, step=0.1)
        k2 = st.number_input(f"{label_prefix} K2 (D)", value=47.0, step=0.1)
        kmax = st.number_input(f"{label_prefix} Kmax (D)", value=49.0, step=0.1)
        pachy = st.number_input(f"{label_prefix} Pachymetry (µm)", value=480)
        bcva = st.number_input(f"{label_prefix} BCVA (0–1.0)", min_value=0.0, max_value=1.0, step=0.05, value=0.8)
        cone_distribution = st.selectbox(
            f"{label_prefix} Cone Distribution Relative to Steep Meridian",
            ["100 cone on one side", "80:20", "60:40", "50:50"]
        )
    return age, sphere, cylinder, k1, k2, kmax, pachy, bcva, cone_distribution

left_eye_data = eye_inputs("Left", cols[0])
right_eye_data = eye_inputs("Right", cols[1])

if st.button("Generate Management Plan"):
    st.subheader("Management Plan Summary")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Left Eye Plan")
        left_results = process_eye_data(*left_eye_data, nomogram_df)
        for line in left_results:
            st.write("-", line)

    with col2:
        st.markdown("#### Right Eye Plan")
        right_results = process_eye_data(*right_eye_data, nomogram_df)
        for line in right_results:
            st.write("-", line)

st.markdown("""
---
*This app uses detailed staging, risk assessment, and full ICRS nomograms to guide keratoconus treatment including CXL, ICRS, PRK, and IOL combinations.*
""")

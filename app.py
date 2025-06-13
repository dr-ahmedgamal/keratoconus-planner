# app.py
import streamlit as st
import pandas as pd
from logic import process_eye_data, load_icrs_nomogram

st.set_page_config(page_title="Keratoconus Planner", layout="wide")
st.title("🌐 Keratoconus Management Planning Tool")

# Load nomogram
nomogram_df = load_icrs_nomogram()

st.sidebar.header("🌐 Patient Information")
age = st.sidebar.number_input("Age", min_value=10, max_value=90, value=25)

st.header("👁️ Right Eye (OD)")
with st.form("right_eye_form"):
    col1, col2, col3 = st.columns(3)
    with col1:
        sphere_od = st.number_input("Sphere (OD)", -20.0, 20.0, step=0.25)
        cylinder_od = st.number_input("Cylinder (OD)", -8.0, 8.0, step=0.25)
        bcva_od = st.slider("BCVA (OD)", 0.1, 1.0, 0.8)
    with col2:
        k1_od = st.number_input("K1 (OD)", 30.0, 55.0, step=0.1)
        k2_od = st.number_input("K2 (OD)", 30.0, 70.0, step=0.1)
        kmax_od = st.number_input("Kmax (OD)", 30.0, 80.0, step=0.1)
    with col3:
        pachy_od = st.number_input("Pachymetry (OD, µm)", 300, 700, step=1)
        cone_type_od = st.selectbox("Cone Asymmetry Type (OD)", [1, 2, 3, 4])
        cone_site_od = st.text_input("Cone site (OD)", "Central")
    submitted_od = st.form_submit_button("Process Right Eye")

st.header("👁️ Left Eye (OS)")
with st.form("left_eye_form"):
    col1, col2, col3 = st.columns(3)
    with col1:
        sphere_os = st.number_input("Sphere (OS)", -20.0, 20.0, step=0.25)
        cylinder_os = st.number_input("Cylinder (OS)", -8.0, 8.0, step=0.25)
        bcva_os = st.slider("BCVA (OS)", 0.1, 1.0, 0.8)
    with col2:
        k1_os = st.number_input("K1 (OS)", 30.0, 55.0, step=0.1)
        k2_os = st.number_input("K2 (OS)", 30.0, 70.0, step=0.1)
        kmax_os = st.number_input("Kmax (OS)", 30.0, 80.0, step=0.1)
    with col3:
        pachy_os = st.number_input("Pachymetry (OS, µm)", 300, 700, step=1)
        cone_type_os = st.selectbox("Cone Asymmetry Type (OS)", [1, 2, 3, 4])
        cone_site_os = st.text_input("Cone site (OS)", "Central")
    submitted_os = st.form_submit_button("Process Left Eye")

if submitted_od:
    st.subheader("📉 Results for Right Eye")
    results_od = process_eye_data(age, sphere_od, cylinder_od, k1_od, k2_od, kmax_od, pachy_od, bcva_od, cone_type_od, nomogram_df)
    for line in results_od:
        st.markdown(f"- {line}")

if submitted_os:
    st.subheader("📉 Results for Left Eye")
    results_os = process_eye_data(age, sphere_os, cylinder_os, k1_os, k2_os, kmax_os, pachy_os, bcva_os, cone_type_os, nomogram_df)
    for line in results_os:
        st.markdown(f"- {line}")

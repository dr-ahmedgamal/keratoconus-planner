import streamlit as st
import pandas as pd
from logic import load_icrs_nomogram, process_eye_data, generate_pdf_summary
import base64

st.set_page_config(page_title="Keratoconus Management Planner", layout="wide")
st.title("Keratoconus Management Planner")

st.markdown("### Enter Patient Data")

col_age, _ = st.columns([1, 5])
age = col_age.number_input("Patient Age", min_value=5, max_value=100, value=18)

# ✅ RIGHT EYE on the LEFT, LEFT EYE on the RIGHT
col_right_eye, col_left_eye = st.columns(2)

with col_right_eye:
    st.subheader("Right Eye")
    sphere_r = st.number_input("Sphere (R)", value=0.0, key="sphere_r", step=0.25)
    cylinder_r = st.number_input("Cylinder (R)", value=0.0, key="cylinder_r", step=0.25)
    k1_r = st.number_input("K1 (R)", value=46.0, key="k1_r", step=0.1)
    k2_r = st.number_input("K2 (R)", value=48.0, key="k2_r", step=0.1)
    kmax_r = st.number_input("Kmax (R)", value=48.0, key="kmax_r", step=0.1)
    pachy_r = st.number_input("Pachymetry (R)", value=480, key="pachy_r")
    bcva_r = st.number_input("BCVA (R)", value=0.5, step=0.1, key="bcva_r")
    cone_dist_r = st.selectbox("Cone Distribution vs Steep Axis (R)", [
        "100 % cone on one side",
        "80 % :20 % ",
        "60 % :40 % ",
        "50 % :50 % "
    ], key="cone_r")

with col_left_eye:
    st.subheader("Left Eye")
    sphere_l = st.number_input("Sphere (L)", value=0.0, key="sphere_l", step=0.25)
    cylinder_l = st.number_input("Cylinder (L)", value=0.0, key="cylinder_l", step=0.25)
    k1_l = st.number_input("K1 (L)", value=46.0, key="k1_l", step=0.1)
    k2_l = st.number_input("K2 (L)", value=48.0, key="k2_l", step=0.1)
    kmax_l = st.number_input("Kmax (L)", value=48.0, key="kmax_l", step=0.1)
    pachy_l = st.number_input("Pachymetry (L)", value=480, key="pachy_l")
    bcva_l = st.number_input("BCVA (L)", value=0.5, step=0.1, key="bcva_l")
    cone_dist_l = st.selectbox("Cone Distribution vs Steep Axis (L)", [
        "100 % cone on one side",
        "80 % :20 % ",
        "60 % :40 % ",
        "50 % :50 % "
    ], key="cone_l")

# ✅ On click, generate plans and PDF
if st.button("Generate Management Plan"):
    nomogram_df = load_icrs_nomogram()

    right_eye = {
        'age': age,
        'sphere': sphere_r,
        'cylinder': cylinder_r,
        'k1': k1_r,
        'k2': k2_r,
        'kmax': kmax_r,
        'pachy': pachy_r,
        'bcva': bcva_r,
        'cone_distribution': cone_dist_r
    }

    left_eye = {
        'age': age,
        'sphere': sphere_l,
        'cylinder': cylinder_l,
        'k1': k1_l,
        'k2': k2_l,
        'kmax': kmax_l,
        'pachy': pachy_l,
        'bcva': bcva_l,
        'cone_distribution': cone_dist_l
    }

    right_plan = process_eye_data(right_eye, nomogram_df)
    left_plan = process_eye_data(left_eye, nomogram_df)

    st.markdown("### Recommended Management Plan")

    col_r, col_l = st.columns(2)
    with col_r:
        st.markdown("**Right Eye:**")
        for line in right_plan:
            st.write("-", line)

    with col_l:
        st.markdown("**Left Eye:**")
        for line in left_plan:
            st.write("-", line)

    # ✅ Generate PDF Summary
    pdf = generate_pdf_summary(left_plan, right_plan)

    try:
        pdf_output = pdf.output(dest='S').encode('latin1')
        st.download_button(
            label="Download PDF Summary",
            data=pdf_output,
            file_name="keratoconus_plan.pdf",
            mime="application/pdf"
        )
    except Exception as e:
        st.error(f"❌ PDF generation failed: {e}")

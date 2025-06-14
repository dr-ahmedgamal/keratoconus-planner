# app.py
import streamlit as st
from logic import load_icrs_nomogram, process_eye_data, generate_pdf_summary

st.set_page_config(page_title="Keratoconus Management Tool", layout="centered")
st.title("Keratoconus Management Planning Tool")

st.markdown("### Enter Right Eye Data")
right_eye = {
    'age': st.number_input("Age", min_value=0, max_value=120, key='age_r'),
    'sphere': st.number_input("Sphere (D)", key='sphere_r'),
    'cylinder': st.number_input("Cylinder (D)", key='cylinder_r'),
    'k1': st.number_input("K1 (D)", key='k1_r'),
    'k2': st.number_input("K2 (D)", key='k2_r'),
    'kmax': st.number_input("Kmax (D)", key='kmax_r'),
    'pachy': st.number_input("Pachymetry (\u00b5m)", key='pachy_r'),
    'bcva': st.text_input("BCVA", key='bcva_r'),
    'cone_distribution': st.selectbox("Cone Distribution", [
        "100 % cone on one side",
        "80 % :20 % ",
        "60 % :40 % ",
        "50 % :50 % "
    ], key='cone_dist_r')
}

st.markdown("### Enter Left Eye Data")
left_eye = {
    'age': st.number_input("Age", min_value=0, max_value=120, key='age_l'),
    'sphere': st.number_input("Sphere (D)", key='sphere_l'),
    'cylinder': st.number_input("Cylinder (D)", key='cylinder_l'),
    'k1': st.number_input("K1 (D)", key='k1_l'),
    'k2': st.number_input("K2 (D)", key='k2_l'),
    'kmax': st.number_input("Kmax (D)", key='kmax_l'),
    'pachy': st.number_input("Pachymetry (\u00b5m)", key='pachy_l'),
    'bcva': st.text_input("BCVA", key='bcva_l'),
    'cone_distribution': st.selectbox("Cone Distribution", [
        "100 % cone on one side",
        "80 % :20 % ",
        "60 % :40 % ",
        "50 % :50 % "
    ], key='cone_dist_l')
}

if st.button("Generate Management Plan"):
    nomogram_df = load_icrs_nomogram()
    right_plan = process_eye_data(right_eye, nomogram_df)
    left_plan = process_eye_data(left_eye, nomogram_df)

    st.subheader("Right Eye Plan")
    for item in right_plan:
        st.write(f"- {item}")

    st.subheader("Left Eye Plan")
    for item in left_plan:
        st.write(f"- {item}")

    if st.button("Download PDF Report"):
        pdf = generate_pdf_summary(right_plan, left_plan)
        pdf.output("keratoconus_plan.pdf")
        with open("keratoconus_plan.pdf", "rb") as f:
            st.download_button("Download PDF", data=f, file_name="keratoconus_plan.pdf")

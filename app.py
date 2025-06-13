# app.py
import streamlit as st
from logic import load_icrs_nomogram, process_eye_data, detect_form_fruste, generate_pdf_summary
import tempfile

st.set_page_config(page_title="Keratoconus Management Planner", layout="wide")
st.title("Keratoconus Management Planning Tool")

st.markdown("**Cone location is specified relative to the steep meridian.**")

cone_options = ["100 cone on one side", "80:20", "60:40", "50:50"]

left, right = st.columns(2)

with left:
    st.header("Left Eye")
    left_eye = {
        'sphere': st.number_input("Sphere (D)", key="lsph", value=0.0),
        'cylinder': st.number_input("Cylinder (D)", key="lcyl", value=0.0),
        'k1': st.number_input("K1 (D)", key="lk1", value=46.0),
        'k2': st.number_input("K2 (D)", key="lk2", value=48.0),
        'kmax': st.number_input("K max (D)", key="lkmax", value=48.0),
        'pachy': st.number_input("Pachymetry (µm)", key="lpachy", value=480),
        'age': st.number_input("Age (years)", key="lage", value=18),
        'bcva': st.number_input("BCVA (decimal)", key="lbcva", value=0.5),
        'cone_distribution': st.selectbox("Cone site (asymmetry)", cone_options, key="lcone")
    }

with right:
    st.header("Right Eye")
    right_eye = {
        'sphere': st.number_input("Sphere (D)", key="rsph", value=0.0),
        'cylinder': st.number_input("Cylinder (D)", key="rcyl", value=0.0),
        'k1': st.number_input("K1 (D)", key="rk1", value=46.0),
        'k2': st.number_input("K2 (D)", key="rk2", value=48.0),
        'kmax': st.number_input("K max (D)", key="rkmax", value=48.0),
        'pachy': st.number_input("Pachymetry (µm)", key="rpachy", value=480),
        'age': st.number_input("Age (years)", key="rage", value=18),
        'bcva': st.number_input("BCVA (decimal)", key="rbcva", value=0.5),
        'cone_distribution': st.selectbox("Cone site (asymmetry)", cone_options, key="rcone")
    }

if st.button("Generate Management Plan"):
    nomogram_df = load_icrs_nomogram()
    left_plan = process_eye_data(left_eye, nomogram_df)
    right_plan = process_eye_data(right_eye, nomogram_df)

    form_fruste = detect_form_fruste(left_eye, right_eye)

    st.subheader("Management Recommendations")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Left Eye Plan:**")
        for line in left_plan:
            st.write(f"- {line}")

    with col2:
        st.markdown("**Right Eye Plan:**")
        for line in right_plan:
            st.write(f"- {line}")

    if form_fruste:
        st.warning("⚠️ Form fruste keratoconus detected in one eye. CXL advised if eligible.")

    pdf = generate_pdf_summary(left_plan, right_plan, form_fruste)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        pdf.output(tmp.name)
        st.download_button("📥 Download Management PDF", data=open(tmp.name, "rb").read(), file_name="keratoconus_plan.pdf")

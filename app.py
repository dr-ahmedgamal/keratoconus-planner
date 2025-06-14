# app.py
import streamlit as st
import pandas as pd
from logic import load_icrs_nomogram, process_eye_data, generate_pdf_summary
from fpdf import FPDF

# Page setup
st.set_page_config(page_title="Keratoconus Management Planner", layout="wide")
st.title("Keratoconus Management Planner")
st.markdown("### Enter Patient Data")

# All patient inputs vertically
age = st.number_input("Patient Age", min_value=5, max_value=100, value=18)
sphere = st.number_input("Sphere", value=0.0, step=0.25)
cylinder = st.number_input("Cylinder", value=0.0, step=0.25)
k1 = st.number_input("K1", value=46.0, step=0.1)
k2 = st.number_input("K2", value=48.0, step=0.1)
kmax = st.number_input("Kmax", value=48.0, step=0.1)
pachy = st.number_input("Pachymetry (µm)", value=480)
bcva = st.number_input("BCVA", value=0.5, step=0.1)
cone_dist = st.selectbox("Cone Distribution vs Steep Axis", [
    "100 % cone on one side", "80 % :20 % ", "60 % :40 % ", "50 % :50 % "
])
scarring = st.checkbox("Corneal Scarring Present", value=False)

# Submit button centered and enlarged
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("🔍 Generate Management Plan", use_container_width=True):
        nomogram_df = load_icrs_nomogram()

        eye_data = {
            'age': age,
            'sphere': sphere,
            'cylinder': cylinder,
            'k1': k1,
            'k2': k2,
            'kmax': kmax,
            'pachy': pachy,
            'bcva': bcva,
            'cone_distribution': cone_dist,
            'scarring': scarring
        }

        plan = process_eye_data(eye_data, nomogram_df)

        # Show output
        st.markdown("### Recommended Management Plan")
        for line in plan:
            st.write("-", line)

        # PDF generation
        pdf = generate_pdf_summary(plan, [])
        try:
            pdf_string = pdf.output(dest='S').encode('latin1')
            st.download_button(
                label="📄 Download PDF Summary",
                data=pdf_string,
                file_name="keratoconus_plan.pdf",
                mime="application/pdf"
            )
        except Exception as e:
            st.error("❌ PDF generation failed. Please check input values.")


import streamlit as st
from logic import load_icrs_nomogram, process_eye_data, detect_form_fruste, generate_pdf_summary

st.set_page_config(page_title="Keratoconus Management App", layout="wide")

st.title("Keratoconus Management Planning Tool")

nomogram_df = load_icrs_nomogram()

with st.form("kc_form"):
    st.subheader("Enter Patient Data")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Left Eye")
        left_eye = {
            "age": st.number_input("Age", value=18, min_value=10, max_value=100, key="age_l"),
            "sphere": st.number_input("Sphere (D)", value=0.0, key="sphere_l"),
            "cylinder": st.number_input("Cylinder (D)", value=0.0, key="cyl_l"),
            "k1": st.number_input("K1 (D)", value=46.0, key="k1_l"),
            "k2": st.number_input("K2 (D)", value=48.0, key="k2_l"),
            "kmax": st.number_input("Kmax (D)", value=48.0, key="kmax_l"),
            "pachy": st.number_input("Pachymetry (µm)", value=480, key="pachy_l"),
            "bcva": st.number_input("BCVA", value=0.5, min_value=0.0, max_value=1.2, step=0.05, key="bcva_l"),
            "cone_distribution": st.selectbox("Cone position vs steep axis", 
                ["100 % cone on one side", "80 % :20 % ", "60 % :40 % ", "50 % :50 % "], key="dist_l")
        }

    with col2:
        st.markdown("### Right Eye")
        right_eye = {
            "age": st.number_input("Age ", value=18, min_value=10, max_value=100, key="age_r"),
            "sphere": st.number_input("Sphere (D) ", value=0.0, key="sphere_r"),
            "cylinder": st.number_input("Cylinder (D) ", value=0.0, key="cyl_r"),
            "k1": st.number_input("K1 (D) ", value=46.0, key="k1_r"),
            "k2": st.number_input("K2 (D) ", value=48.0, key="k2_r"),
            "kmax": st.number_input("Kmax (D) ", value=48.0, key="kmax_r"),
            "pachy": st.number_input("Pachymetry (µm) ", value=480, key="pachy_r"),
            "bcva": st.number_input("BCVA ", value=0.5, min_value=0.0, max_value=1.2, step=0.05, key="bcva_r"),
            "cone_distribution": st.selectbox("Cone position vs steep axis ", 
                ["100 % cone on one side", "80 % :20 % ", "60 % :40 % ", "50 % :50 % "], key="dist_r")
        }

    submitted = st.form_submit_button("Analyze")

if submitted:
    st.subheader("🧠 Management Recommendations")

    left_plan = process_eye_data(left_eye, nomogram_df)
    right_plan = process_eye_data(right_eye, nomogram_df)
    form_fruste_flag = detect_form_fruste(left_eye, right_eye)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Left Eye Plan")
        for item in left_plan:
            st.write("🔹", item)

    with col2:
        st.markdown("#### Right Eye Plan")
        for item in right_plan:
            st.write("🔹", item)

    if form_fruste_flag:
        st.markdown("### ⚠️ Form Fruste Keratoconus Detected")
        st.warning("One eye shows subclinical keratoconus with risk of progression. CXL advised if eligible.")

    pdf = generate_pdf_summary(left_plan, right_plan, form_fruste_flag)
    pdf_path = "/mnt/data/keratoconus_plan.pdf"
    pdf.output(pdf_path)
    with open(pdf_path, "rb") as f:
        st.download_button("📄 Download PDF Report", f, file_name="keratoconus_plan.pdf")

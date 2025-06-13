# app.py
import streamlit as st
from logic import load_icrs_nomogram, process_eye_data, detect_form_fruste
from io import StringIO
import base64

st.set_page_config(page_title="Keratoconus Management Planner", layout="wide")
st.title("Keratoconus Management Planning App")

nomogram_df = load_icrs_nomogram()

st.markdown("### Enter Patient Data for Both Eyes")

cols = st.columns(2)

def eye_inputs(label_prefix, col):
    with col:
        st.subheader(f"{label_prefix} Eye")
        age = st.number_input(f"{label_prefix} Age", min_value=10, max_value=80, value=18)
        sphere = st.number_input(f"{label_prefix} Sphere (D)", value=0.0, step=0.25)
        cylinder = st.number_input(f"{label_prefix} Cylinder (D)", value=0.0, step=0.25)
        k1 = st.number_input(f"{label_prefix} K1 (D)", value=46.0, step=0.1)
        k2 = st.number_input(f"{label_prefix} K2 (D)", value=48.0, step=0.1)
        kmax = st.number_input(f"{label_prefix} Kmax (D)", value=48.0, step=0.1)
        pachy = st.number_input(f"{label_prefix} Pachymetry (µm)", value=480)
        bcva = st.number_input(f"{label_prefix} BCVA (0–1.0)", min_value=0.0, max_value=1.0, step=0.05, value=0.5)
        cone_distribution = st.selectbox(
            f"{label_prefix} Cone Distribution Relative to Steep Meridian (cone location is defined relative to the steep axis)",
            ["100 cone on one side", "80:20", "60:40", "50:50"]
        )
    return {
        'age': age,
        'sphere': sphere,
        'cylinder': cylinder,
        'k1': k1,
        'k2': k2,
        'kmax': kmax,
        'pachy': pachy,
        'bcva': bcva,
        'cone_distribution': cone_distribution
    }

left_eye = eye_inputs("Left", cols[0])
right_eye = eye_inputs("Right", cols[1])

if st.button("Generate Management Plan"):
    st.subheader("Management Plan Summary")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Left Eye Plan")
        left_results = process_eye_data(left_eye, nomogram_df)
        for line in left_results:
            st.write("-", line)

    with col2:
        st.markdown("#### Right Eye Plan")
        right_results = process_eye_data(right_eye, nomogram_df)
        for line in right_results:
            st.write("-", line)

    # Check for form fruste keratoconus
    form_fruste = detect_form_fruste(left_eye, right_eye)
    if form_fruste:
        st.warning("⚠️ Form fruste keratoconus detected in one eye: Recommend careful monitoring and possible CXL.")

    # Generate PDF-like text for download
    summary = StringIO()
    summary.write("Keratoconus Management Report\n\n")
    summary.write("LEFT EYE:\n")
    for line in left_results:
        summary.write(f"- {line}\n")
    summary.write("\nRIGHT EYE:\n")
    for line in right_results:
        summary.write(f"- {line}\n")
    if form_fruste:
        summary.write("\n⚠️ Form fruste keratoconus detected in one eye. High risk of progression. CXL advised if eligible.\n")

    content = summary.getvalue()
    b64 = base64.b64encode(content.encode()).decode()
    href = f'<a href="data:file/txt;base64,{b64}" download="keratoconus_plan.txt">📄 Download Summary as Text File</a>'
    st.markdown(href, unsafe_allow_html=True)

st.markdown("""
---
*This app uses detailed staging, progression risk, and asymmetry-based ICRS nomograms to generate personalized keratoconus treatment plans including CXL, ICRS, PRK, and IOL strategies.*
""")

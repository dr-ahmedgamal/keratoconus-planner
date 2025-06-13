# logic.py
import pandas as pd
from fpdf import FPDF

def load_icrs_nomogram():
    return pd.read_csv("icrs_nomograms.csv")

def get_asymmetry_type(cone_distribution):
    mapping = {
        "100 % cone on one side": "Type 1",
        "80 % :20 % ": "Type 2",
        "60 % :40 % ": "Type 3",
        "50 % :50 % ": "Type 4"
    }
    return mapping.get(cone_distribution, "Type 1")

def find_icrs_recommendation(sphere, cylinder, asymmetry_type, nomogram_df):
    if sphere < -10:
        if cylinder < -2:
            return "ICRS 340/300 + IOL for residual error"
        else:
            return "Recommend Phakic or Pseudophakic IOL"
    elif -10 <= sphere < -8:
        return "ICRS 340/300"
    else:
        filtered = nomogram_df[
            (nomogram_df['Type'] == asymmetry_type) &
            (nomogram_df['Sphere'] == int(round(sphere))) &
            (nomogram_df['Cylinder'] == int(round(abs(cylinder))))
        ]
        if not filtered.empty:
            return filtered.iloc[0]['Recommendation']
        else:
            return "No exact match found in nomogram"

def process_eye_data(eye_data, nomogram_df):
    age = eye_data['age']
    sphere = eye_data['sphere']
    cylinder = eye_data['cylinder']
    k1 = eye_data['k1']
    k2 = eye_data['k2']
    kmax = eye_data['kmax']
    pachy = eye_data['pachy']
    bcva = eye_data['bcva']
    cone_dist = eye_data['cone_distribution']

    asymmetry_type = get_asymmetry_type(cone_dist)
    plan = []

    # CXL default if age < 40
    if age < 40:
        plan.append("CXL indicated (age < 40)")

    # Add ICRS if sphere and pachy eligible
    if pachy >= 350 and abs(sphere) >= 1:
        icrs = find_icrs_recommendation(sphere, cylinder, asymmetry_type, nomogram_df)
        if "340/300 + IOL" in icrs:
            plan.append("ICRS recommendation: 340/300")
            plan.append("Followed by: IOL for residual myopia")
        elif "340/300" in icrs:
            plan.append("ICRS recommendation: 340/300")
            plan.append("Followed by: Consider IOL for residual myopia")
        elif "IOL" in icrs:
            plan.append(icrs)
        elif "not suitable" in icrs.lower():
            plan.append("ICRS not suitable")
        else:
            plan.append(f"ICRS recommendation: {icrs}")

    # PRK if BCVA < 1.0 and within topographic range
    if bcva <= 1.0 and kmax < 55:
        plan.append("PRK + CXL recommended (BCVA improvement expected)")

    # Glasses or RGP lenses always an option
    plan.append("Glasses or RGP lenses as initial management")

    return plan

def detect_form_fruste(eye1, eye2):
    def is_frank_kc(eye):
        return eye['kmax'] >= 50 or eye['pachy'] < 460

    def is_suspicious(eye):
        return 47 <= eye['kmax'] < 50 or 460 <= eye['pachy'] < 500

    return (
        (is_frank_kc(eye1) and is_suspicious(eye2)) or
        (is_frank_kc(eye2) and is_suspicious(eye1))
    )

def generate_pdf_summary(left_plan, right_plan, form_fruste_detected):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="Keratoconus Management Report", ln=True, align="C")
    pdf.ln(10)

    pdf.set_font("Arial", style="B", size=12)
    pdf.cell(200, 10, txt="Left Eye Plan:", ln=True)
    pdf.set_font("Arial", size=12)
    for line in left_plan:
        pdf.cell(200, 10, txt=f"- {line}", ln=True)

    pdf.ln(5)
    pdf.set_font("Arial", style="B", size=12)
    pdf.cell(200, 10, txt="Right Eye Plan:", ln=True)
    pdf.set_font("Arial", size=12)
    for line in right_plan:
        pdf.cell(200, 10, txt=f"- {line}", ln=True)

    if form_fruste_detected:
        pdf.ln(10)
        pdf.set_font("Arial", style="B", size=12)
        pdf.set_text_color(220, 50, 50)
        pdf.multi_cell(0, 10, txt="⚠️ Form fruste keratoconus detected in one eye. High risk of progression. CXL advised if eligible.")

    pdf.set_text_color(0, 0, 0)
    return pdf

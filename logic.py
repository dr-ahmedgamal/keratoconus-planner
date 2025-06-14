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
        return "ICRS 340/300 + IOL for residual error"
    elif -10 <= sphere < -8:
        return "ICRS 340/300"
    elif -8 <= sphere <= 3:
        filtered = nomogram_df[
            (nomogram_df['Type'] == asymmetry_type) &
            (nomogram_df['Sphere'] == int(round(sphere))) &
            (nomogram_df['Cylinder'] == int(round(abs(cylinder))))
        ]
        if not filtered.empty:
            return filtered.iloc[0]['Recommendation']
        else:
            return "No exact match found in nomogram"
    else:
        return "ICRS not suitable"

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

    # Glasses or Contact Lenses (always offered)
    plan.append("Glasses or RGP contact lenses as initial management")

    # PRK (only if Sphere + Cylinder < 4 and pachy >= 450)
    prk_eligible = (sphere + cylinder) < 4 and pachy >= 450
    if prk_eligible:
        plan.append("PRK recommended")
        plan.append("CXL should follow PRK in same session")

    # ICRS (if sphere within range and pachy >= 350)
    if pachy >= 350 and abs(sphere) >= 1:
        icrs = find_icrs_recommendation(sphere, cylinder, asymmetry_type, nomogram_df)
        if "340/300 + IOL" in icrs:
            plan.append("ICRS recommendation: 340/300")
            plan.append("Followed by: IOL for residual myopia")
        elif "340/300" in icrs:
            plan.append("ICRS recommendation: 340/300")
        elif "IOL" in icrs:
            plan.append(icrs)
        elif "not suitable" in icrs.lower():
            plan.append("ICRS not suitable")
        elif "No exact match" in icrs:
            plan.append("ICRS: No exact match in nomogram")
        else:
            plan.append(f"ICRS recommendation: {icrs}")

    # CXL (if age < 40 or PRK offered)
    if age < 40 or prk_eligible:
        plan.append("CXL recommended")

    # IOL (if sphere > 10 and cylinder < 2)
    if abs(sphere) > 10:
        if abs(cylinder) <= 2:
            plan.append("Phakic/Pseudophakic IOL indicated (high spherical error)")
        else:
            plan.append("Phakic/Pseudophakic IOL + ICRS to correct residual cylinder")

    return plan

def generate_pdf_summary(right_plan, left_plan):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Helvetica", size=12)

    pdf.set_font(style="B")
    pdf.cell(0, 10, txt="Keratoconus Management Report", ln=True, align="C")
    pdf.ln(10)

    pdf.set_font(style="B")
    pdf.cell(0, 10, txt="Right Eye Plan:", ln=True)
    pdf.set_font(style="")
    for line in right_plan:
        safe_line = str(line).replace("⚠️", "WARNING:")
        pdf.multi_cell(w=180, h=8, txt=f"- {safe_line}", align='L')

    pdf.ln(5)
    pdf.set_font(style="B")
    pdf.cell(0, 10, txt="Left Eye Plan:", ln=True)
    pdf.set_font(style="")
    for line in left_plan:
        safe_line = str(line).replace("⚠️", "WARNING:")
        pdf.multi_cell(w=180, h=8, txt=f"- {safe_line}", align='L')

    return pdf

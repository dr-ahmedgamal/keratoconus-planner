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
    # Normalize inputs
    cylinder = abs(cylinder)
    rounded_sphere = int(round(sphere))
    rounded_cylinder = int(round(cylinder))

    if rounded_sphere < -10:
        if rounded_cylinder > 2:
            return "ICRS 340/300 + IOL for residual error"
        else:
            return "Recommend Phakic or Pseudophakic IOL"
    elif -10 <= rounded_sphere < -8:
        return "ICRS 340/300"
    else:
        filtered = nomogram_df[
            (nomogram_df['Type'] == asymmetry_type) &
            (nomogram_df['Sphere'] == rounded_sphere) &
            (nomogram_df['Cylinder'] == rounded_cylinder)
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

    if age < 40:
        plan.append("CXL indicated (age < 40)")

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

    if bcva <= 1.0 and kmax < 55:
        plan.append("PRK + CXL recommended (BCVA improvement expected)")

    plan.append("Glasses or RGP lenses as initial management")

    return plan

def generate_pdf_summary(left_plan, right_plan):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Helvetica", size=12)

    # Title
    pdf.set_font("Helvetica", style="B", size=14)
    pdf.cell(0, 10, txt="Keratoconus Management Report", ln=True, align="C")
    pdf.ln(10)

    # Right Eye Plan
    pdf.set_font("Helvetica", style="B", size=12)
    pdf.cell(0, 10, txt="Right Eye Plan:", ln=True)
    pdf.set_font("Helvetica", size=12)
    for line in right_plan:
        safe_line = str(line).replace("⚠️", "WARNING:")
        pdf.multi_cell(w=0, h=8, txt=f"- {safe_line}", align='L')

    pdf.ln(5)

    # Left Eye Plan
    pdf.set_font("Helvetica", style="B", size=12)
    pdf.cell(0, 10, txt="Left Eye Plan:", ln=True)
    pdf.set_font("Helvetica", size=12)
    for line in left_plan:
        safe_line = str(line).replace("⚠️", "WARNING:")
        pdf.multi_cell(w=0, h=8, txt=f"- {safe_line}", align='L')

    return pdf

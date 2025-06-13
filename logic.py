# logic.py
import pandas as pd

def load_icrs_nomogram():
    return pd.read_csv("icrs_nomograms.csv")

def get_asymmetry_type(cone_distribution):
    mapping = {
        "100 cone on one side": "Type 1",
        "80:20": "Type 2",
        "60:40": "Type 3",
        "50:50": "Type 4"
    }
    return mapping.get(cone_distribution, "Type 1")

def find_icrs_recommendation(sphere, cylinder, asymmetry_type, nomogram_df):
    if sphere < -10:
        return "Not recommended (sphere exceeds nomogram limits)"
    elif -10 <= sphere < -8:
        return "ICRS 340/300 + consider IOL for residual myopia"
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
    if 350 <= pachy <= 500 and abs(sphere) >= 1:
        icrs = find_icrs_recommendation(sphere, cylinder, asymmetry_type, nomogram_df)
        if "IOL" in icrs:
            plan.append("ICRS implantation recommended")
            plan.append("Followed by: Phakic or pseudophakic IOL for residual myopia")
        elif "not recommended" in icrs.lower():
            plan.append("ICRS not suitable")
        else:
            plan.append(f"ICRS recommendation: {icrs}")

    # PRK if BCVA < 1.0 and within topographic range
    if bcva < 1.0 and kmax < 55:
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

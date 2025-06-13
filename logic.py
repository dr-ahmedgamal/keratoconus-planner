# logic.py
import pandas as pd

def load_icrs_nomogram():
    path = "icrs_nomograms.csv"
    try:
        return pd.read_csv(path)
    except:
        return pd.DataFrame()

def calculate_se(sphere, cylinder):
    return sphere + (cylinder / 2)

def calculate_kavg(k1, k2):
    return (k1 + k2) / 2

def determine_stage(kmax, pachy, bcva):
    if kmax <= 47 and pachy > 500 and bcva >= 0.8:
        return "Stage 1"
    elif 47 < kmax <= 52 and pachy > 450:
        return "Stage 2"
    elif 52 < kmax <= 55 and pachy > 400:
        return "Stage 3"
    else:
        return "Stage 4"

def is_progressive(age, bcva, kmax):
    return age < 30 or bcva < 0.6 or kmax > 53

def is_subclinical(kmax, pachy, bcva):
    return kmax < 48 and pachy > 500 and bcva >= 0.9

def icrs_eligibility(stage, sphere, cylinder, pachy, kmax):
    return (
        stage in ["Stage 1", "Stage 2", "Stage 3"] and
        -10 <= sphere <= -1 and
        1 <= abs(cylinder) <= 8 and
        350 <= pachy <= 500 and
        kmax <= 65
    )

def recommend_icrs(nomogram_df, cone_type, sphere, cylinder):
    if nomogram_df.empty:
        return "Nomogram data not loaded."

    try:
        match = nomogram_df[
            (nomogram_df['Type'] == cone_type) &
            (nomogram_df['Sphere'] == abs(int(sphere))) &
            (nomogram_df['Cylinder'] == abs(int(cylinder)))
        ]
        if not match.empty:
            val = match.iloc[0]['Segments']
            return f"Recommended ICRS: {val}"
        else:
            return "No exact match in nomogram. Consider expert review."
    except Exception as e:
        return f"Error using nomogram: {e}"

def process_eye_data(age, sphere, cylinder, k1, k2, kmax, pachy, bcva, cone_type, nomogram_df):
    results = []

    se = calculate_se(sphere, cylinder)
    kavg = calculate_kavg(k1, k2)
    stage = determine_stage(kmax, pachy, bcva)
    progressive = is_progressive(age, bcva, kmax)
    subclinical = is_subclinical(kmax, pachy, bcva)

    results.append(f"Stage: {stage}")
    if progressive:
        results.append("Signs of progression: YES")
    else:
        results.append("Signs of progression: NO")

    if subclinical:
        if progressive:
            results.append("Subclinical keratoconus with risk of progression → Recommend prophylactic CXL")
        else:
            results.append("Subclinical keratoconus without progression → Observation or optional CXL")
    else:
        if age < 40:
            results.append("Age < 40 → CXL recommended if progressive")
        if stage == "Stage 1":
            results.append("Consider: Glasses / RGP Lenses / ICRS ± CXL")
        elif stage == "Stage 2":
            results.append("Consider: ICRS ± CXL, PRK+CXL if stable")
        elif stage == "Stage 3":
            results.append("Consider: ICRS+CXL, Phakic IOL if stable, PRK+CXL rarely")
        elif stage == "Stage 4":
            results.append("Consider: DALK / PKP, or ICL if optical zone is clear")

    if icrs_eligibility(stage, sphere, cylinder, pachy, kmax):
        icrs_plan = recommend_icrs(nomogram_df, cone_type, sphere, cylinder)
        results.append(icrs_plan)
    else:
        results.append("Not a candidate for ICRS based on criteria")

    return results

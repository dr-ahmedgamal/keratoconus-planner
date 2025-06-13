# logic.py
import pandas as pd

def load_icrs_nomogram():
    path = "icrs_nomograms.csv"  # ensure file name is correct and placed properly
    try:
        df = pd.read_csv(path)
        df['Type'] = df['Type'].astype(str).str.strip()  # normalize for matching
        return df
    except Exception as e:
        print(f"Failed to load nomogram: {e}")
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

def map_cone_distribution_to_type(distribution):
    mapping = {
        "100 cone on one side": "1",
        "80:20": "2",
        "60:40": "3",
        "50:50": "4"
    }
    return mapping.get(distribution, "")

def recommend_icrs(nomogram_df, cone_distribution, sphere, cylinder):
    if nomogram_df.empty:
        return "Nomogram data not loaded."

    cone_type = map_cone_distribution_to_type(cone_distribution)
    if not cone_type:
        return "Invalid cone distribution type."

    try:
        abs_sphere = abs(int(sphere))
        abs_cylinder = abs(int(cylinder))

        match = nomogram_df[
            (nomogram_df['Type'] == cone_type) &
            (nomogram_df['Sphere'] == abs_sphere) &
            (nomogram_df['Cylinder'] == abs_cylinder)
        ]

        if not match.empty:
            val = match.iloc[0]['Segments']
            return f"Recommended ICRS: {val}"
        elif -10 <= sphere < -8:
            return "Recommended ICRS: 340/300 (off-nomogram correction for high myopia)"
        else:
            return "No exact match in nomogram. Consider expert review."
    except Exception as e:
        return f"Error using nomogram: {e}"

def process_eye_data(age, sphere, cylinder, k1, k2, kmax, pachy, bcva, cone_distribution, nomogram_df):
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
        cxl_needed = age < 40 or progressive

        if stage == "Stage 1":
            plan = "Consider: Glasses / RGP Lenses"
            if icrs_eligibility(stage, sphere, cylinder, pachy, kmax):
                plan += " / ICRS"
            if cxl_needed:
                plan += " + CXL"
            results.append(plan)

        elif stage == "Stage 2":
            plan = "Consider: "
            if icrs_eligibility(stage, sphere, cylinder, pachy, kmax):
                plan += "ICRS + CXL, "
            plan += "PRK + CXL"
            results.append(plan)

        elif stage == "Stage 3":
            plan = "Consider: "
            if icrs_eligibility(stage, sphere, cylinder, pachy, kmax):
                if abs(sphere) > 10:
                    plan += "ICRS followed by IOL for residual correction"
                else:
                    plan += "ICRS + CXL"
            else:
                plan += "Phakic IOL"
            results.append(plan)

        elif stage == "Stage 4":
            results.append("Consider: DALK / PKP, or ICL if optical zone is clear")

    if icrs_eligibility(stage, sphere, cylinder, pachy, kmax):
        icrs_plan = recommend_icrs(nomogram_df, cone_distribution, sphere, cylinder)
        results.append(icrs_plan)
    else:
        results.append("Not a candidate for ICRS based on criteria")

    return results

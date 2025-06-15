# logic.py
import pandas as pd
from fpdf import FPDF

# --- Load Nomogram ---
def load_icrs_nomogram():
    return pd.read_csv("icrs_nomograms.csv")

# --- Staging ---
def determine_stage(kmax, pachy, bcva):
    if pachy < 300 or kmax > 65 or bcva < 0.1:
        return "Stage 4"
    elif kmax > 60 or pachy < 400:
        return "Stage 3"
    elif kmax > 55 or pachy < 450:
        return "Stage 2"
    else:
        return "Stage 1"

# --- Eligibility Check Functions ---
def is_keratoplasty_indicated(pachy, kmax, scarring):
    return pachy < 300 or kmax > 65 or scarring

def is_prk_eligible(sphere, cylinder, pachy, scarring):
    total_error = sphere + cylinder
    return -4 <= total_error <= -1 and pachy >= 450 and not scarring

def is_icrs_eligible(sphere, cylinder, pachy, kmax, scarring):
    return (
        pachy >= 350 and
        1 <= abs(cylinder) <= 8 and
        kmax <= 65 and
        not scarring and
        -10 <= sphere <= 3
    )

def is_cxl_indicated(age, prk_eligible, icrs_eligible, pachy):
    return (age < 40 or prk_eligible or icrs_eligible) and pachy >= 350

def is_phakic_iol(age, sphere, cylinder):
    return age < 40 and sphere < -10 and abs(cylinder) <= 2

def is_phakic_iol_with_icrs(age, sphere, cylinder):
    return age < 40 and sphere < -10 and abs(cylinder) > 2

def is_pseudophakic_iol(age, sphere, cylinder):
    return age >= 40 and sphere < -10 and abs(cylinder) <= 2

def is_pseudophakic_iol_with_icrs(age, sphere, cylinder):
    return age >= 40 and sphere < -10 and abs(cylinder) > 2

# --- ICRS Recommendation Logic ---
def get_asymmetry_type(cone_distribution):
    mapping = {
        "100 % cone on one side": "Type 1",
        "80 % :20 % ": "Type 2",
        "60 % :40 % ": "Type 3",
        "50 % :50 % ": "Type 4"
    }
    return mapping.get(cone_distribution, "Type 1")

def find_icrs_recommendation(sphere, cylinder, asymmetry_type, nomogram_df, age, pachy, scarring):
    # Special case: Sphere -8 to -10 and Cylinder -1 to -3 → 340–355/300
    if -10 <= sphere <= -8 and -3 <= cylinder <= -1:
        return "ICRS 340–355/300"

    # Try standard nomogram usage for sphere -8 to +3
    if -10 <= sphere <= 3:
        filtered = nomogram_df[
            (nomogram_df['Type'] == asymmetry_type) &
            (nomogram_df['Sphere'] == int(round(min(sphere, -8)))) &
            (nomogram_df['Cylinder'] == int(round(min(abs(cylinder), 8))))
        ]
        if not filtered.empty:
            icrs_text = filtered.iloc[0]['Recommendation']
        else:
            icrs_text = "Maximal ICRS (from -8/-8)"

        # Calculate residual error beyond -8/-8 correction
        residual_sphere = sphere + 8
        residual_cylinder = cylinder + 8
        residual_total = residual_sphere + residual_cylinder

        residual_plan = []
        if -4 <= residual_total <= -1 and pachy >= 450 and not scarring:
            residual_plan.append("PRK for residual")
        elif residual_total < -10:
            if age < 40:
                residual_plan.append("Phakic IOL for residual")
            else:
                residual_plan.append("Pseudophakic IOL for residual")
        elif -10 <= residual_total < -4 and pachy >= 450 and not scarring:
            residual_plan.append("Consider PRK for partial residual")

        if residual_plan:
            return f"{icrs_text} + {' and '.join(residual_plan)}"
        else:
            return f"{icrs_text} + assess options for residual correction"

    # Sphere is out of range entirely → use max config and handle residual
    if sphere < -10 or sphere > 3:
        max_icrs = nomogram_df[
            (nomogram_df['Type'] == asymmetry_type) &
            (nomogram_df['Sphere'] == -8) &
            (nomogram_df['Cylinder'] == 8)
        ]
        icrs_text = (
            f"{max_icrs.iloc[0]['Recommendation']} (maximal ICRS for -8/-8)" if not max_icrs.empty
            else "Maximal ICRS (for -8/-8)"
        )

        residual_sphere = sphere + 8
        residual_cylinder = cylinder + 8
        residual_total = residual_sphere + residual_cylinder

        residual_plan = []
        if -4 <= residual_total <= -1 and pachy >= 450 and not scarring:
            residual_plan.append("PRK for residual")
        elif residual_total < -10:
            if age < 40:
                residual_plan.append("Phakic IOL for residual")
            else:
                residual_plan.append("Pseudophakic IOL for residual")
        elif -10 <= residual_total < -4 and pachy >= 450 and not scarring:
            residual_plan.append("Consider PRK for partial residual")

        if residual_plan:
            return f"{icrs_text} + {' and '.join(residual_plan)}"
        else:
            return f"{icrs_text} + assess options for residual correction"

    return "ICRS not suitable"




# --- Management Plan Generator ---
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
    scarring = eye_data.get('scarring', False)

    asymmetry_type = get_asymmetry_type(cone_dist)
    stage = determine_stage(kmax, pachy, bcva)
    plan = [f"Stage: {stage}"]

    # Step 1: Glasses/RGP
    plan.append("Glasses or RGP lenses as first-line management")

    # Step 2: Keratoplasty check
    if is_keratoplasty_indicated(pachy, kmax, scarring):
        plan.append("⚠️ Keratoplasty recommended due to scarring or advanced disease")
        return plan

    # Step 3: PRK + CXL
    prk_ok = is_prk_eligible(sphere, cylinder, pachy, scarring)
    if prk_ok:
        plan.append("PRK eligible (must be combined with CXL if age < 40)")

        # Step 4: ICRS
    icrs_ok = is_icrs_eligible(sphere, cylinder, pachy, kmax, scarring)
    if icrs_ok:
        icrs = find_icrs_recommendation(sphere, cylinder, asymmetry_type, nomogram_df, age, pachy, scarring)
        plan.append(f"ICRS recommendation: {icrs}")

    # Step 5: CXL
    if is_cxl_indicated(age, prk_ok, icrs_ok, pachy):
        plan.append("CXL recommended")

    # Step 6: IOLs
    if is_phakic_iol(age, sphere, cylinder):
        plan.append("Phakic IOL indicated (sphere < -10 D, age < 40)")
    elif is_phakic_iol_with_icrs(age, sphere, cylinder):
        plan.append("Phakic IOL + ICRS (high sphere with astigmatism > 2 D)")
    elif is_pseudophakic_iol(age, sphere, cylinder):
        plan.append("Pseudophakic IOL indicated (sphere < -10 D, age ≥ 40)")
    elif is_pseudophakic_iol_with_icrs(age, sphere, cylinder):
        plan.append("Pseudophakic IOL + ICRS (high sphere + astigmatism > 2 D)")

    return plan


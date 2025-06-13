
# LASIK Surgical Planner App

This is a Streamlit web app to plan LASIK surgeries based on patient data. It calculates ablation depth, postoperative keratometry, pachymetry, and BCVA predictions, and provides surgical recommendations with risk warnings.

## Features

- Predict postoperative K1, K2, pachymetry, and BCVA
- Recommend best refractive surgery type (LASIK, PRK, or Phakic IOL)
- Show warnings for keratoconus risk, ectasia, extreme hyperopia, and poor vision
- Upload patient data via CSV

## Project Structure

- `app.py`: Main Streamlit app
- `logic.py`: Core calculations
- `utils/helpers.py`: Optional helper functions
- `data/sample_data.csv`: Sample patient input
- `.streamlit/config.toml`: Streamlit settings
- `.gitignore`: Files to exclude from Git
- `README.md`: This file

## How to Run Locally

1. Clone the repo:
```bash
git clone https://github.com/yourusername/lasik-planner.git
cd lasik-planner
```

2. Install the required libraries:
```bash
pip install -r requirements.txt
```

3. Run the app:
```bash
streamlit run app.py
```

## Sample Input Format

```csv
PatientID,Sphere,Cylinder,K1_pre,K2_pre,Pachymetry_pre,BCVA_pre,Age
1,-3.5,-1.25,43.5,44.1,520,0.8,27
...
```

## License

MIT License

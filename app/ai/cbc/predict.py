import os
import json
from pathlib import Path
import warnings

# Suppress warnings
warnings.filterwarnings('ignore', category=UserWarning, module='pytorch_tabnet')
warnings.filterwarnings('ignore', category=UserWarning, module='sklearn')
warnings.filterwarnings('ignore', message='.*InconsistentVersionWarning.*')

import numpy as np
import pandas as pd
import joblib
from pytorch_tabnet.tab_model import TabNetClassifier


# =================== Configuration ===================
# Get the directory where this file is located
CURRENT_DIR = Path(__file__).parent

# Model file paths
MODEL_PATH   = str(CURRENT_DIR / "tabnet_anemia_model.zip")
SCALER_PATH  = str(CURRENT_DIR / "scaler.pkl")
FEATURES_PTH = str(CURRENT_DIR / "used_features.json")

# Column name aliases for flexible input
ALIASES = {
    'TLC':  ['tlc', 'wbc', 'white blood cells', 'whitebloodcells', 'w.b.c'],
    'PCV':  ['pcv', 'hct', 'hematocrit'],
    'RBC':  ['rbc', 'red blood cells', 'redbloodcells'],
    'HGB':  ['hgb', 'hb', 'hemoglobin', 'haemoglobin'],
    'MCV':  ['mcv'],
    'MCH':  ['mch'],
    'MCHC': ['mchc'],
    'PLT':  ['plt', 'platelets', 'platelet', 'platelet count'],
    'RDW':  ['rdw', 'rdw-cv', 'rdw_cv', 'rdwcv', 'rdw_sd', 'rdwsd'],
    'Age':  ['age', 'years', 'age (y)'],
    'Sex':  ['sex', 'gender', 'm/f', 'male/female'],
    'ID':   ['id', 'sample id', 'sampleid', 'record id', 'patient id', 'no'],
}


# =================== Helper Functions ===================

def norm(s: str) -> str:
    return str(s).strip().lower().replace(' ', '').replace('.', '').replace('-', '').replace('_', '')


def build_rename_map(df_columns):
    rename_map = {}
    for std_name, variants in ALIASES.items():
        for v in variants:
            v_key = norm(v)
            for col in df_columns:
                if norm(col) == v_key:
                    rename_map[col] = std_name
                    break
            if std_name in rename_map.values():
                break
    return rename_map


def normalize_sex_column(series: pd.Series) -> pd.Series:
    if series.dtype == 'object':
        mapped = series.astype(str).str.strip().str.upper().map({
            'F': 0, 'FEMALE': 0, '0': 0,
            'M': 1, 'MALE': 1, '1': 1,
        })
        return pd.to_numeric(mapped, errors='coerce')
    else:
        vals = pd.Series(series.dropna().unique())
        if set(vals) == {0, 1}:
            return series
        if set(vals) == {1, 2}:
            return series.astype(float) - 1
        return pd.to_numeric(series, errors='coerce')


def prepare_dataframe_for_inference(raw_df: pd.DataFrame, used_features, allow_hgb_heuristic: bool = True) -> pd.DataFrame:
    df = raw_df.copy()
    
    # Rename columns
    df = df.rename(columns=build_rename_map(df.columns))
    
    # Normalize Sex column
    if 'Sex' in df.columns:
        df['Sex'] = normalize_sex_column(df['Sex'])
    
    # Convert to numeric
    for c in df.columns:
        if c != 'Diagnosis':
            df[c] = pd.to_numeric(df[c], errors='ignore')
    
    # Check for missing features
    missing = [c for c in used_features if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    
    # Drop rows with NaN in required features
    df_model = df.dropna(subset=used_features).reset_index(drop=True)
    if len(df_model) == 0:
        raise ValueError("No valid rows for inference (all rows have NaN in required features)")
    
    return df_model


# =================== Model Loading ===================
def load_model_and_assets():
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"Model file not found: {MODEL_PATH}")
    if not os.path.exists(SCALER_PATH):
        raise FileNotFoundError(f"Scaler file not found: {SCALER_PATH}")
    if not os.path.exists(FEATURES_PTH):
        raise FileNotFoundError(f"Features file not found: {FEATURES_PTH}")
    
    model = TabNetClassifier()
    model.load_model(MODEL_PATH)
    
    scaler = joblib.load(SCALER_PATH)
    
    with open(FEATURES_PTH, "r") as f:
        used_features = json.load(f)
    
    return model, scaler, used_features


# =================== Medical Report Generation ===================
def _val(row, col):
    try:
        return float(row[col]) if pd.notna(row.get(col, np.nan)) else np.nan
    except Exception:
        return np.nan

def _anemia_phenotype(row):
    mcv  = _val(row, 'MCV')
    mchc = _val(row, 'MCHC')
    rdw  = _val(row, 'RDW')
    
    phenotype = "غير محدد"
    hints = []
    
    if not np.isnan(mcv):
        if mcv < 80:
            phenotype = "Microcytic Anemia (often iron deficiency)"
        elif mcv > 100:
            phenotype = "Macrocytic Anemia (may indicate B12/folate deficiency or other causes)"
        else:
            phenotype = "Normocytic Anemia (may be related to chronic disease/acute bleeding/kidney issues)"
    
    if not np.isnan(mchc) and mchc < 32:
        hints.append("Hypochromia (supports iron deficiency)")
    if not np.isnan(rdw) and rdw > 14.5:
        hints.append("Elevated RDW → significant variation in cell size")
    
    return phenotype, hints

def build_report(row):
    if int(row['Predicted_Anemia']) == 0:
        return (
            "Result: Not Anemic ✅\n"
            "Note: A healthy lifestyle, adequate hydration, and periodic CBC tests as advised by your doctor are recommended."
        )
    
    phenotype, hints = _anemia_phenotype(row)
    hgb = _val(row, 'HGB')
    mcv = _val(row, 'MCV')
    
    base_tests = [
        "Repeat CBC for confirmation",
        "Ferritin + Serum Iron + TIBC/Transferrin Saturation",
        "CRP/ESR if inflammatory/chronic disease is suspected",
    ]
    extra_tests = []
    lifestyle = [
        "Increase iron-rich foods: liver, red meat, lentils, beans, spinach",
        "Take vitamin C with meals to improve iron absorption",
        "Avoid tea and coffee immediately after iron-rich meals (preferably wait 1-2 hours)",
    ]
    
    if not np.isnan(mcv):
        if mcv < 80:
            extra_tests += [
                "Fecal occult blood test (FOBT) based on age and symptoms",
                "Evaluate for uterine bleeding/malabsorption if needed",
            ]
        elif mcv > 100:
            extra_tests += [
                "Vitamin B12 and folate levels",
                "Thyroid function tests (TSH)",
                "Liver function tests (LFTs)",
            ]
        else:
            extra_tests += [
                "Kidney function tests (Creatinine/eGFR)",
                "Screen for chronic diseases or acute bleeding",
            ]
    
    red_flags = [
        "Frequent dizziness/fainting, severe shortness of breath, chest pain",
        "Severe drop in hemoglobin",
        "Visible bleeding: bloody vomit, black stools, severe uterine bleeding",
    ]
    
    lines = []
    lines.append("Result: Anemia Detected 🩸")
    if not np.isnan(hgb):
        lines.append(f"Hb: {hgb:.1f} g/dL")
    if not np.isnan(mcv):
        lines.append(f"MCV: {mcv:.1f} fL")
    lines.append(f"Expected Classification: {phenotype}")
    if hints:
        lines.append("Supporting Observations: " + "; ".join(hints))
    
    lines.append("\n🔬 Suggested Tests (according to physician's evaluation):")
    for t in base_tests + extra_tests:
        lines.append(f"- {t}")
    
    lines.append("\n🍽️ Lifestyle Recommendations:")
    for tip in lifestyle:
        lines.append(f"- {tip}")
    
    lines.append("\n🚩 Red Flags Requiring Urgent Medical Attention:")
    for f in red_flags:
        lines.append(f"- {f}")
    
    lines.append(
        "\n⚠️ Important Notice: This is an automated advisory report and does not constitute a final diagnosis."
        " All treatment decisions are the responsibility of the treating physician."
    )
    
    return "\n".join(lines)


# =================== Prediction with DataFrame Output ===================
def predict_and_annotate_dataframe(df: pd.DataFrame, model, scaler, used_features):
    """
    Make predictions on a dataframe and add Diagnosis and Predicted_Anemia columns.
    
    Args:
        df: Input dataframe with CBC data
        model: Trained model
        scaler: Fitted scaler
        used_features: List of feature names
        
    Returns:
        Tuple of (annotated DataFrame, probabilities array)
    """
    # Prepare the dataframe
    df_prepared = prepare_dataframe_for_inference(df, used_features)
    
    # Extract features and scale
    X = df_prepared[used_features].values
    X_scaled = scaler.transform(X)
    
    # Make predictions
    predictions = model.predict(X_scaled)
    probabilities = model.predict_proba(X_scaled)
    
    # Create output dataframe with original data
    df_output = df_prepared.copy()
    
    # Add prediction columns
    df_output['Predicted_Anemia'] = predictions
    df_output['Diagnosis'] = ['Anemia' if pred == 1 else 'Normal' for pred in predictions]
    
    return df_output, probabilities

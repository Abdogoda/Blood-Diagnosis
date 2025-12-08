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
            phenotype = "أنيميا ميكروسيتيك (غالبًا نقص الحديد)"
        elif mcv > 100:
            phenotype = "أنيميا ماكروسيتيك (قد تشير إلى نقص B12/فولات أو أسباب أخرى)"
        else:
            phenotype = "أنيميا نورموسيتيك (قد ترتبط بمرض مزمن/نزف حاد/كلوي..)"
    
    if not np.isnan(mchc) and mchc < 32:
        hints.append("هيبوكروما (يدعم احتمال نقص الحديد)")
    if not np.isnan(rdw) and rdw > 14.5:
        hints.append("RDW مرتفع → تباين واضح في حجم الكريات")
    
    return phenotype, hints

def build_report(row):
    if int(row['Predicted_Anemia']) == 0:
        return (
            "النتيجة: غير مصاب بالأنيميا ✅\n"
            "ملاحظة: يُنصح بنمط حياة صحي، وترطيب كافٍ، وإعادة CBC دوريًا حسب توجيه الطبيب."
        )
    
    phenotype, hints = _anemia_phenotype(row)
    hgb = _val(row, 'HGB')
    mcv = _val(row, 'MCV')
    
    base_tests = [
        "إعادة CBC للتأكيد",
        "Ferritin + Serum Iron + TIBC/Transferrin Saturation",
        "CRP/ESR عند الشك في مرض التهابي/مزمن",
    ]
    extra_tests = []
    lifestyle = [
        "الإكثار من الأطعمة الغنية بالحديد: كبدة، لحوم حمراء، عدس، فول، سبانخ",
        "تناول فيتامين C مع الوجبات لتحسين امتصاص الحديد",
        "تجنّب الشاي والقهوة مباشرة بعد الوجبات الغنية بالحديد (يفضَّل بعد 1–2 ساعة)",
    ]
    
    if not np.isnan(mcv):
        if mcv < 80:
            extra_tests += [
                "فحص نزف خفي بالبراز (FOBT) حسب العمر والأعراض",
                "تقييم نزف رحمي/سوء امتصاص عند الحاجة",
            ]
        elif mcv > 100:
            extra_tests += [
                "قياس فيتامين B12 وفولات",
                "وظائف الغدة الدرقية (TSH)",
                "وظائف الكبد (LFTs)",
            ]
        else:
            extra_tests += [
                "وظائف الكُلى (Creatinine/eGFR)",
                "بحث عن أمراض مزمنة أو نزف حاد",
            ]
    
    red_flags = [
        "دوخة/إغماء متكرر، ضيق نفس شديد، ألم صدري",
        "هبوط شديد في الهيموجلوبين",
        "نزف ظاهر: قيء دموي، براز أسود، نزف رحمي شديد",
    ]
    
    lines = []
    lines.append("النتيجة: مصاب بالأنيميا 🩸")
    if not np.isnan(hgb):
        lines.append(f"Hb: {hgb:.1f} g/dL")
    if not np.isnan(mcv):
        lines.append(f"MCV: {mcv:.1f} fL")
    lines.append(f"التصنيف المتوقع: {phenotype}")
    if hints:
        lines.append("ملاحظات داعمة: " + "؛ ".join(hints))
    
    lines.append("\n🔬 فحوصات مقترحة (وفق تقييم الطبيب):")
    for t in base_tests + extra_tests:
        lines.append(f"- {t}")
    
    lines.append("\n🍽️ إرشادات نمط حياة:")
    for tip in lifestyle:
        lines.append(f"- {tip}")
    
    lines.append("\n🚩 أعلام خطر تستدعي مراجعة طبية عاجلة:")
    for f in red_flags:
        lines.append(f"- {f}")
    
    lines.append(
        "\n⚠️ تنبيه هام: هذا التقرير آلي استرشادي ولا يُعد تشخيصًا نهائيًا."
        " القرار العلاجي بالكامل للطبيب المعالج."
    )
    
    return "\n".join(lines)

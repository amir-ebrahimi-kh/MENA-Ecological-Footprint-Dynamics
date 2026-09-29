import pandas as pd
import numpy as np
from sklearn.impute import KNNImputer
from sklearn.preprocessing import StandardScaler
import os

# ==============================================================================
# SCRIPT 01: DATA ENGINEERING & IMPUTATION (TARGET-LEAKAGE PROOF)
# ==============================================================================

INPUT_FILE = "data/cleaned/panel_ready.csv"
OUTPUT_FILE = "data/cleaned/engineered_panel.csv"
APPX_DIR = "results/tables/appendix"
os.makedirs(APPX_DIR, exist_ok=True)

df = pd.read_csv(INPUT_FILE)
df['is_imputed'] = df.isnull().any(axis=1).astype(int)

# 1. IMPUTATION TRACKING FOR APPENDIX
missing_rows = df[df.isnull().any(axis=1)].copy()
missing_profile = [{'Country': row['country'], 'Year': int(row['year']), 'Missing_Variables': ", ".join(row.index[row.isnull()].tolist())} for _, row in missing_rows.iterrows()]
pd.DataFrame(missing_profile).to_csv(os.path.join(APPX_DIR, "imputed_observations_appendix.csv"), index=False)

# 2. KNN IMPUTATION (K=3)
# We exclude dependent variables and inequality metrics to prevent Target Leakage
impute_features = [c for c in df.columns if c not in ['country', 'year', 'is_imputed', 'ef_prod', 'ef_carbon', 'ef_noncarbon', 'palma', 'gini_wid', 'top10_share', 'bottom40_share']]

scaler = StandardScaler()
scaled_features = scaler.fit_transform(df[impute_features])

imputer = KNNImputer(n_neighbors=3, weights='distance')
df[impute_features] = scaler.inverse_transform(imputer.fit_transform(scaled_features))

# 3. MATHEMATICAL TRANSFORMATIONS
log_vars = ['ef_prod', 'ef_carbon', 'ef_noncarbon', 'gdp_per_capita', 'palma', 'urban_pct', 'trade_openness', 'co2_owid', 'energy_intensity_eia', 'gini_wid', 'top10_share', 'bottom40_share']
for var in log_vars: 
    df[f'ln_{var}'] = np.log(df[var].clip(lower=1e-5))

# Inverse Hyperbolic Sine for variables containing negative or absolute zero values
ihs_vars = ['fdi_unctad', 'renew_share_eia', 'oil_rents']
for var in ihs_vars: 
    df[f'ihs_{var}'] = np.arcsinh(df[var])

# 4. EXPORT
df = df.drop(columns=log_vars + ihs_vars)
df = df[['country', 'year', 'is_imputed', 'middle50_share'] + [c for c in df.columns if c not in ['country', 'year', 'is_imputed', 'middle50_share']]]
df.to_csv(OUTPUT_FILE, index=False)

print(f"SUCCESS: Engineered panel saved to {OUTPUT_FILE}")
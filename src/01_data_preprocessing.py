import pandas as pd
import numpy as np
import os
from sklearn.impute import KNNImputer

# ==========================================
# 1. PATH CONFIGURATION
# ==========================================
# Adjusted for the GitHub repository structure
DATA_PATH = 'data/raw/master_panel.csv'
OUTPUT_PATH = 'data/processed/engineered_panel.csv'

# Ensure processed data directory exists
os.makedirs('data/processed', exist_ok=True)

print("Loading raw data...")
df = pd.read_csv(DATA_PATH)

# ==========================================
# 2. ANOMALY REMOVAL 
# ==========================================
print("Removing impossible values (setting to NaN for imputation)...")
# Remove the negative Kuwait value and the 2016-2020 hardcoded zeros
df.loc[df['fossil_fuel_share'] <= 0, 'fossil_fuel_share'] = np.nan
# Remove the unreported absolute zeros in renewables
df.loc[df['renewable_energy'] == 0, 'renewable_energy'] = np.nan

# ==========================================
# 3. K-NEAREST NEIGHBORS (KNN) IMPUTATION
# ==========================================
print("Running KNN Imputation (k=3)...")

# We define the specific feature space + targets to be imputed
knn_cols = [
    'fossil_fuel_share', 'energy_intensity', 'fdi_inflows', 'renewable_energy',
    'gdp_per_capita', 'urban_pct', 'trade_openness', 'oil_rents'
]

# Using K=3 as updated in your methodology section
imputer = KNNImputer(n_neighbors=3, weights="distance")

df_imputed = df.copy()
df_imputed[knn_cols] = imputer.fit_transform(df[knn_cols])

# ==========================================
# 4. LOGARITHMIC & IHS TRANSFORMATIONS
# ==========================================
print("Applying Logarithmic and Inverse Hyperbolic Sine (IHS) Transformations...")

# A. Standard Natural Log for strictly positive variables
cols_to_log = [
    'ef', 'palma', 'gini_wid', 'gdp_per_capita', 'fossil_fuel_share', 
    'urban_pct', 'trade_openness', 'co2_per_capita', 'energy_intensity', 'renewable_energy'
]
for col in cols_to_log:
    # We use a tiny lower bound (1e-5) just in case to strictly prevent log(0)
    df_imputed[f'ln_{col}'] = np.log(df_imputed[col].clip(lower=1e-5))

# B. Oil Rents (Contains true economic zeros for countries without oil)
# Standard practice is to add a small constant (e.g., 0.001) before logging
df_imputed['ln_oil'] = np.log(df_imputed['oil_rents'] + 0.001)

# C. Inverse Hyperbolic Sine (IHS) Transformation for FDI
# Formula: ln(x + sqrt(x^2 + 1)) which in numpy is simply arcsinh
df_imputed['ihs_fdi'] = np.arcsinh(df_imputed['fdi_inflows'])

# ==========================================
# 5. GENERATE NEW SUMMARY STATISTICS FOR LATEX
# ==========================================
print("\n=== NEW DESCRIPTIVE STATISTICS FOR TABLE 2 ===")
table_vars = [
    'ln_ef', 'ln_palma', 'ln_gini_wid', 'ln_gdp_per_capita', 
    'ln_fossil_fuel_share', 'ln_renewable_energy', 'ln_urban_pct', 
    'ln_trade_openness', 'ln_oil', 'ihs_fdi'
]

# Print the cleanly rounded stats for you to paste straight into Table 2
summary_stats = df_imputed[table_vars].describe().T[['count', 'mean', 'std', 'min', 'max']]
summary_stats['count'] = summary_stats['count'].astype(int)
print(summary_stats.round(2))

# ==========================================
# 6. FILTER AND SAVE FILE (UPDATED)
# ==========================================
print("\nFiltering dataset to retain only essential econometric variables...")

# Define strictly the variables needed for the final Stata regressions
essential_cols = [
    'country',                # Panel identifier
    'year',                   # Time identifier
    'ln_ef',                  # Dependent Variable
    'ln_co2_per_capita',      # Robustness Dependent Variable
    'ln_palma',               # Main Independent (Palma)
    'ln_gini_wid',            # Main Independent (Gini)
    'ln_gdp_per_capita',      # EKC / Threshold Variable
    'ln_fossil_fuel_share',   # Control
    'ln_renewable_energy',    # Control
    'ln_urban_pct',           # Control
    'ln_trade_openness',      # Control
    'ln_oil',                 # Control
    'ihs_fdi'                 # Control
]

# Keep only the essential columns
df_final = df_imputed[essential_cols]

# Save the pristine dataset
df_final.to_csv(OUTPUT_PATH, index=False)
print(f"\nSUCCESS! Cleaned, minimal dataset saved to:\n{OUTPUT_PATH}")
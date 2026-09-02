import os
import numpy as np
import pandas as pd
import statsmodels.api as sm

# ==========================================
# 1. DIRECTORY SETUP & DATA LOADING
# ==========================================
BASE_DIR = os.getcwd()
DATA_PATH = os.path.join(BASE_DIR, 'data', 'processed', 'engineered_panel.csv') 
TABLES_DIR = os.path.join(BASE_DIR, 'results', 'tables')

os.makedirs(TABLES_DIR, exist_ok=True)

print("Loading engineered panel for Linear Models...")
df = pd.read_csv(DATA_PATH)

# ==========================================
# 2. PANEL INDEXING & LAGGING
# ==========================================
df = df.rename(columns={'country': 'Country', 'year': 'Year'})
df['Year'] = pd.to_datetime(df['Year'], format='%Y').dt.year
df = df.set_index(['Country', 'Year']).sort_index()

df['ln_gdp_sq'] = df['ln_gdp_per_capita'] ** 2
df['ln_ef_lag1'] = df.groupby('Country')['ln_ef'].shift(1)
df['ln_co2_lag1'] = df.groupby('Country')['ln_co2_per_capita'].shift(1)
df = df.dropna(subset=['ln_ef_lag1', 'ln_co2_lag1'])

# ==========================================
# 3. LINEAR MODELS (DFE & ROBUSTNESS)
# ==========================================
print("Estimating Base Linear Models (Table 3)...")
linear_controls = ['ln_ef_lag1', 'ln_gdp_per_capita', 'ln_gdp_sq', 'ln_fossil_fuel_share', 
                   'ln_renewable_energy', 'ln_urban_pct', 'ln_trade_openness', 'ln_oil', 'ihs_fdi']

# Create dummy variables for fixed effects
dummies = pd.get_dummies(df.index.get_level_values('Country'), drop_first=True)
dummies.index = df.index

# Model 1: Palma EF
X1 = sm.add_constant(pd.concat([df[['ln_palma'] + linear_controls], dummies], axis=1)).astype(float)
mod1 = sm.OLS(df['ln_ef'], X1).fit(cov_type='cluster', cov_kwds={'groups': df.index.get_level_values('Country')})

# Model 2: Gini EF
X2 = sm.add_constant(pd.concat([df[['ln_gini_wid'] + linear_controls], dummies], axis=1)).astype(float)
mod2 = sm.OLS(df['ln_ef'], X2).fit(cov_type='cluster', cov_kwds={'groups': df.index.get_level_values('Country')})

# Model 3: Palma CO2 (Robustness)
co2_controls = ['ln_co2_lag1', 'ln_gdp_per_capita', 'ln_gdp_sq', 'ln_fossil_fuel_share', 
                'ln_renewable_energy', 'ln_urban_pct', 'ln_trade_openness', 'ln_oil', 'ihs_fdi']
X3 = sm.add_constant(pd.concat([df[['ln_palma'] + co2_controls], dummies], axis=1)).astype(float)
mod3 = sm.OLS(df['ln_co2_per_capita'], X3).fit(cov_type='cluster', cov_kwds={'groups': df.index.get_level_values('Country')})

# ==========================================
# 4. EXPORT RESULTS
# ==========================================
display_vars = ['const', 'ln_ef_lag1', 'ln_co2_lag1', 'ln_palma', 'ln_gini_wid', 
                'ln_gdp_per_capita', 'ln_gdp_sq', 'ln_fossil_fuel_share', 'ln_renewable_energy', 
                'ln_urban_pct', 'ln_trade_openness', 'ln_oil', 'ihs_fdi']

linear_summary = pd.DataFrame({'Model 1 (Coef)': mod1.params, 'M1 P-val': mod1.pvalues, 
                               'Model 2 (Coef)': mod2.params, 'M2 P-val': mod2.pvalues, 
                               'Model 3 (Coef)': mod3.params, 'M3 P-val': mod3.pvalues})
linear_summary = linear_summary.reindex(display_vars)

output_file = os.path.join(TABLES_DIR, 'Table3_Linear_Models.csv')
linear_summary.to_csv(output_file)
print(f"Success! Linear results saved to {output_file}")
import os
import numpy as np
import pandas as pd
import statsmodels.api as sm
import matplotlib.pyplot as plt
import seaborn as sns

# ==========================================
# 1. DIRECTORY SETUP & DATA LOADING
# ==========================================
BASE_DIR = os.getcwd()
DATA_PATH = os.path.join(BASE_DIR, 'data', 'processed', 'engineered_panel.csv') 
TABLES_DIR = os.path.join(BASE_DIR, 'results', 'tables')
FIGURES_DIR = os.path.join(BASE_DIR, 'results', 'figures')

os.makedirs(TABLES_DIR, exist_ok=True)
os.makedirs(FIGURES_DIR, exist_ok=True)

print("Loading engineered panel for Threshold Model...")
df = pd.read_csv(DATA_PATH)

# ==========================================
# 2. PANEL INDEXING & LAGGING
# ==========================================
df = df.rename(columns={'country': 'Country', 'year': 'Year'})
df['Year'] = pd.to_datetime(df['Year'], format='%Y').dt.year
df = df.set_index(['Country', 'Year']).sort_index()

df['ln_gdp_sq'] = df['ln_gdp_per_capita'] ** 2
df['ln_ef_lag1'] = df.groupby('Country')['ln_ef'].shift(1)
df = df.dropna(subset=['ln_ef_lag1'])

# ==========================================
# 3. FORWARD ORTHOGONAL DEVIATIONS (FOD)
# ==========================================
print("Applying Forward Orthogonal Deviations...")
def forward_orthogonal_deviation(series):
    fod = pd.Series(index=series.index, dtype=float)
    T = len(series)
    for i in range(T - 1):
        future_mean = series.iloc[i+1:].mean()
        scale = np.sqrt((T - i - 1) / (T - i))
        fod.iloc[i] = scale * (series.iloc[i] - future_mean)
    return fod

fod_df = pd.DataFrame(index=df.index)
cols_to_fod = ['ln_ef', 'ln_ef_lag1', 'ln_palma', 'ln_gdp_per_capita', 'ln_gdp_sq', 
               'ln_fossil_fuel_share', 'ln_renewable_energy', 'ln_urban_pct', 
               'ln_trade_openness', 'ln_oil', 'ihs_fdi']

for col in cols_to_fod:
    fod_df[f'{col}_fod'] = df.groupby(level='Country', group_keys=False)[col].apply(forward_orthogonal_deviation)
fod_df = fod_df.dropna()

# ==========================================
# 4. DYNAMIC PANEL THRESHOLD GRID SEARCH
# ==========================================
print("Initiating Grid Search for Endogenous Threshold (Gamma)...")
controls = ['ln_ef_lag1_fod', 'ln_gdp_per_capita_fod', 'ln_gdp_sq_fod', 'ln_fossil_fuel_share_fod', 
            'ln_renewable_energy_fod', 'ln_urban_pct_fod', 'ln_trade_openness_fod', 'ln_oil_fod', 'ihs_fdi_fod']
q = fod_df['ln_gdp_per_capita_fod']
percentiles = np.percentile(q, np.arange(15, 86, 1))

best_gamma, min_ssr = None, np.inf
ssr_list, gamma_list = [], []

for gamma in percentiles:
    regime_1 = (q <= gamma).astype(int)
    regime_2 = (q > gamma).astype(int)
    fod_df['Palma_Regime1'] = fod_df['ln_palma_fod'] * regime_1
    fod_df['Palma_Regime2'] = fod_df['ln_palma_fod'] * regime_2
    
    X = fod_df[['Palma_Regime1', 'Palma_Regime2'] + controls]
    Y = fod_df['ln_ef_fod']
    model = sm.OLS(Y, X).fit()
    
    ssr_list.append(model.ssr)
    gamma_list.append(gamma)
    if model.ssr < min_ssr:
        min_ssr, best_gamma, best_model = model.ssr, gamma, model

print(f"Optimal Threshold (Gamma) discovered at ln_GDP_fod = {best_gamma:.4f}")

# Export Table 4
dptr_summary = pd.DataFrame({'Coefficient': best_model.params, 'Std_Error': best_model.bse, 
                             'T_Stat': best_model.tvalues, 'P_Value': best_model.pvalues})
dptr_summary.to_csv(os.path.join(TABLES_DIR, 'Table4_Threshold_Regimes.csv'))

# ==========================================
# 5. GENERATING FIGURE 2
# ==========================================
print("Generating SSR Grid Search Plot...")
plt.figure(figsize=(10, 6))
sns.set_style("whitegrid")
plt.plot(gamma_list, ssr_list, color='darkred', linewidth=2, label='Sum of Squared Residuals (SSR)')
plt.axvline(x=best_gamma, color='black', linestyle='--', label=rf'Optimal Threshold $\gamma$ = {best_gamma:.4f}')
plt.title('Endogenous Threshold Identification (Grid Search)', fontsize=14, fontweight='bold')
plt.xlabel('Transition Variable (ln_GDP Forward Orthogonal Deviation)', fontsize=12)
plt.ylabel('Sum of Squared Residuals (SSR)', fontsize=12)
plt.legend()
plt.tight_layout()

fig_path = os.path.join(FIGURES_DIR, 'Figure2_threshold_ssr.png')
plt.savefig(fig_path, dpi=300)
plt.close()

print(f"Success! Threshold results saved to '{TABLES_DIR}' and '{FIGURES_DIR}'")
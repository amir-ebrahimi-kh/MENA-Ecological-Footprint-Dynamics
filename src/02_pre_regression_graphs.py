import os
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# ==============================================================================
# SCRIPT 02: PRE-REGRESSION DESCRIPTIVE VISUALIZATIONS & SUMMARY TABLES
# ==============================================================================

RAW_DIR = "data/raw"
CLEAN_DIR = "data/cleaned"
FIG_DIR = "results/figures"
TABLE_DIR = "results/tables" 

os.makedirs(FIG_DIR, exist_ok=True)
os.makedirs(TABLE_DIR, exist_ok=True)

COUNTRIES_17 = [
    'Algeria', 'Bahrain', 'Egypt', 'Iran', 'Iraq', 'Jordan', 'Kuwait', 
    'Lebanon', 'Libya', 'Morocco', 'Oman', 'Qatar', 'Saudi Arabia', 
    'Syria', 'Tunisia', 'United Arab Emirates', 'Yemen'
]

plt.style.use("seaborn-v0_8-whitegrid")
plt.rcParams.update({"font.family": "serif", "font.size": 11, "axes.labelsize": 12})

# ==============================================================================
# 1. ECOLOGICAL DEFICIT FIGURE (FIGURE 1 IN MANUSCRIPT)
# ==============================================================================
print("Generating Figure 1: Regional Ecological Deficit...")
df_ef = pd.read_excel(os.path.join(RAW_DIR, "EF Data.xlsx"))
df_ef["country_name"] = df_ef["country_name"].replace({"Syrian Arab Republic": "Syria", "Iran, Islamic Rep.": "Iran", "Iran (Islamic Republic of)": "Iran"})
df_mena = df_ef[(df_ef["country_name"].isin(COUNTRIES_17)) & (df_ef["year"] >= 2005) & (df_ef["year"] <= 2020)].copy()

agg_df = df_mena.groupby('year')[['efp_total_gha', 'biocap_total_gha']].sum().reset_index()
agg_df['efp_total_gha'] = agg_df['efp_total_gha'] / 1_000_000
agg_df['biocap_total_gha'] = agg_df['biocap_total_gha'] / 1_000_000

plt.figure(figsize=(10, 6))
plt.plot(agg_df['year'], agg_df['efp_total_gha'], color='#6b2121', label='Total Ecological Footprint')
plt.plot(agg_df['year'], agg_df['biocap_total_gha'], color='#1b5e20', label='Total Biocapacity')
plt.fill_between(agg_df['year'], agg_df['biocap_total_gha'], agg_df['efp_total_gha'], color='#f5c6cb', alpha=0.8, label='Ecological Deficit')

plt.xlim(2005, 2020)
plt.ylim(0, agg_df['efp_total_gha'].max() * 1.1)
plt.xlabel('Year')
plt.ylabel('Millions of Global Hectares (gha)')
plt.legend(loc='upper left')
plt.title('')
plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, "Figure1_MENA_Ecological_Deficit.png"), dpi=300)
plt.close()

# ==============================================================================
# 2. RAW SUMMARY TABLE (TABLE 2 IN MANUSCRIPT)
# ==============================================================================
print("Exporting Descriptive Statistics Table...")
engineered_panel = pd.read_csv(os.path.join(CLEAN_DIR, "engineered_panel.csv"))

raw_vars = ["ln_ef_prod", "ln_palma", "ln_gini_wid", "ln_gdp_per_capita", "ln_energy_intensity_eia", "ihs_renew_share_eia", "ln_urban_pct", "ln_trade_openness", "ihs_oil_rents", "ihs_fdi_unctad"]
raw_stats = engineered_panel[raw_vars].describe().T[["count", "mean", "std", "min", "max"]].round(2)
raw_stats.to_latex(os.path.join(TABLE_DIR, "Table2_Descriptive_Statistics.tex"))

print(f"Figure 1 saved to '{FIG_DIR}/'. Descriptive stats saved to '{TABLE_DIR}/'.")
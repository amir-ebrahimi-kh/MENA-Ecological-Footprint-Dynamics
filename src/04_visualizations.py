import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ==========================================
# 1. DIRECTORY SETUP & DATA LOADING
# ==========================================
BASE_DIR = os.getcwd()
# Points to the raw data folder where EF Data.xlsx should be stored
DATA_PATH = os.path.join(BASE_DIR, 'data', 'raw', 'EF Data.xlsx') 
FIGURES_DIR = os.path.join(BASE_DIR, 'results', 'figures')

os.makedirs(FIGURES_DIR, exist_ok=True)

print("Loading raw Ecological Footprint data...")
if not os.path.exists(DATA_PATH):
    print(f"Error: Could not find '{DATA_PATH}'. Please ensure 'EF Data.xlsx' is in the 'data/raw' folder.")
else:
    ef_raw = pd.read_excel(DATA_PATH)

    # ==========================================
    # 2. DATA FILTERING & AGGREGATION
    # ==========================================
    print("Filtering for MENA region and calculating aggregate deficit...")
    mena_17 = [
        'Algeria', 'Bahrain', 'Egypt', 'Iran', 'Iraq', 'Jordan', 'Kuwait', 'Lebanon', 
        'Libya', 'Morocco', 'Oman', 'Qatar', 'Saudi Arabia', 'Syrian Arab Republic', 
        'Tunisia', 'United Arab Emirates', 'Yemen'
    ]

    # Filter for our specific 17 countries and the 2005-2020 timeline
    ef_mena = ef_raw[ef_raw['country_name'].isin(mena_17) & (ef_raw['year'] >= 2005) & (ef_raw['year'] <= 2020)]
    
    # Group by year and sum total footprint and biocapacity, then convert to millions of gha
    regional_totals = ef_mena.groupby('year')[['efp_total_gha', 'biocap_total_gha']].sum() / 1_000_000

    # ==========================================
    # 3. GENERATING FIGURE 1
    # ==========================================
    print("Generating Figure 1: Ecological Deficit Area Chart...")
    plt.figure(figsize=(10, 6))
    sns.set_style("whitegrid")
    
    # Plot the two main lines
    plt.plot(regional_totals.index, regional_totals['efp_total_gha'], color='darkred', label='Total Ecological Footprint')
    plt.plot(regional_totals.index, regional_totals['biocap_total_gha'], color='darkgreen', label='Total Biocapacity')
    
    # Fill the gap to visually represent the Ecological Deficit
    plt.fill_between(regional_totals.index, regional_totals['biocap_total_gha'], 
                     regional_totals['efp_total_gha'], color='lightcoral', alpha=0.4, label='Ecological Deficit')

    # Formatting
    plt.title('The Widening Ecological Deficit in the MENA Region (2005-2020)', fontsize=14, fontweight='bold')
    plt.ylabel('Millions of Global Hectares (gha)', fontsize=12)
    plt.xlabel('Year', fontsize=12)
    plt.xlim(2005, 2020)
    plt.legend(loc='upper left')
    plt.tight_layout()
    
    # Save the figure
    fig_path = os.path.join(FIGURES_DIR, 'Figure1_ecological_deficit.png')
    plt.savefig(fig_path, dpi=300)
    plt.close()
    
    print(f"Success! Figure 1 successfully saved to '{fig_path}'")
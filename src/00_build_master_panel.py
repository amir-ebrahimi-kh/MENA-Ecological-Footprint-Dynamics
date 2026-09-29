import pandas as pd
import numpy as np
import os

# ==============================================================================
# SCRIPT 00: MASTER PANEL EXTRACTION & HARMONIZATION
# ==============================================================================

BASE = "data/raw"
OUTPUT = "data/cleaned/panel_ready.csv"
YEARS = list(range(2005, 2021))

os.makedirs("data/cleaned", exist_ok=True)

COUNTRIES_17 = [
    'Algeria', 'Bahrain', 'Egypt', 'Iran', 'Iraq', 'Jordan',
    'Kuwait', 'Lebanon', 'Libya', 'Morocco', 'Oman', 'Qatar',
    'Saudi Arabia', 'Syria', 'Tunisia', 'United Arab Emirates', 'Yemen'
]

WB_NAME_VARIANTS = {
    'Egypt': ['Egypt, Arab Rep.', 'Egypt'], 'Iran': ['Iran, Islamic Rep.', 'Iran'],
    'Syria': ['Syrian Arab Republic', 'Syria'], 'Yemen': ['Yemen, Rep.', 'Yemen']
}
WID_CODES = {
    'Algeria': 'DZ', 'Bahrain': 'BH', 'Egypt': 'EG', 'Iran': 'IR', 'Iraq': 'IQ', 'Jordan': 'JO', 
    'Kuwait': 'KW', 'Lebanon': 'LB', 'Libya': 'LY', 'Morocco': 'MA', 'Oman': 'OM', 'Qatar': 'QA',
    'Saudi Arabia': 'SA', 'Syria': 'SY', 'Tunisia': 'TN', 'United Arab Emirates': 'AE', 'Yemen': 'YE'
}

def extract_wid(filename, years=YEARS):
    raw = pd.read_excel(os.path.join(BASE, filename), sheet_name="Data", header=None)
    header = raw.iloc[0, :].tolist()
    records = []
    for col_idx, col_header in enumerate(header):
        if isinstance(col_header, str) and ('sptinc' in col_header.lower() or 'gptinc' in col_header.lower()):
            code = col_header.split('\n')[0].strip().split('_')[-1].upper()
            if code in WID_CODES.values():
                country = [k for k, v in WID_CODES.items() if v == code][0]
                for row_idx in range(1, len(raw)):
                    year_val, value_val = raw.iloc[row_idx, 1], raw.iloc[row_idx, col_idx]
                    if pd.notna(year_val) and pd.notna(value_val):
                        try:
                            year = int(float(year_val))
                            if year in years: records.append({'country': country, 'year': year, 'value': float(value_val)})
                        except: pass
    return pd.DataFrame(records)

def extract_wb(filename, value_name, years=YEARS):
    for skip in [3, 2, 0]:
        df = pd.read_excel(os.path.join(BASE, filename), skiprows=skip)
        if 'Country Name' in df.columns: break
    name_map = {c: c for c in COUNTRIES_17}
    for std_name, variants in WB_NAME_VARIANTS.items():
        for var in variants:
            if var in df['Country Name'].values: name_map[var] = std_name
    df = df[df['Country Name'].isin(name_map.keys())].copy()
    df['country'] = df['Country Name'].map(name_map)
    df_long = df.melt(id_vars=['country'], value_vars=[str(y) for y in years], var_name='year', value_name=value_name)
    df_long['year'] = df_long['year'].astype(int)
    df_long[value_name] = pd.to_numeric(df_long[value_name], errors='coerce')
    return df_long[['country', 'year', value_name]]

def extract_ef():
    df = pd.read_excel(os.path.join(BASE, "EF Data.xlsx"), sheet_name=0)
    ef = df[['country_name', 'year', 'efp_total_percapita', 'efp_carbon_gha', 'pop_1000_persons']].copy()
    ef.columns = ['country', 'year', 'ef_prod', 'efp_carbon_gha', 'pop_1000']
    ef['country'] = ef['country'].replace({'Syrian Arab Republic': 'Syria', 'Iran, Islamic Rep.': 'Iran', 'Iran (Islamic Republic of)': 'Iran'})
    ef = ef[ef['country'].isin(COUNTRIES_17) & ef['year'].isin(YEARS)]
    for col in ['ef_prod', 'efp_carbon_gha', 'pop_1000']: ef[col] = pd.to_numeric(ef[col], errors='coerce')
    ef['ef_carbon'] = ef['efp_carbon_gha'] / (ef['pop_1000'] * 1000)
    ef['ef_noncarbon'] = ef['ef_prod'] - ef['ef_carbon']
    return ef[['country', 'year', 'ef_prod', 'ef_carbon', 'ef_noncarbon']]

def extract_owid_co2():
    df = pd.read_csv(os.path.join(BASE, "co-emissions-per-capita.csv"))
    val_cols = [c for c in df.columns if 'per_capita' in c.lower() or 'emissions' in c.lower()]
    val_col = val_cols[-1] if val_cols else df.columns[-1]
    records = []
    for c in COUNTRIES_17:
        match = df[(df['Entity'] == ('Syria' if c == 'Syria' else c)) & (df['Year'].isin(YEARS))]
        for _, row in match.iterrows(): records.append({'country': c, 'year': int(row['Year']), 'co2_owid': row[val_col]})
    return pd.DataFrame(records)

def extract_eia_intensity():
    df = pd.read_csv(os.path.join(BASE, "INT-Export-09-16-2026_13-28-59-intensity.csv"), skiprows=1)
    records = []
    for c in COUNTRIES_17:
        search_name = 'Syria' if c == 'Syria' else c
        for i, row in df.iterrows():
            if search_name.lower() == str(row['Unnamed: 1']).strip().lower():
                data_row = df.iloc[i+2]
                for y in YEARS: records.append({'country': c, 'year': y, 'energy_intensity_eia': data_row[str(y)]})
                break
    return pd.DataFrame(records)

def extract_eia_renewables():
    df = pd.read_csv(os.path.join(BASE, "INT-Export-09-16-2026_13-30-28-renew-and-total.csv"), skiprows=1)
    records = []
    for c in COUNTRIES_17:
        search_name, current = 'Syria' if c == 'Syria' else c, False
        total, renew = {}, {}
        for i, row in df.iterrows():
            val = str(row['Unnamed: 1']).strip()
            if pd.isna(row['API']) and not pd.isna(row['Unnamed: 1']) and '(' not in val: current = (search_name.lower() == val.lower())
            elif current:
                if 'Consumption' in val and 'Renewables' not in val and 'Nuclear' not in val:
                    for y in YEARS: total[y] = row[str(y)]
                elif 'Renewables' in val and 'Nuclear' not in val:
                    for y in YEARS: renew[y] = row[str(y)]
        for y in YEARS:
            if y in total and y in renew:
                try: share = max(0.0, (float(renew[y]) / float(total[y])) * 100 if float(total[y]) > 0 else 0.0)
                except: share = np.nan
                records.append({'country': c, 'year': y, 'renew_share_eia': share})
    return pd.DataFrame(records)

def extract_unctad_fdi():
    df = pd.read_csv(os.path.join(BASE, "US.FdiFlowsStock_20260916_102759.csv"))
    records = []
    for c in COUNTRIES_17:
        search_name = 'Syrian Arab Republic' if c == 'Syria' else ('Iran (Islamic Republic of)' if c == 'Iran' else c)
        match = df[df['Economy_Label'] == search_name]
        if not match.empty:
            for y in YEARS:
                col = f"{y}_Percentage_of_gross_Domestic_Product_Value"
                records.append({'country': c, 'year': y, 'fdi_unctad': match.iloc[0][col] if col in match.iloc[0].index else np.nan})
    out = pd.DataFrame(records)
    out['fdi_unctad'] = pd.to_numeric(out['fdi_unctad'], errors='coerce')
    return out

print("Extracting data...")
bottom40 = extract_wid("Bottom40.xlsx").rename(columns={'value': 'bottom40_share'})
top10 = extract_wid("Top10.xlsx").rename(columns={'value': 'top10_share'})
wid_gini = extract_wid("WID_Data_13052026-165225.xlsx").rename(columns={'value': 'gini_wid'})

wb_files = {
    "API_NY.GDP.PCAP.CD_DS2_en_excel_v2_126983.xls": "gdp_per_capita",
    "API_SP.URB.TOTL.IN.ZS_DS2_en_excel_v2_782.xls": "urban_pct",
    "API_NE.TRD.GNFS.ZS_DS2_en_excel_v2_731.xls": "trade_openness",
    "API_NY.GDP.PETR.RT.ZS_DS2_en_excel_v2_1124.xls": "oil_rents",
}
wb_data = {var: extract_wb(f, var) for f, var in wb_files.items()}
ef, co2, eia_int, eia_ren, fdi = extract_ef(), extract_owid_co2(), extract_eia_intensity(), extract_eia_renewables(), extract_unctad_fdi()

master = bottom40.merge(top10, on=['country', 'year'], how='outer')
master['palma'] = master['top10_share'] / master['bottom40_share']
master['middle50_share'] = 1 - (master['top10_share'] + master['bottom40_share'])
master = master[['country', 'year', 'palma', 'top10_share', 'bottom40_share', 'middle50_share']].merge(ef, on=['country', 'year'], how='left')

for data in wb_data.values(): master = master.merge(data, on=['country', 'year'], how='left')
for data in [wid_gini, co2, eia_int, eia_ren, fdi]: master = master.merge(data, on=['country', 'year'], how='left')

master.to_csv(OUTPUT, index=False)
print(f"✓ Saved successfully to {OUTPUT}")
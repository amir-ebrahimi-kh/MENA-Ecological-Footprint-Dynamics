/* =====================================================================
   Script: 02_linear_baseline_dfe.do
   Purpose: Dynamic Fixed Effects with Kiviet (1995) Bias Correction 
            and Automated Table Export
   ===================================================================== */

clear all
set more off

// 1. Load the dataset engineered by the Python KNN pipeline
import delimited "data/processed/engineered_panel.csv", clear

// 2. Encode country string to numeric and declare panel structure
encode country, generate(country_id)
xtset country_id year

// 3. Generate the squared GDP term (Environmental Kuznets Curve assumption)
generate ln_gdp_sq = ln_gdp_per_capita^2

// 4. Define control variables globally for clean code
global controls ln_gdp_per_capita ln_gdp_sq ln_fossil_fuel_share ln_renewable_energy ln_urban_pct ln_trade_openness ln_oil ihs_fdi

// Clear previous stored estimates
eststo clear

// =====================================================================
// MODEL 1: Palma Ratio on Ecological Footprint (Kiviet LSDVC)
// =====================================================================
display "Estimating Bias-Corrected LSDV (Model 1: Palma -> EF)..."
xtlsdvc ln_ef ln_palma $controls, initial(ab) vcov(50)
eststo model1

// =====================================================================
// MODEL 2: Gini on Ecological Footprint (Kiviet LSDVC)
// =====================================================================
display "Estimating Bias-Corrected LSDV (Model 2: Gini -> EF)..."
xtlsdvc ln_ef ln_gini_wid $controls, initial(ab) vcov(50)
eststo model2

// =====================================================================
// MODEL 3: Robustness Check (Palma -> CO2)
// =====================================================================
display "Estimating Bias-Corrected LSDV (Model 3: Palma -> CO2)..."
xtlsdvc ln_co2_per_capita ln_palma $controls, initial(ab) vcov(50)
eststo model3

// =====================================================================
// 4. EXPORT RESULTS TO CSV (For Table 3)
// =====================================================================
// Create the results directory if it doesn't exist (using a shell command)
capture mkdir "results/tables"

display "Exporting results to results/tables/Table3_Linear_Models.csv..."

esttab model1 model2 model3 using "results/tables/Table3_Linear_Models.csv", ///
    replace csv ///
    title("Table 3: Dynamic Panel Data Estimation (Kiviet Bias-Corrected LSDVC)") ///
    mtitles("Palma (EF)" "Gini (EF)" "Palma (CO2)") ///
    cells(b(star fmt(3)) se(par fmt(3))) ///
    star(* 0.10 ** 0.05 *** 0.01) ///
    stats(N, labels("Observations")) ///
    addnotes("Bootstrapped standard errors in parentheses (50 iterations).")

display "SUCCESS! Linear results saved."
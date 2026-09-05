/* =====================================================================
   Script: 03_dynamic_threshold_fod.do
   Purpose: Kremer Dynamic Panel Threshold Model (FOD Transformation)
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

// =====================================================================
// 5. DYNAMIC THRESHOLD ESTIMATION (Kremer et al., 2013)
// =====================================================================
display "Estimating Dynamic Panel Threshold (FOD) for Ecological Footprint..."
capture mkdir "results/figures"

// Model 1: Palma Threshold Effect
xtendothresdpd ln_ef L.ln_ef $controls, thresv(ln_gdp_per_capita) stub(m1) pivar(ln_palma) dgmmiv(ln_ef) fodeviation grid(100)
// Save physical graph and store estimation results
graph save "results/figures/palma_temp.gph", replace
eststo threshold_model1

// Model 2: Gini Threshold Effect (Robustness)
display "Estimating Dynamic Panel Threshold (FOD) using Gini..."
xtendothresdpd ln_ef L.ln_ef $controls, thresv(ln_gdp_per_capita) stub(m2) pivar(ln_gini_wid) dgmmiv(ln_ef) fodeviation grid(100)
// Save physical graph and store estimation results
graph save "results/figures/gini_temp.gph", replace
eststo threshold_model2

// Combine the physical .gph files side-by-side
graph combine "results/figures/palma_temp.gph" "results/figures/gini_temp.gph", ///
    xsize(10) ysize(5)

// Export the combined graph as a single high-quality PNG
graph export "results/figures/Figure2_Combined_Thresholds.png", replace width(2000)

// Clean up the temporary files
erase "results/figures/palma_temp.gph"
erase "results/figures/gini_temp.gph"

// =====================================================================
// 6. EXPORT RESULTS TO CSV
// =====================================================================
capture mkdir "results/tables"
display "Exporting Threshold Results..."

esttab threshold_model1 threshold_model2 using "results/tables/Table4_Threshold_Models.csv", ///
    replace csv ///
    title("Table 4: Dynamic Panel Threshold Estimation") ///
    mtitles("Palma Threshold" "Gini Threshold") ///
    cells(b(star fmt(3)) se(par fmt(3))) ///
    star(* 0.10 ** 0.05 *** 0.01) ///
    stats(N, labels("Observations")) ///
    addnotes("Threshold effects estimated via Forward Orthogonal Deviations (FOD).")

display "SUCCESS! Threshold results saved."
/* ==============================================================================
   SCRIPT 05: LEAVE-ONE-OUT (LOO) & SAMPLE SENSITIVITY
============================================================================== */

clear all
set more off

capture mkdir "results/logs"
capture log close
log using "results/logs/05_sensitivity_log.txt", text replace

import delimited "data/cleaned/engineered_panel.csv", clear
encode country, generate(country_id)
xtset country_id year

gen ln_gdp_sq = ln_gdp_per_capita^2
global controls ln_gdp_per_capita ln_gdp_sq ihs_renew_share_eia ln_urban_pct ln_trade_openness ihs_oil_rents ihs_fdi_unctad


/* --- 1. SENSITIVITY 1: CONFLICT-FREE & DROP 2020 & DROP IRQ/LBN --- */

// Sensitivity: Drop conflict-prone states
preserve
drop if inlist(country, "Syria", "Yemen", "Libya")
set seed 12345
xtlsdvc ln_ef_prod ln_palma $controls, initial(ab) vcov(50)
restore

// Sensitivity: Drop 2020 (COVID-19 shock)
preserve
drop if year == 2020
set seed 12345
xtlsdvc ln_ef_prod ln_palma $controls, initial(ab) vcov(50)
restore

// Sensitivity: Drop specific outlier cases
preserve
drop if inlist(country, "Iraq", "Lebanon")
set seed 12345
xtlsdvc ln_ef_prod ln_palma $controls, initial(ab) vcov(50)
restore


/* --- 2. LEAVE-ONE-OUT (LOO) TRACKING --- */
display "=========================================================="
display "LEAVE-ONE-OUT STABILITY TEST"
display "=========================================================="

matrix loo_results = J(17, 1, .)
local row = 1

levelsof country_id, local(countries)

foreach c of local countries {
    set seed 12345
    quietly xtlsdvc ln_ef_prod ln_palma $controls if country_id != `c', initial(ab) vcov(50)

    local beta_palma = _b[ln_palma]
    matrix loo_results[`row', 1] = `beta_palma'
    local row = `row' + 1
}

svmat loo_results, names(loo_)
summarize loo_1

display "LOO Min: " r(min) " | LOO Max: " r(max)

log close

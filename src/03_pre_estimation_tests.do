/* ==============================================================================
   SCRIPT 03: PRE-ESTIMATION DIAGNOSTICS
============================================================================== */

clear all
set more off

capture mkdir "results/logs"
capture log close
log using "results/logs/03_pre_estimation_tests_log.txt", text replace

import delimited "data/cleaned/engineered_panel.csv", clear
encode country, generate(country_id)
xtset country_id year

gen ln_gdp_sq = ln_gdp_per_capita^2
global controls ln_gdp_per_capita ln_gdp_sq ihs_renew_share_eia ln_urban_pct ln_trade_openness ihs_oil_rents ihs_fdi_unctad


/* --- 1. MULTICOLLINEARITY (CENTERED VIF) --- */
display "=========================================================="
display "CENTERED VIF TEST"
display "=========================================================="

quietly reg ln_ef_prod ln_palma $controls
vif


/* --- 2. CSD TEST ON RESIDUALS --- */
display "=========================================================="
display "CROSS-SECTIONAL DEPENDENCE TEST (PESARAN CD ON RESIDUALS)"
display "=========================================================="

capture which xtcd
if _rc quietly ssc install xtcd

quietly xtreg ln_ef_prod ln_palma $controls, fe
predict res_fe, e
xtcd res_fe


/* --- 3. PANEL UNIT ROOT TESTS --- */
display "=========================================================="
display "PANEL UNIT ROOT TESTS"
display "=========================================================="

capture which xtcips
if _rc quietly ssc install multipurt

capture xtcips ln_ef_prod, maxlags(1) bglags(1)
capture xtcips ln_palma, maxlags(1) bglags(1)

log close

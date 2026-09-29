/* =========================================================================
   SCRIPT 06: Dynamic Panel Threshold Regression & SSR Export
========================================================================= */
clear all
set more off

capture mkdir "results/logs"
capture log close
log using "results/logs/06_threshold_log.txt", text replace

import delimited "data/cleaned/engineered_panel.csv", clear
encode country, generate(country_id)
xtset country_id year
gen ln_gdp_sq = ln_gdp_per_capita^2
global controls ln_gdp_per_capita ln_gdp_sq ihs_renew_share_eia ln_urban_pct ln_trade_openness ihs_oil_rents ihs_fdi_unctad

/* --- 1. RUN BASE THRESHOLD MODEL (MANUSCRIPT TABLE 5) --- */
xtendothresdpd ln_ef_prod L.ln_ef_prod $controls, thresv(ln_gdp_per_capita) stub(rgm) pivar(ln_palma) dgmmiv(ln_ef_prod) fodeviation grid(100)
local gamma = e(gammahat)

/* --- 2. EXPORT SSR DATA SAFELY FOR PYTHON GRAPHING (FIGURE 2) --- */
// We directly export the variables xtendothresdpd creates, avoiding serset entirely.
preserve
keep rgm_gamma rgm_lrofgamma
drop if missing(rgm_gamma)
export delimited using "data/cleaned/threshold_graph_data.csv", replace
restore

/* --- 3. ROBUSTNESS: GULF PROXY CHECK --- */
display "--- DROPPING GULF STATES ---"
gen is_gulf = inlist(country, "Bahrain", "Kuwait", "Oman", "Qatar", "Saudi Arabia", "United Arab Emirates")
capture xtendothresdpd ln_ef_prod L.ln_ef_prod $controls if is_gulf == 0, thresv(ln_gdp_per_capita) stub(nogulf) pivar(ln_palma) dgmmiv(ln_ef_prod) fodeviation grid(50)

log close
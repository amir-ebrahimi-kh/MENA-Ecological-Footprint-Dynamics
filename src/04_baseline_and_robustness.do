/* =========================================================================
   SCRIPT 04: Baseline LSDVC, Sys-GMM, and Falsification Tests
========================================================================= */
clear all
set more off

capture mkdir "results/logs"
capture log close
log using "results/logs/04_baseline_models_log.txt", text replace

import delimited "data/cleaned/engineered_panel.csv", clear
encode country, generate(country_id)
xtset country_id year

gen ln_gdp_sq = ln_gdp_per_capita^2
global controls ln_gdp_per_capita ln_gdp_sq ihs_renew_share_eia ln_urban_pct ln_trade_openness ihs_oil_rents ihs_fdi_unctad

/* --- 1. POOLED OLS & FE BOUNDS FOR THE LAG COEFFICIENT --- */
reg ln_ef_prod L.ln_ef_prod ln_palma $controls, vce(cluster country_id)
estimates store m_ols
xtreg ln_ef_prod L.ln_ef_prod ln_palma $controls, fe vce(cluster country_id)
estimates store m_fe

/* --- 2. BASELINE LSDVC (MANUSCRIPT TABLE 3, MODEL 1) --- */
set seed 12345
xtlsdvc ln_ef_prod ln_palma $controls, initial(ab) bias(3) vcov(200)
estimates store m_baseline

/* --- 3. SYSTEM GMM DIAGNOSTICS (MANUSCRIPT TABLE 3, MODEL 2) --- */
capture which xtabond2
if _rc quietly ssc install xtabond2
xtabond2 ln_ef_prod L.ln_ef_prod ln_palma $controls, gmm(L.ln_ef_prod ln_palma, lag(1 2) collapse) iv($controls) twostep robust small
estimates store m_gmm

/* --- 4. FALSIFICATION: CARBON VS NON-CARBON VS TERRITORIAL CO2 (MANUSCRIPT TABLE 4) --- */
set seed 12345
xtlsdvc ln_ef_carbon ln_palma $controls, initial(ab) bias(3) vcov(200)
estimates store m_carbon

set seed 12345
xtlsdvc ln_ef_noncarbon ln_palma $controls, initial(ab) bias(3) vcov(200)
estimates store m_noncarbon

set seed 12345
xtlsdvc ln_co2_owid ln_palma $controls, initial(ab) bias(3) vcov(200)
estimates store m_co2

/* --- EXPORT TABLES --- */
capture mkdir "results/tables"
capture which esttab
if _rc quietly ssc install estout

esttab m_baseline m_gmm using "results/tables/Table3_Baseline_LSDVC.tex", replace style(tex) label b(3) se(3) star(* 0.10 ** 0.05 *** 0.01) keep(L.ln_ef_prod ln_palma)
esttab m_carbon m_noncarbon m_co2 using "results/tables/Table4_Falsification.tex", replace style(tex) label b(3) se(3) star(* 0.10 ** 0.05 *** 0.01) keep(L.ln_ef_carbon L.ln_ef_noncarbon L.ln_co2_owid ln_palma)

log close
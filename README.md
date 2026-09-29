# The Impact of Income Inequality on the Ecological Footprint in MENA Countries

![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)
![Stata Version](https://img.shields.io/badge/stata-16+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

**Replication Repository for:** *The Impact of Income Inequality on the Ecological Footprint in MENA Countries: A Comparative Study of Linear and Non-linear Methods* (Submitted to *Ecological Economics*).

This repository contains the complete data pipeline, Python preprocessing scripts, and Stata econometric models required to replicate all tables, figures, and statistical findings presented in the manuscript.

## 📌 Abstract / Project Overview

This study investigates the association between income inequality (measured by the Palma ratio) and the production-based Ecological Footprint across 17 Middle East and North Africa (MENA) countries from 2005 to 2020. Grounded in the **political economy of the environment (the "Boyce effect")**, the methodology contrasts linear dynamic panel models against non-linear threshold regimes. The analysis aims to test whether elite-driven domestic infrastructure and resource extraction drive ecological overshoot in rentier states, demonstrating how structural inequality influences environmental degradation in the MENA region.

## 📂 Repository Structure

The project is structured to guarantee a strictly reproducible workflow from raw data ingestion to the generation of final regression estimates and visualizations:

```text
.
├── data/
│   ├── raw/                 # Original raw datasets (GFN, WDI, WID, OWID, IEA)
│   └── cleaned/             # Processed, combined datasets ready for econometric modeling
├── results/
│   ├── figures/             # Output directory for generated PNG/EPS charts
│   ├── logs/                # Stata and Python execution logs
│   └── tables/              # LaTeX and CSV outputs of regression summary tables
├── src/
│   ├── 00_build_master_panel.py      # Merges raw data into a master panel
│   ├── 01_data_engineering.py        # Applies KNN imputation and IHS transformations
│   ├── 02_pre_regression_graphs.py   # Generates pre-regression descriptive visualizations
│   ├── 03_pre_estimation_tests.do    # Stata: Unit roots, CSD, and collinearity tests
│   ├── 04_baseline_and_robustness.do # Stata: Baseline LSDVC & Sys-GMM estimations
│   ├── 05_leave_one_out.do           # Stata: Sensitivity checks and Leave-One-Out validation
│   ├── 06_threshold_correction.do    # Stata: Dynamic Panel Threshold Regression
│   └── 07_post_regression_graphs.py  # Generates post-regression figures and threshold graphs
├── .gitignore               # Ignored files for Python/Stata
├── requirements.txt         # Python dependency lockfile
└── README.md                # Project documentation
```

## 🛠️ Methodological Notes for Reviewers

### 1. Data Engineering & Missing Values (Python)
Given the rigid requirements of Forward Orthogonal Deviations (FOD) for strictly balanced panels, we addressed 19 missing country-year observations (<2% of the dataset) using a **K-Nearest Neighbors (KNN)** algorithm ($K=3$). 
*   **No Target Leakage:** The dependent variables (Ecological Footprints) and inequality metrics (Palma, Gini) were strictly excluded from the imputation feature space.
*   **IHS Transformation:** Foreign Direct Investment (FDI) data, which naturally contains negative net inflows, was transformed using the Inverse Hyperbolic Sine (IHS) function to preserve variance while allowing log-like interpretation.

### 2. Linear Baseline: Kiviet Bias-Corrected LSDVC (Stata)
To model the path-dependency of environmental degradation without succumbing to the severe instrument proliferation inherent to System-GMM in small macro-panels ($N=17$), our baseline relies on the **bias-corrected Least Squares Dummy Variable (LSDVC)** estimator (Kiviet 1995; Bruno 2005). The algorithm is initialized via Arellano-Bond with $O(1/NT^2)$ approximation and bootstrapped standard errors.

### 3. Non-Linear Model: Dynamic Panel Threshold Regression (Stata)
To test for structural breaks across economic development stages, we employ the dynamic panel threshold regression model (Kremer et al. 2013) using **Forward Orthogonal Deviations (FOD)**. Given the $N=17$ sample bounds, these threshold estimates are presented as exploratory.

## 🚀 How to Reproduce

### Prerequisites
*   **Python 3.9+** (Requires packages listed in `requirements.txt`)
*   **Stata 16+** (Requires packages: `xtlsdvc`, `xtendothresdpd`, `pesaran`, `xtcd`, `multipurt`, `xtabond2`, `estout`)

### Step-by-Step Execution Guide

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/[your-username]/mena-ecological-inequality.git
    cd mena-ecological-inequality
    ```

2.  **Install Python dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the Data Pipeline (Python):**
    Execute scripts 00 through 02 sequentially in the `src/` folder. This processes the raw files in `data/raw/`, applies the KNN imputation and IHS transformations, builds the main panel, and generates initial visualizations.
    ```bash
    python src/00_build_master_panel.py
    python src/01_data_engineering.py
    python src/02_pre_regression_graphs.py
    ```

4.  **Run the Econometric Models (Stata):**
    Open Stata, set your working directory to the repository root, and execute scripts 03, 04, 05, and 06 sequentially in the `src/` folder. Regression tables will be exported directly to `results/tables/`. (Alternatively, run them in batch mode as shown below).
    ```bash
    stata-mp -b do src/03_pre_estimation_tests.do
    stata-mp -b do src/04_baseline_and_robustness.do
    stata-mp -b do src/05_leave_one_out.do
    stata-mp -b do src/06_threshold_correction.do
    ```

5.  **Generate Post-Regression Figures (Python):**
    Execute script 07 to generate the post-regression graphics (Figure 2 and regime split scatter), which will be saved to `results/figures/`.
    ```bash
    python src/07_post_regression_graphs.py
    ```

## 📜 License & Data Availability
The code in this repository is licensed under the MIT License. The raw macroeconomic and environmental data are publicly available from their respective providers (World Bank, Global Footprint Network, World Inequality Database, Our World in Data).
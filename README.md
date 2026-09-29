# The Impact of Income Inequality on the Ecological Footprint in MENA Countries

**Replication Repository for:** *The Impact of Income Inequality on the Ecological Footprint in MENA Countries: A Comparative Study of Linear and Non-linear Methods* (Submitted to *Ecological Economics*).

This repository contains the complete data pipeline, Python preprocessing scripts, and Stata econometric models required to replicate all tables, figures, and statistical findings presented in the manuscript. 

## 📌 Project Overview

This study investigates the association between income inequality (measured by the Palma ratio) and the production-based Ecological Footprint across 17 Middle East and North Africa (MENA) countries from 2005 to 2020. 

Grounded in the **political economy of the environment (the "Boyce effect")**, the methodology contrasts linear dynamic panel models against non-linear threshold regimes to test whether elite-driven domestic infrastructure and resource extraction drive ecological overshoot in rentier states.

## 📂 Repository Structure

The project is organized to ensure strictly reproducible workflows from raw data to final estimates:

├── data/
│   ├── raw/                 # Original data from GFN, WDI, WID, OWID, and IEA
│   └── cleaned/             # Processed datasets ready for econometric modeling
├── src/
│   ├── 00_build_master_panel.py      # Merges raw datasets
│   ├── 01_data_engineering.py        # Handles KNN imputation and IHS transformations
│   ├── 03_pre_estimation_tests.do    # Stata: Unit roots, CSD, and collinearity tests
│   ├── 04_baseline_and_robustness.do # Stata: LSDVC and Sys-GMM estimations (Tables 3 & 4)
│   ├── 06_threshold_correction.do    # Stata: Dynamic Panel Threshold Regression (Table 5)
│   └── 08_plot_ecological_deficit.py # Python: Generates Figure 1
├── results/
│   ├── figures/             # Output directory for generated PNG/EPS charts
│   ├── logs/                # Stata and Python execution logs
│   └── tables/              # LaTeX and CSV outputs of regression tables
├── requirements.txt         # Python dependencies
└── README.md


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
*   **Python 3.9+**
*   **Stata 16+** (Requires packages: xtlsdvc, xtendothresdpd, pesaran)

### Step-by-Step Execution
1.  **Clone the repository:**
    git clone https://github.com/[your-username]/mena-ecological-inequality.git
    cd mena-ecological-inequality

2.  **Install Python dependencies:**
    pip install -r requirements.txt

3.  **Run the Data Pipeline (Python):**
    Execute scripts 00 through 02 in the src/ folder. This will ingest the files in data/raw/, apply the KNN algorithm and IHS transformations, and output engineered_panel.csv to data/cleaned/.

4.  **Run the Econometric Models (Stata):**
    Open Stata, set your working directory to the repository root, and execute scripts 03, 04, 05, and 06 in the src/ folder. Regression tables will be exported directly to results/tables/.

5.  **Generate Figures (Python):**
    Execute scripts 07, 08, and 09 to generate the exact, publication-ready graphics used in the manuscript (Figures 1 and 2), which will be saved to results/figures/.

## 📜 License & Data Availability
The code in this repository is licensed under the MIT License. The raw macroeconomic and environmental data are publicly available from their respective providers (World Bank, Global Footprint Network, World Inequality Database, Our World in Data).
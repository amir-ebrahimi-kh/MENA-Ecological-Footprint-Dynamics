# MENA Ecological Footprint Dynamics: A Dynamic Panel Threshold Analysis

## 📌 Overview

This repository contains the complete, reproducible data engineering and econometric pipeline for analyzing the non-linear impacts of income inequality (Palma ratio, Gini coefficient) on environmental degradation in the MENA region (2005–2020).

## 🛠️ Methodological Highlights

* **Data Engineering & Visualization (Python):** Automated processing of raw panel data, implementing distance-weighted K-Nearest Neighbors (KNN, $k=3$) imputation for missing values, and applying Inverse Hyperbolic Sine (IHS) and logarithmic transformations.
* **Baseline Econometrics (Stata):** Dynamic Fixed Effects estimation utilizing the Bruno (2005) implementation of the Kiviet (1995) bias-corrected LSDV estimator to resolve Nickell bias in small-$T$ dynamic panels.
* **Non-Linear Analysis (Stata):** Dynamic panel data threshold estimation utilizing the Kremer et al. (2013) Forward Orthogonal Deviations (FOD) transformation to identify regime-switching effects in environmental degradation.

## 📂 Repository Architecture

```text
MENA-Ecological-Footprint-Dynamics/
│
├── data/
│   ├── raw/                          # Raw input variables (master panel)
│   └── processed/                    # Engineered panel output from Python pipeline
│
├── src/
│   ├── 01_knn_imputation.py          # Python: Data cleaning, KNN, transformations
│   ├── 02_linear_baseline_dfe.do     # Stata: Kiviet bias-corrected LSDVC models
│   ├── 03_dynamic_threshold_fod.do   # Stata: Kremer FOD Threshold models & graphs
│   └── 04_visualizations.py          # Python: Descriptive trend analysis & charting
│
├── results/
│   ├── tables/                       # Automated CSV outputs of regression matrices
│   └── figures/                      # High-resolution Likelihood Ratio (LR) & trend plots
│
├── .gitignore                        # Standard Git ignore file
├── requirements.txt                  # Python dependencies
└── README.md                         # Project documentation

```

## 🚀 Replication Guide

This pipeline is designed for seamless local execution.

**Step 1: Python Environment & Data Pipeline**
First, install the required Python packages, then execute the data engineering and visualization scripts.

```bash
pip install -r requirements.txt
python src/01_knn_imputation.py
python src/04_visualizations.py

```

**Step 2: Econometric Modeling**
Open Stata, set your working directory to the project root, and execute the `.do` files. The scripts are programmed to automatically create `results/tables/` and `results/figures/` folders and export outputs.

```stata
do "src/02_linear_baseline_dfe.do"
do "src/03_dynamic_threshold_fod.do"

```

*(Requires community Stata packages: `xtlsdvc`, `estout`, `xtendothresdpd`)*
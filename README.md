# MENA Ecological Footprint Dynamics

## Overview
This repository contains the data and replication code for the paper: **"The Impact of Income Inequality on the Ecological Footprint in MENA Countries: A Comparative Study of Linear and Non-linear Methods."** 

The research investigates the structural and non-linear relationship between income inequality (measured by the Palma ratio) and environmental degradation (Ecological Footprint) across 17 Middle East and North Africa (MENA) countries from 2005 to 2020. 

## Methodology
This project employs a robust data engineering and econometric pipeline to resolve endogeneity and small-sample biases:
*   **Missing Data Imputation:** A K-Nearest Neighbors (KNN, K=3) algorithm is used to correct recording anomalies in structural macroeconomic indicators.
*   **Variable Transformation:** An Inverse Hyperbolic Sine (IHS) transformation is applied to Foreign Direct Investment to properly handle negative net inflows.
*   **Linear Baseline Model:** A Dynamic Fixed Effects (DFE) estimator is used to address the path-dependency of environmental degradation.
*   **Non-Linear Model:** A dynamic panel threshold regression utilizing Forward Orthogonal Deviations (FOD) is applied to identify endogenous structural breaks based on the level of economic development.

## Repository Structure
```text
├── data/
│   ├── raw/                 # Original WB and GFN data files
│   └── processed/           # Engineered and imputed panel dataset
├── results/
│   ├── figures/             # Output charts (Figure 1, Figure 2)
│   └── tables/              # Regression outputs (Table 3, Table 4)
├── src/
│   ├── 01_data_preprocessing.py
│   ├── 02_linear_baseline_dfe.py
│   ├── 03_nonlinear_threshold.py
│   └── 04_visualizations.py
├── .gitignore
├── requirements.txt
└── README.md
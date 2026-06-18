# Green Computing Final Project

## Overview
This repository contains the software code for the Green Computing final project for the Università di Milano-Bicocca. The goal of the project is to perform binary classification on tabular data derived from electronic health records (EHRs) while measuring and optimizing the project's environmental impact.

According to the project instructions, three distinct approaches are implemented and compared:
* A baseline Python script performing binary classification.
* An optimized Python script applying energy-saving strategies to consume less energy, CO2, and time.
* An R version of the script (`main_r.R`) to compare execution time, CO2-eq consumption, and energy use across different programming languages.

Classification performance is measured using the Matthews correlation coefficient (MCC) over a repeated hold-out validation with 100 iterations. The energy consumption (in Wh), CO2-eq emissions (in grams), and execution time (in seconds) are tracked using CodeCarbon.

## Repository Structure
* **`five_EHRs_public_datasets/`**: Directory containing the 5 tabular EHR datasets in CSV format (including neuroblastoma, pediatric brain tumors, colorectal cancer, sepsis, and depression/heart failure). The target feature to predict is always the last column on the right.
* **`main_base.py`**: The baseline Python script for the classification task.
* **`main_optimized.py`**: The energy-optimized Python script for the classification task.
* **`main_r.R`**: The R language implementation of the classification task.
* **`main_r_wrapper.py`**: A Python wrapper designed to track the R script's energy metrics using CodeCarbon.
* **`pipeline_utils.py` & `plot_results.py`**: Utility scripts containing helper functions and code to generate results plots.
* **Shell Scripts**: Scripts like `run_all.sh`, `run_base.sh`, `run_optimized.sh`, and `run_r.sh` are provided to automate the execution of the models.
* **`output/` & `results/`**: Folders containing the evaluation metrics in CSV format and generated graphical comparisons (e.g., `duration_comparison.png`, `emissions_comparison.png`, `energy_comparison.png`, `training_mcc_comparison.png`).
* **`.gitignore`**: Git exclusion rules.

## How to Run
You can run the entire evaluation pipeline or individual scripts using the provided bash scripts:
* Execute `./run_all.sh` to run the baseline, optimized, and R pipelines sequentially.
* Run `./run_base.sh`, `./run_optimized.sh`, or `./run_r.sh` to execute a specific pipeline and track its respective CodeCarbon footprint.
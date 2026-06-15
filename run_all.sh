#!/bin/bash
echo "Starting all scripts..."

bash run_base.sh
bash run_optimized.sh
bash run_r.sh
venv/bin/python plot_results.py
echo "All scripts have finished running!"

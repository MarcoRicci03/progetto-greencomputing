#!/bin/bash
echo "--- Running main_optimized.py ---"
if [ -d "venv" ]; then
    source venv/bin/activate
fi
python3 main_optimized.py

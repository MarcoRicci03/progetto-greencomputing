#!/bin/bash
echo "--- Running main_r.R ---"
docker build -t r-greencomputing .
if [ -d "venv" ]; then
    source venv/bin/activate
fi
python3 main_r_wrapper.py

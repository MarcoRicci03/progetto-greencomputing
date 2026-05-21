#!/bin/bash
echo "--- Running main_base.py ---"
if [ -d "venv" ]; then
    source venv/bin/activate
fi
python3 main_base.py

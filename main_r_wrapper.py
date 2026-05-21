import os
import subprocess
from codecarbon import OfflineEmissionsTracker

print("Starting CodeCarbon tracker for R (Docker)...")

tracker = OfflineEmissionsTracker(
    country_iso_code="ITA",
    project_name="green-computing-r",
    output_file="emissions_r.csv",
    output_dir="."
)  # ← parentesi chiusa!

tracker.start()

subprocess.run([
    "docker", "run", "--rm",
    "-v", f"{os.getcwd()}:/progetto",
    "r-greencomputing", "Rscript", "/progetto/main_r.R"
], check=True)  # ← check=True: solleva errore se R crasha

tracker.stop()
print("Done. Emissions saved to emissions_r.csv")
import subprocess

from codecarbon import OfflineEmissionsTracker

print("Starting CodeCarbon tracker for R...")

tracker = OfflineEmissionsTracker(
    country_iso_code="ITA",
    project_name="green-computing-r",
    output_file="emissions_r.csv",
    output_dir=".",
)

tracker.start()

try:
    subprocess.run(
        ["Rscript", "main_r.R"],
        check = True
    )
except subprocess.CalledProcessError as e:
    print(f"Error: R script failed with exit code {e.returncode}")
    raise
except FileNotFoundError:
    print("Error: 'Rscript' command not found. Is R installed and on PATH?")
    raise
finally:
    tracker.stop()

print("Done. Emissions saved to emissions_r.csv")
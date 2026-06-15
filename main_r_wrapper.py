import os
import subprocess
import time

from codecarbon import OfflineEmissionsTracker

print("Starting CodeCarbon tracker for R...")

tracker = OfflineEmissionsTracker(
    country_iso_code="ITA",
    project_name="green-computing-r",
    output_file="emissions_r.csv",
    output_dir=".",
)

start_time = time.time()
tracker.start()

try:
    """ subprocess.run(
        ["docker", "run", "--rm", "-v", PROJECT_MOUNT, DOCKER_IMAGE, "Rscript", R_SCRIPT_PATH],
        check=True,
    ) """

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

elapsed = time.time() - start_time
print(f"Total time: {elapsed:.2f} seconds")
print("Done. Emissions saved to emissions_r.csv")
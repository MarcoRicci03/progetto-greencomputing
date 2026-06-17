import os
import glob
import subprocess
from codecarbon import OfflineEmissionsTracker

DATASET_DIR = "five_EHRs_public_datasets/"
RESULTS_BASE_DIR = "results/"

print("Starting CodeCarbon tracker for R...")

pattern = os.path.join(DATASET_DIR, "*.csv")
dataset_files = glob.glob(pattern)

for csv_path in dataset_files:
    dataset_name = os.path.basename(csv_path).replace(".csv", "")
    print(f"\n--- Processing {dataset_name} with R ---")
    dataset_results_dir = os.path.join(RESULTS_BASE_DIR, dataset_name)
    os.makedirs(dataset_results_dir, exist_ok=True)
    tracker = OfflineEmissionsTracker(
        country_iso_code="ITA",
        project_name=f"green-computing-r-{dataset_name}",
        output_file="emissions_r.csv",
        output_dir=dataset_results_dir,
    )

    tracker.start()

    try:
        # Chiamiamo lo script R passando come argomenti il percorso del CSV e la cartella di output
        subprocess.run(
            ["Rscript", "main_r.R", csv_path, dataset_results_dir],
            check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"Errore: lo script R ha fallito su {dataset_name} con codice {e.returncode}")
    except FileNotFoundError:
        print("Errore: Comando 'Rscript' non trovato. R è installato e nel PATH?")
        tracker.stop()
        break
    finally:
        tracker.stop()

print("\nFinito! Le emissioni e i risultati R sono stati salvati nelle rispettive cartelle.")
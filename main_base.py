import os
from sklearn.ensemble import RandomForestClassifier
from codecarbon import OfflineEmissionsTracker

from pipeline_utils import get_dataset_files, run_pipeline_on_dataset, save_results

# ── Configuration ──────────────────────────────────────────────────────
DATASET_DIR = "five_EHRs_public_datasets/"
RESULTS_BASE_DIR = "results/"
N_RUNS = 100
TEST_SIZE = 0.2


def baseline_model(i: int) -> RandomForestClassifier:
    """Default RandomForest with iteration-specific random state."""
    return RandomForestClassifier(random_state=i)


# ── Main execution ────────────────────────────────────────────────────
if __name__ == "__main__":
    dataset_files = get_dataset_files(DATASET_DIR)
    
    for csv_path in dataset_files: 
        dataset_name = os.path.basename(csv_path).replace(".csv", "")
        dataset_results_dir = os.path.join(RESULTS_BASE_DIR, dataset_name)
        os.makedirs(dataset_results_dir, exist_ok=True)
        training_results_csv = os.path.join(dataset_results_dir, "training_results.csv")
        tracker = OfflineEmissionsTracker(
            country_iso_code="ITA",
            project_name=f"green-computing-py-base-{dataset_name}",
            output_file="emissions_base.csv",
            output_dir=dataset_results_dir,
        )

        tracker.start()

        result = run_pipeline_on_dataset(
            csv_path=csv_path,
            model_factory=baseline_model,
            n_runs=N_RUNS,
            test_size=TEST_SIZE,
        )

        tracker.stop()
        save_results([result], training_results_csv)
    
    print("Training completed! Emissions and duration are saved in 'emissions_base.csv'.")
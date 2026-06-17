import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import VarianceThreshold
from codecarbon import OfflineEmissionsTracker

from pipeline_utils import get_dataset_files, run_pipeline_on_dataset, save_results

# ── Configuration ──────────────────────────────────────────────────────
DATASET_DIR = "five_EHRs_public_datasets/"
RESULTS_BASE_DIR = "results/"
N_RUNS = 100
TEST_SIZE = 0.2


def optimized_model(i: int) -> RandomForestClassifier:
    """Lighter RandomForest: fewer trees, limited depth, parallel execution."""
    return RandomForestClassifier(
        n_estimators=30,
        max_depth=5,
        random_state=i,
    )


def remove_zero_variance(X):
    """Remove features with zero variance (applied once per dataset)."""
    selector = VarianceThreshold(threshold=0.0)
    return selector.fit_transform(X)


# ── Main execution ────────────────────────────────────────────────────
if __name__ == "__main__":
    dataset_files = get_dataset_files(DATASET_DIR)

    for csv_path in dataset_files:
        dataset_name = os.path.basename(csv_path).replace(".csv", "")
        dataset_results_dir = os.path.join(RESULTS_BASE_DIR, dataset_name)
        os.makedirs(dataset_results_dir, exist_ok=True)
        training_results_csv = os.path.join(dataset_results_dir, "training_results_optimized.csv")
        tracker = OfflineEmissionsTracker(
            country_iso_code="ITA",
            output_file="emissions_optimized.csv",
            output_dir=dataset_results_dir,
        )

        tracker.start()

        result = run_pipeline_on_dataset(
            csv_path=csv_path,
            model_factory=optimized_model,
            n_runs=N_RUNS,
            test_size=TEST_SIZE,
            preprocess_fn=remove_zero_variance,
        )

        tracker.stop()
        save_results([result], training_results_csv)
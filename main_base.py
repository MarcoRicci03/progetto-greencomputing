import time

from sklearn.ensemble import RandomForestClassifier
from codecarbon import OfflineEmissionsTracker

from pipeline_utils import run_pipeline_on_all_datasets, save_results

# ── Configuration ──────────────────────────────────────────────────────
DATASET_DIR = "five_EHRs_public_datasets/"
OUTPUT_CSV = "results/base_results.csv"
N_RUNS = 100
TEST_SIZE = 0.2


def baseline_model(i: int) -> RandomForestClassifier:
    """Default RandomForest with iteration-specific random state."""
    return RandomForestClassifier(random_state=i)


# ── Main execution ────────────────────────────────────────────────────
tracker = OfflineEmissionsTracker(
    country_iso_code="ITA",
    output_file="emissions_base.csv",
    output_dir=".",
)

start_time = time.time()
tracker.start()

results = run_pipeline_on_all_datasets(
    dataset_dir=DATASET_DIR,
    model_factory=baseline_model,
    n_runs=N_RUNS,
    test_size=TEST_SIZE,
)

tracker.stop()
elapsed = time.time() - start_time
print(f"Total time: {elapsed:.2f} seconds")

save_results(results, OUTPUT_CSV)

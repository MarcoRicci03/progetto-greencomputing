from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import VarianceThreshold
from codecarbon import OfflineEmissionsTracker

from pipeline_utils import run_pipeline_on_all_datasets, save_results

# ── Configuration ──────────────────────────────────────────────────────
DATASET_DIR = "five_EHRs_public_datasets/"
OUTPUT_CSV = "results/optimized_results.csv"
N_RUNS = 100
TEST_SIZE = 0.2


def optimized_model(i: int) -> RandomForestClassifier:
    """Lighter RandomForest: fewer trees, limited depth, parallel execution."""
    return RandomForestClassifier(
        n_estimators=30,
        max_depth=5,
        n_jobs=-1,
        random_state=i,
    )


def remove_zero_variance(X):
    """Remove features with zero variance (applied once per dataset)."""
    selector = VarianceThreshold(threshold=0.0)
    return selector.fit_transform(X)


# ── Main execution ────────────────────────────────────────────────────
tracker = OfflineEmissionsTracker(
    country_iso_code="ITA",
    project_name="green-computing-optimized",
    output_file="emissions_ottimizzato.csv",
    output_dir=".",
)

tracker.start()

results = run_pipeline_on_all_datasets(
    dataset_dir=DATASET_DIR,
    model_factory=optimized_model,
    preprocess_fn=remove_zero_variance,
    n_runs=N_RUNS,
    test_size=TEST_SIZE,
)

tracker.stop()

save_results(results, OUTPUT_CSV)
print("Training completato! I consumi e la durata sono salvati in 'emissions_optimized.csv'.")
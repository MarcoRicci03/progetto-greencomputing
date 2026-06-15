import os
import glob

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import matthews_corrcoef
from sklearn.preprocessing import LabelEncoder


def get_dataset_files(dataset_dir: str) -> list[str]:
    """Return sorted list of CSV file paths in ``dataset_dir``."""
    pattern = os.path.join(dataset_dir, "*.csv")
    files = sorted(glob.glob(pattern))
    if not files:
        raise FileNotFoundError(
            f"No CSV files found in '{dataset_dir}'. "
            "Check that the dataset directory exists and contains .csv files."
        )
    return files


def load_dataset(csv_path: str) -> tuple[np.ndarray, np.ndarray]:
    """Load a CSV and split into features (all cols except last) and target (last col)."""
    df = pd.read_csv(csv_path)
    X = df.iloc[:, :-1].values
    y = df.iloc[:, -1].values
    return X, y


def encode_target_if_needed(y: np.ndarray) -> np.ndarray:
    """Label-encode the target array if it contains non-numeric (object) values."""
    if y.dtype == object:
        le = LabelEncoder()
        y = le.fit_transform(y)
    return y


def run_repeated_holdout(
    X: np.ndarray,
    y: np.ndarray,
    model_factory,
    n_runs: int = 100,
    test_size: float = 0.2,
) -> list[float]:
    mccs = []
    for i in range(n_runs):
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=i
        )
        clf = model_factory(i)
        clf.fit(X_train, y_train)
        y_pred = clf.predict(X_test)
        mccs.append(matthews_corrcoef(y_test, y_pred))
    return mccs


def run_pipeline_on_all_datasets(
    dataset_dir: str,
    model_factory,
    preprocess_fn=None,
    n_runs: int = 100,
    test_size: float = 0.2,
) -> list[dict]:
    dataset_files = get_dataset_files(dataset_dir)
    all_results = []

    for csv_path in dataset_files:
        dataset_name = os.path.basename(csv_path).replace(".csv", "")
        print(f"Processing dataset: {dataset_name}")

        X, y = load_dataset(csv_path)
        y = encode_target_if_needed(y)

        if preprocess_fn is not None:
            X = preprocess_fn(X)

        mccs = run_repeated_holdout(X, y, model_factory, n_runs, test_size)

        mean_mcc = np.mean(mccs)
        std_mcc = np.std(mccs)
        all_results.append({
            "dataset": dataset_name,
            "mean_mcc": mean_mcc,
            "std_mcc": std_mcc,
        })
        print(f"{dataset_name}: MCC = {mean_mcc:.4f} ± {std_mcc:.4f}")

    return all_results


def save_results(results: list[dict], output_csv: str) -> None:
    """Save aggregated results to a CSV file, creating directories as needed."""
    output_dir = os.path.dirname(output_csv)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    pd.DataFrame(results).to_csv(output_csv, index=False)
    print(f"Results saved to {output_csv}")

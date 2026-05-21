import os
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import matthews_corrcoef
from sklearn.preprocessing import LabelEncoder
from sklearn.feature_selection import VarianceThreshold
from codecarbon import OfflineEmissionsTracker
import time
import glob

DATASET_DIR = "five_EHRs_public_datasets/"
dataset_files = sorted(glob.glob(os.path.join(DATASET_DIR, "*.csv")))

tracker = OfflineEmissionsTracker(
    country_iso_code="ITA",
    project_name="green-computing-optimized",
    output_file="emissions_ottimizzato.csv",
    output_dir="."
)

start_time = time.time()
tracker.start()

all_results = []

for csv_path in dataset_files:
    dataset_name = os.path.basename(csv_path).replace(".csv", "")
    print(f"Processing dataset: {dataset_name}")
    df = pd.read_csv(csv_path)

    X = df.iloc[:, :-1].values
    y = df.iloc[:, -1].values

    if y.dtype == object:
        le = LabelEncoder()
        y = le.fit_transform(y)

    selector = VarianceThreshold(threshold=0.0)
    X = selector.fit_transform(X)
    mccs = []
    for i in range(100):
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=i
        )
        clf = RandomForestClassifier(
            n_estimators=30,
            max_depth=5,
            n_jobs=-1,
            random_state=i
        )
        clf.fit(X_train, y_train)
        y_pred = clf.predict(X_test)
        mccs.append(matthews_corrcoef(y_test, y_pred))

    all_results.append({
        "dataset": dataset_name,
        "mean_mcc": np.mean(mccs),
        "std_mcc": np.std(mccs),
    })
    print(f"{dataset_name}: MCC = {np.mean(mccs):.4f} ± {np.std(mccs):.4f}")

tracker.stop()
elapsed = time.time() - start_time

os.makedirs("results", exist_ok=True)
pd.DataFrame(all_results).to_csv("results/optimized_results.csv", index=False)
import os
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import matthews_corrcoef
from sklearn.preprocessing import LabelEncoder
from codecarbon import OfflineEmissionsTracker
import numpy as np
import time
import glob
import os

DATASET_DIR = "five_EHRs_public_datasets/"
dataset_files = sorted(glob.glob(os.path.join(DATASET_DIR, "*.csv")))

tracker = OfflineEmissionsTracker(
    country_iso_code="ITA", 
    output_file="emissions_base.csv", 
    output_dir="."
)

start_time = time.time()
tracker.start()

all_results = []

for csv_path in dataset_files:
    dataset_name = os.path.basename(csv_path).replace(".csv", "")
    print(f"Processing dataset: {dataset_name}")
    df = pd.read_csv(csv_path)

    X = df.iloc[:, :-1].values   # all columns except the last one
    y = df.iloc[:, -1].values    # last column = target

    # Convert target to numbers if it is text
    if y.dtype == object:
        le = LabelEncoder()
        y = le.fit_transform(y)

    mccs = []
    for i in range(100):  # repeated hold-out
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=i
        )
        clf = RandomForestClassifier(random_state=i)
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
print(f"Total time: {elapsed:.2f} seconds")

os.makedirs("results", exist_ok=True)
pd.DataFrame(all_results).to_csv("results/base_results.csv", index=False) 

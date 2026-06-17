from __future__ import annotations

from pathlib import Path
import re
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="whitegrid")

RESULTS_DIR = Path("results")
OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

TRAINING_FILES = {
    "training_results.csv": "Base",
    "training_results_optimized.csv": "Optimized",
    "training_results_r.csv": "R",
}

EMISSIONS_FILES = {
    "emissions_base.csv": "Base",
    "emissions_optimized.csv": "Optimized",
    "emissions_r.csv": "R",
}


def prettify_dataset_name(raw: str) -> str:
    # Mappa manuale per rinominare i dataset come preferisci
    name_mapping = {
        "dataset_Belgrade2021_pediatric_brain_tumor_plos_one_0259095_cleaned": "Pediatric Brain Tumor",
        "journal.pone.0158570_S2File_depression_heart_failure": "Depression Heart Failure",
        "journal.pone.0148699_S1_Text_Sepsis_SIRS_EDITED": "Sepsis SIRS",
        "10_7717_peerj_5665_dataYM2018_neuroblastoma": "Neuroblastoma",
        "dataset_Taipei2018_colorectal_cancer_EHRs_plos_one_0200893_final_cleaned": "Colorectal Cancer",
    }
    
    # Se il nome è nel dizionario, usa il nome pulito
    if raw in name_mapping:
        return name_mapping[raw]
    
    # Fallback alla pulizia automatica (se trovi altri dataset in futuro)
    name = Path(raw).name
    name = re.sub(r"^\d+_", "", name)
    name = re.sub(r"^dataset_", "", name)
    name = re.sub(r"^journal\.", "", name)
    name = re.sub(r"_cleaned$", "", name)
    name = name.replace("_", " ")
    name = re.sub(r"\s+", " ", name).strip()
    return name.title()


def find_csv_files(root: Path, filename: str):
    return sorted(root.rglob(filename))


def load_training_results(root: Path) -> pd.DataFrame:
    rows = []
    for filename, variant in TRAINING_FILES.items():
        for csv_path in find_csv_files(root, filename):
            dataset_dir = csv_path.parent.name
            df = pd.read_csv(csv_path)
            df.columns = [c.strip() for c in df.columns]
            if "dataset" not in df.columns:
                df["dataset"] = dataset_dir
            df["dataset_raw"] = dataset_dir
            df["dataset_label"] = df["dataset_raw"].map(prettify_dataset_name)
            df["variant"] = variant
            rows.append(df)
    if not rows:
        raise FileNotFoundError("Nessun file training_results trovato dentro results/")
    return pd.concat(rows, ignore_index=True)


def load_emissions_results(root: Path) -> pd.DataFrame:
    rows = []
    for filename, variant in EMISSIONS_FILES.items():
        for csv_path in find_csv_files(root, filename):
            dataset_dir = csv_path.parent.name
            df = pd.read_csv(csv_path)
            df.columns = [c.strip() for c in df.columns]
            df["dataset_raw"] = dataset_dir
            df["dataset_label"] = df["dataset_raw"].map(prettify_dataset_name)
            df["variant"] = variant
            rows.append(df)
    if not rows:
        raise FileNotFoundError("Nessun file emissions trovato dentro results/")
    return pd.concat(rows, ignore_index=True)


def save_training_plot(training_df: pd.DataFrame):
    plot_df = training_df.copy()
    plot_df = plot_df.sort_values(["dataset_label", "variant"])

    plt.figure(figsize=(14, 7))
    ax = sns.barplot(
        data=plot_df,
        x="dataset_label",
        y="mean_mcc",
        hue="variant",
        palette="Set2",
        errorbar=None,
    )

    if "std_mcc" in plot_df.columns:
        hue_order = [t.get_text() for t in ax.legend_.texts] if ax.legend_ else sorted(plot_df["variant"].unique())
        containers = ax.containers
        idx = 0
        for container in containers:
            for bar in container:
                if idx >= len(plot_df):
                    break
                row = plot_df.iloc[idx]
                x = bar.get_x() + bar.get_width() / 2
                y = bar.get_height()
                err = row.get("std_mcc", 0)
                if pd.notna(err):
                    ax.errorbar(x, y, yerr=err, fmt="none", ecolor="black", capsize=4, lw=1)
                idx += 1

    ax.set_title("Mean MCC per dataset e variante")
    ax.set_xlabel("Dataset")
    ax.set_ylabel("Mean MCC")
    plt.xticks(rotation=25, ha="right")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "training_mcc_comparison.png", dpi=200, bbox_inches="tight")
    plt.close()


def save_emissions_plots(emissions_df: pd.DataFrame):
    metrics = [
        ("duration", "Duration (s)", "duration_comparison.png"),
        ("energy_consumed", "Energy consumed (kWh)", "energy_comparison.png"),
        ("emissions", "Emissions (kg CO2eq)", "emissions_comparison.png"),
    ]

    for column, ylabel, filename in metrics:
        if column not in emissions_df.columns:
            continue
        plot_df = emissions_df.copy().sort_values(["dataset_label", "variant"])
        plt.figure(figsize=(14, 7))
        ax = sns.barplot(
            data=plot_df,
            x="dataset_label",
            y=column,
            hue="variant",
            palette="Set2",
            estimator="mean",
            errorbar=None,
        )
        ax.set_title(f"{ylabel} per dataset e variante")
        ax.set_xlabel("Dataset")
        ax.set_ylabel(ylabel)
        plt.xticks(rotation=25, ha="right")
        plt.tight_layout()
        plt.savefig(OUTPUT_DIR / filename, dpi=200, bbox_inches="tight")
        plt.close()


def save_label_mapping(training_df: pd.DataFrame, emissions_df: pd.DataFrame):
    labels = pd.concat([
        training_df[["dataset_raw", "dataset_label"]],
        emissions_df[["dataset_raw", "dataset_label"]],
    ], ignore_index=True).drop_duplicates().sort_values("dataset_label")
    labels.to_csv(OUTPUT_DIR / "dataset_labels.csv", index=False)


def main():
    training_df = load_training_results(RESULTS_DIR)
    emissions_df = load_emissions_results(RESULTS_DIR)

    save_training_plot(training_df)
    save_emissions_plots(emissions_df)
    save_label_mapping(training_df, emissions_df)

    training_df.to_csv(OUTPUT_DIR / "training_results_merged.csv", index=False)
    emissions_df.to_csv(OUTPUT_DIR / "emissions_results_merged.csv", index=False)

    print("Script pronto. File generati in output/")


if __name__ == "__main__":
    main()
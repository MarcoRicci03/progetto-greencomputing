import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import os

# --- Load results ---
base_res  = pd.read_csv("results/base_results.csv")
optim_res = pd.read_csv("results/optimized_results.csv")
r_res     = pd.read_csv("results/r_results.csv")

# --- Load emissions (last row = most recent run) ---
def load_emissions(path):
    try:
        row = pd.read_csv(path).iloc[-1]
        return {
            "energy_wh":  float(row["energy_consumed"]) * 1000,  # kWh -> Wh
            "co2_g":      float(row["emissions"]) * 1000,         # kg  -> g
            "duration_s": float(row["duration"]),
        }
    except FileNotFoundError:
        print(f"Warning: {path} not found — using zeros.")
        return {"energy_wh": 0, "co2_g": 0, "duration_s": 0}

base_emis  = load_emissions("emissions_base.csv")
optim_emis = load_emissions("emissions_ottimizzato.csv")
r_emis     = load_emissions("emissions_r.csv")

labels = ["Base (Py)", "Optimized (Py)", "R (Docker)"]
colors = ["#e05c5c", "#4caf82", "#2196F3"]

energia = [base_emis["energy_wh"],  optim_emis["energy_wh"],  r_emis["energy_wh"]]
co2     = [base_emis["co2_g"],      optim_emis["co2_g"],      r_emis["co2_g"]]
durata  = [base_emis["duration_s"], optim_emis["duration_s"], r_emis["duration_s"]]

# --- MCC per dataset (mean ± std) ---
# Merge on dataset name for aligned comparison
mcc_merged = (
    base_res.rename(columns={"mean_mcc": "mcc_base", "std_mcc": "std_base"})
    .merge(optim_res.rename(columns={"mean_mcc": "mcc_optim", "std_mcc": "std_optim"}), on="dataset")
    .merge(r_res.rename(columns={"mean_mcc": "mcc_r", "std_mcc": "std_r"}), on="dataset")
)
# Shorten dataset names for readability
mcc_merged["short_name"] = mcc_merged["dataset"].str[:30]

# --- Layout ---
fig = plt.figure(figsize=(16, 10))
fig.suptitle("Green Computing — Performance & Emissions Comparison", fontsize=16, fontweight="bold", y=0.99)

ax1 = plt.subplot(2, 3, 1)
ax2 = plt.subplot(2, 3, 2)
ax3 = plt.subplot(2, 3, 3)
ax4 = plt.subplot(2, 1, 2)

# --- Bar charts for emissions ---
def bar_chart(ax, vals, title, unit, fmt):
    bars = ax.bar(labels, vals, color=colors, width=0.5, edgecolor="black", linewidth=0.8)
    ax.set_title(title, fontsize=11, fontweight="bold", pad=8)
    ax.set_ylabel(unit, fontsize=9)
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(axis="x", labelsize=9)
    for bar, val in zip(bars, vals):
        label_y = bar.get_height() * 1.03
        label_txt = fmt.format(val) if val > 0 else "N/A"
        color_txt = "black" if val > 0 else "grey"
        ax.text(bar.get_x() + bar.get_width() / 2, label_y,
                label_txt, ha="center", va="bottom", fontsize=9,
                fontweight="bold", color=color_txt)
    ax.set_ylim(0, max(vals) * 1.3 if max(vals) > 0 else 1)

bar_chart(ax1, energia, "Energy (Wh)",     "Wh",  "{:.4f}")
bar_chart(ax2, co2,     "CO₂-eq (g)",      "g",   "{:.6f}")
bar_chart(ax3, durata,  "Total Time (sec)","sec",  "{:.1f}")

# --- MCC per dataset grouped bar chart with error bars ---
datasets = mcc_merged["short_name"].tolist()
x = np.arange(len(datasets))
width = 0.25

bars_b = ax4.bar(x - width, mcc_merged["mcc_base"],  width, yerr=mcc_merged["std_base"],
                 label="Base (Py)",       color=colors[0], alpha=0.85,
                 capsize=4, error_kw={"elinewidth":1.2, "ecolor":"#555"}, edgecolor="black", linewidth=0.6)
bars_o = ax4.bar(x,          mcc_merged["mcc_optim"], width, yerr=mcc_merged["std_optim"],
                 label="Optimized (Py)", color=colors[1], alpha=0.85,
                 capsize=4, error_kw={"elinewidth":1.2, "ecolor":"#555"}, edgecolor="black", linewidth=0.6)
bars_r = ax4.bar(x + width,  mcc_merged["mcc_r"],     width, yerr=mcc_merged["std_r"],
                 label="R (Docker)",     color=colors[2], alpha=0.85,
                 capsize=4, error_kw={"elinewidth":1.2, "ecolor":"#555"}, edgecolor="black", linewidth=0.6)

ax4.set_title("MCC per Dataset — Mean ± Std over 100 Repeated Hold-Out Runs",
              fontsize=12, fontweight="bold")
ax4.set_ylabel("Matthews Correlation Coefficient (MCC)", fontsize=10)
ax4.set_xticks(x)
ax4.set_xticklabels(datasets, fontsize=7, rotation=30, ha="right")
ax4.set_ylim(0, 1.15)
ax4.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.2f"))
ax4.spines[["top", "right"]].set_visible(False)
ax4.legend(fontsize=10, framealpha=0.7)
ax4.axhline(0, color="black", linewidth=0.5)

plt.tight_layout(rect=[0, 0, 1, 0.97])
os.makedirs("results", exist_ok=True)
out_path = "confronto_risultati.png"
plt.savefig(out_path, dpi=150, bbox_inches="tight")
print(f"Saved: {out_path}")
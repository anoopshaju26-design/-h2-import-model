"""Run the model: table, cost-vs-distance chart, results CSV."""

import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

sys.path.insert(0, "src")
from model import count_placeholders, delivered_cost, load_inputs  # noqa: E402

DISTANCE_KM = 5000  # example distance for the comparison table
DISTANCES = list(range(500, 15001, 500))

params, chains, glob = load_inputs("data")

n = count_placeholders(glob, chains)
if n:
    print(f"WARNING: {n} input rows are still PLACEHOLDERS. Results are not real.\n")

rows = []
for name, steps in chains.groupby("chain"):
    for d in DISTANCES:
        cost, parts = delivered_cost(steps, d, params)
        rows.append({"chain": name, "distance_km": d, "cost_eur_per_mwh": cost, **parts})
results = pd.DataFrame(rows)
results.to_csv("results/cost_by_distance.csv", index=False)

print(f"Delivered cost at {DISTANCE_KM} km (EUR per MWh H2)")
at = results[results["distance_km"] == DISTANCE_KM]
for _, r in at.iterrows():
    print(f"  {r['chain']:<18} {r['cost_eur_per_mwh']:8.1f}")

fig, ax = plt.subplots()
for name, grp in results.groupby("chain"):
    ax.plot(grp["distance_km"], grp["cost_eur_per_mwh"], label=name)
ax.set_xlabel("Distance (km)")
ax.set_ylabel("Delivered cost (EUR per MWh H2)")
title = "Delivered cost vs distance"
ax.set_title(title + (" (PLACEHOLDER inputs)" if n else ""))
ax.legend()
ax.grid(alpha=0.3)
fig.savefig("results/cost_vs_distance.png", dpi=150, bbox_inches="tight")
print("Saved results/cost_by_distance.csv and results/cost_vs_distance.png")

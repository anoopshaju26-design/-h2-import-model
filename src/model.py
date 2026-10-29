"""Core cost model for hydrogen supply chains.

Energy basis: MWh of hydrogen, lower heating value (LHV).

Idea: start with 1 MWh of H2 produced, pass it through the steps of a chain.
Conversion steps lose energy (efficiency) and add cost (EUR per MWh entering).
Transport steps lose a share per 1000 km and add cost per MWh per 1000 km.
Delivered cost = total cost / energy that arrives.
"""

import pandas as pd


def load_inputs(data_dir="data"):
    glob = pd.read_csv(f"{data_dir}/global_inputs.csv")
    chains = pd.read_csv(f"{data_dir}/chains.csv")
    params = dict(zip(glob["key"], glob["value"].astype(float)))
    return params, chains, glob


def count_placeholders(*tables):
    """How many input rows are still unsourced placeholders."""
    return sum((t["status"] == "PLACEHOLDER").sum() for t in tables)


def annuity_factor(rate, years):
    """Share of the investment paid per year (interest + repayment)."""
    return rate * (1 + rate) ** years / ((1 + rate) ** years - 1)


def hydrogen_production_cost(p):
    """Levelised cost of electrolytic hydrogen, EUR per MWh H2."""
    af = annuity_factor(p["interest_rate"], p["lifetime_years"])
    capex_per_mwh_el = p["electrolyser_capex"] * 1000 * af / p["full_load_hours"]
    opex_per_mwh_el = (
        p["electrolyser_capex"] * 1000 * p["opex_fraction_of_capex"] / p["full_load_hours"]
    )
    cost_per_mwh_el = capex_per_mwh_el + opex_per_mwh_el + p["electricity_price"]
    return cost_per_mwh_el / p["electrolyser_efficiency"]


def delivered_cost(chain_steps, distance_km, p):
    """Return (delivered cost EUR/MWh, breakdown dict) for one chain."""
    energy = 1.0
    prod_cost = hydrogen_production_cost(p)
    breakdown = {"Production": prod_cost}
    d = distance_km / 1000

    for _, step in chain_steps.sort_values("order").iterrows():
        if step["type"] == "conversion":
            breakdown[step["step"]] = step["cost_per_mwh_in"] * energy
            energy *= step["efficiency"]
        elif step["type"] == "transport":
            breakdown[step["step"]] = step["cost_per_mwh_per_1000km"] * d * energy
            energy *= (1 - step["loss_per_1000km"]) ** d
        else:
            raise ValueError(f"Unknown step type: {step['type']}")

    total = sum(breakdown.values())
    # Express each part per MWh delivered so the parts add up to delivered cost
    per_delivered = {k: v / energy for k, v in breakdown.items()}
    return total / energy, per_delivered

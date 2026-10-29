# Hydrogen Import Cost Model

A simple Python model that compares the **delivered cost of hydrogen** (and hydrogen
carriers) to Germany for different supply chains and distances.

**Status: work in progress.** 7 of 12 input values are sourced. The 5 supply-chain
rows in `data/chains.csv` are still placeholders (see the `status` column), so results
are not yet meaningful. The script prints a warning while placeholders remain.

## Question

Which supply chain is cheapest for a given distance: compressed hydrogen by pipeline,
ammonia by ship (with cracking back to hydrogen), and later liquid hydrogen and DME?

## How the model works

Start with 1 MWh of hydrogen (LHV). Pass it through each step of a chain:

- **Conversion step:** energy out = energy in x efficiency; adds cost per MWh entering.
- **Transport step:** loses a share of energy per 1000 km; adds cost per MWh per 1000 km.
- **Production:** electrolysis cost from annualised capex (annuity factor), opex and
  electricity price.

Delivered cost = total cost / energy that arrives (EUR per MWh H2).

## Project structure

    data/global_inputs.csv   finance and electrolysis inputs (with source column)
    data/chains.csv          one row per step of each supply chain (with source column)
    src/model.py             model functions
    run.py                   runs the model, writes results/ and a chart
    results/                 generated outputs

## Run

    pip install -r requirements.txt
    python run.py

## Add a new supply chain

Add rows to `data/chains.csv` (same chain name, increasing `order`). Use
`type = conversion` with `efficiency` and `cost_per_mwh_in`, or `type = transport` with
`loss_per_1000km` and `cost_per_mwh_per_1000km`. No code change needed.

## Assumptions and limits (update as the project grows)

- Single production cost for all chains; no country differences yet.
- Energy basis is LHV throughout.
- Costs are simplified per-step values, not full plant designs.
- No CO2 supply modelled (needed for DME).
- Results show relative differences, not exact prices.

## Roadmap

- [x] Source global inputs (electrolysis and finance)
- [ ] Source supply-chain inputs in `chains.csv`
- [ ] Add liquid hydrogen and DME chains
- [ ] Add exporting countries with different electricity costs
- [ ] Low / base / high scenarios and sensitivity chart
- [ ] Cost-breakdown chart per chain

## Sources

Global inputs (`data/global_inputs.csv`); full details are in the `source` column:

- IRENA (2026), Renewable Power Generation Costs in 2025 (electricity price)
- ACER CHEST dataset based on IEA Global Hydrogen Review 2025 (electrolyser capex)
- Enagas, electrolysis technology summary report, Dec 2025, citing IEA (efficiency)
- Aurecon, 2024 Energy Technology Cost and Technical Parameter Review (lifetime, O&M)
- NESO, capex and opex input assumptions for PEM and alkaline electrolysers (lifetime)
- German hydrogen strategy planning assumptions; Fraunhofer policy brief (full-load hours)
- Techno-economic and environmental assessment of renewable hydrogen import routes
  from overseas in 2030; Griffith University 2024; IRENA 2020 (interest rate / WACC)
- ECB reference rate, 15 Oct 2026 (USD to EUR conversion)

Supply-chain inputs (`data/chains.csv`): still to be sourced.

## Known simplifications

- One interest rate for all projects; real WACC differs by country.
- Electrolyser stack replacement is not modelled.
- Electricity price is a global average, not a specific site.

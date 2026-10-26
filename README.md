# Dengue Risk Profiling and LGU Prioritization in Metro Manila

A Panel Regression Approach — Capstone 2 (MO-IT200D2, Section A4103, Group 1)
Mapúa Malayan Digital College · BS Information Technology, Major in Data Analytics

An annual dengue analytics and prioritization prototype for the 17 Metro Manila local government units (LGUs), built on 2021–2025 DOH dengue case records and PSA population data. A Python pipeline cleans and merges the data, computes incidence indicators, fits a Negative Binomial regression, and applies a predefined Priority / Watch / Stable rule. Results are exported as CSV files that feed an interactive Tableau dashboard.

> **Scope.** This is a supplementary research prototype. It does not forecast cases, predict outbreaks, or establish causation, and it does not replace official DOH surveillance.

## Authors

Rania Nabil M. Abdelfattah · Martin Sheen C. Cajucom · Chadley Marie V. De Lara · Karissa Mae N. Manicad

Adviser: John Edmon Alcomendas

## Data

| Data | Source | Notes |
|---|---|---|
| Annual dengue cases per LGU, 2021–2025; NCR age and sex counts | DOH–MMCHD, via Freedom of Information request | 17 LGUs × 5 years = 85 LGU-year observations |
| Population (2020, 2024 census) and land area | Philippine Statistics Authority | 2021–2023 interpolated, 2024 official, 2025 extrapolated |

Every population value carries a status flag (`official`, `interpolated`, or `extrapolated`). All 2025 values are lower-confidence estimates. Age and sex data exist only at the NCR level, so they are used for description and never enter the regression.

Raw source files are preserved unmodified. All cleaning is done programmatically on copies.

## Method in brief

1. **Validate and merge.** Standardize LGU names, reconcile LGU case sums to the FOI NCR totals (10,493 / 43,753 / 23,678 / 37,225 / 45,014 for 2021–2025), and build the 85-row panel.
2. **Descriptive indicators.** Incidence per 100,000, year-over-year change, five-year average incidence, and 2025 incidence versus each LGU's own average.
3. **Poisson baseline.** Used as a diagnostic. The overdispersion index is 198.95, which justifies Negative Binomial.
4. **Negative Binomial regression (NB2).** Dengue cases ~ population density (per 1,000 persons/km²) + year effects (2021 as reference), with log(population) as the exposure offset and LGU-clustered standard errors.
5. **Structural risk ranking.** Each LGU's model-fitted incidence per 100,000, averaged over 2021–2025.
6. **Priority rule.** An LGU is **Priority** if it is in the top third of the structural risk ranking (ranks 1–6) *and* its 2025 incidence is at or above its five-year average. **Watch** if exactly one condition holds. **Stable** if neither does.
7. **Validation.** Deviance residuals, Cook's distance, leave-one-LGU-out refits, a sensitivity run without 2025, Makati–Taguig boundary sensitivity checks, and grouped cross-validation against a Random Forest.

## Key results

- Reported cases rose from 10,493 (2021) to 43,753 (2022), fell in 2023, and reached 45,014 in 2025. 13 of 17 LGUs ended 2025 at or above their own five-year average.
- Population density showed a small negative association with incidence (IRR 0.9935 per 1,000 persons/km²) that was **not statistically significant** with clustered standard errors (p = 0.1296). The finding is fragile: it becomes significant when 2025 is excluded (p = 0.034) or when Manila is omitted (p = 0.002). The density result should be treated as inconclusive.
- Year effects are large and significant (2022 incidence is about 4.1 times the 2021 level).
- The rule produced **4 Priority** LGUs (Muntinlupa, Parañaque, Makati, Pasig), **11 Watch**, and **2 Stable** (Malabon, Taguig).
- Makati's tier is sensitive to the population denominators used. It moves from Priority to Watch under the boundary-adjusted scenario. The adjusted scenario is reported as a sensitivity check and does not replace the primary data.
- Because density is the only LGU-level predictor, the structural ranking is almost the reverse of density order (Spearman −0.99). The observed-incidence condition is the more dependable half of the rule, so always read tiers alongside the values that produced them.
- User acceptance testing (15 respondents): overall mean 4.20 / 5 (4.08 excluding two respondents who rated every item 5).

## Repository layout

```
notebooks/   Jupyter notebooks, one per pipeline stage
             05_negative_binomial_regression.ipynb — NB model, diagnostics,
             sensitivity analyses, risk ranking, priority tiers, CSV export
src/         Reusable functions (e.g. src/priority.py: assign_priority_tier)
data/        Raw, cleaned, and validated data
             04_validated/lgu_year_panel.csv — the 85-row analysis panel
outputs/     Dashboard-ready CSV exports (sole data source for Tableau)
docs/        data_dictionary.md and supporting documentation
tests/       pytest suite
```

## Outputs

`notebooks/05_negative_binomial_regression.ipynb` writes three files to `outputs/`:

| File | Contents |
|---|---|
| `lgu_structural_risk_ranking.csv` | Risk rank, structural risk score, mean population density per LGU |
| `lgu_priority_flags.csv` | Rank, score, 2025 incidence, five-year average, both rule conditions, and the Priority / Watch / Stable tier |
| `lgu_year_nb_model_output.csv` | LGU-year cases, population, density, incidence, and NB-predicted cases and incidence |

Every tier can be verified by hand from `lgu_priority_flags.csv` without refitting the model.

## Setup and reproduction

Requires Python 3 with `pandas`, `numpy`, `statsmodels`, `scikit-learn`, and `pytest`.

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS / Linux
pip install pandas numpy statsmodels scikit-learn pytest jupyter
```

Run the notebooks in order, using Restart Kernel and Run All, to regenerate the panel and the CSVs in `outputs/`. Run the tests with:

```bash
pytest
```

The suite has 128 tests covering name standardization, population estimation, panel construction, descriptive indicators, age/sex summaries, data validation, the Poisson/NB specification, structural risk ranking, and the priority rule.

## Dashboard

The Tableau dashboard reads only the CSVs in `outputs/`. It shows an incidence choropleth with a year selector, annual trends, the structural risk ranking, Priority / Watch / Stable classifications with their underlying values, and an NCR-level age and sex panel. Only the five observed years appear; no projections are shown.

Dashboard link: https://public.tableau.com/app/profile/karissa.mae.manicad4435/viz/DengueRiskandPrioritizationDashboard/DengueRiskandPrioritizationDashboard

## Limitations

- Only five annual observations per LGU, so no time-series, seasonality, or forecasting.
- Population for 2021–2023 and 2025 is estimated; 2025 rests on extrapolation.
- The Makati–Taguig barangay transfer cannot be corrected in the primary data because case counts are not available at barangay level.
- A single predictor across 17 LGUs gives limited statistical power; clustered standard errors with 17 clusters are approximate.
- No climate or environmental variables.
- Usability testing involved only four respondents working in public health practice.

## Data privacy

Only aggregated, de-identified secondary data from DOH–MMCHD and PSA are used, in line with the Data Privacy Act of 2012 (RA 10173).

## Acknowledgements

Thanks to DOH–MMCHD for the FOI data release and to the Philippine Statistics Authority for its public census data.

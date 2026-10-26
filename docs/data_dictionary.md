# Data Dictionary

Covers `data/04_validated/lgu_year_panel.csv` (the 85-row LGU-year analytical
panel), its upstream component `data/03_processed/population_panel.csv`, and the
derived indicator columns exported to `outputs/dashboard_exports/`.

---

## Panel variables

### LGU
- **Meaning:** One of the 17 cities/municipalities of Metro Manila (NCR)
- **Source:** DOH–MMCHD (FOI) / PSA
- **Unit:** categorical
- **Transformation:** Standardized to a canonical short form via `src/lgu_names.py` (handles PSA official form, suffixes, the Kalookan variant, and missing tildes)
- **Analytical role:** Panel identifier / geographic unit
- **Status tag:** official

### Year
- **Meaning:** Calendar year of observation
- **Source:** DOH–MMCHD (FOI) / PSA
- **Unit:** categorical, 2021–2025
- **Transformation:** None
- **Analytical role:** Time index for the panel
- **Status tag:** official

### Dengue Cases
- **Meaning:** Total annual dengue case count for the LGU-year
- **Source:** DOH–MMCHD (via FOI)
- **Unit:** count
- **Transformation:** None — reported as released
- **Analytical role:** Dependent variable in the NB/Poisson regression; basis for incidence rate
- **Status tag:** official

### Population
- **Meaning:** Estimated total population for the LGU-year
- **Source:** PSA 2020 Census (anchor) and PSA 2024 POPCEN (anchor); 2021–2023 and 2025 derived
- **Unit:** count
- **Transformation:** 2020, 2024 — taken directly from the PSA reference datasets used in the project. 2021–2023 — linear interpolation between the 2020 and 2024 anchors. 2025 — linear extrapolation using the same annual change beyond the 2024 anchor
- **Analytical role:** Exposure/offset term in the regression; denominator for incidence rate and density
- **Status tag:** official (2020, 2024) / interpolated (2021–2023) / extrapolated (2025)

### Land Area
- **Meaning:** Fixed land area of the LGU used in the analytical dataset
- **Source:** PSA land-area reference used in the project
- **Unit:** km²
- **Transformation:** None — the land-area values available in the project's reference datasets were carried forward unchanged across all five analytical years
- **Analytical role:** Denominator for population density
- **Status tag:** official
- **Limitation:** For Makati and Taguig, the fixed land-area values used in the analytical dataset do not account for the administrative boundary change involving the transfer of 10 barangays from Makati to Taguig during the study period. See the Makati–Taguig Geographic Boundary Limitation below.

### Population Density
- **Meaning:** Population per square kilometre for the LGU-year
- **Source:** Computed
- **Unit:** persons/km²
- **Transformation:** `Population ÷ Land Area`, recomputed for every year using that year's estimated population
- **Analytical role:** Primary structural predictor in the NB/Poisson regression
- **Status tag:** computed (inherits the status of the Population value used)

### Incidence Rate
- **Meaning:** Dengue cases per 100,000 population for the LGU-year
- **Source:** Computed
- **Unit:** cases per 100,000
- **Transformation:** `Dengue Cases ÷ Population × 100,000`
- **Analytical role:** Descriptive indicator for cross-LGU comparison; basis for the five-year-average trend indicator
- **Status tag:** computed (inherits the status of the Population value used)

### Previous Year Incidence
- **Meaning:** The same LGU's incidence rate in the preceding year
- **Source:** Computed
- **Unit:** cases per 100,000
- **Transformation:** Incidence Rate shifted by one year within the LGU, after sorting by LGU then Year. Empty for 2021, which has no prior year in the panel
- **Analytical role:** Denominator of the year-over-year change; carried in the export so the change can be audited without a second lookup
- **Status tag:** computed

### YoY % Change
- **Meaning:** Percent change in incidence against the same LGU's previous year
- **Source:** Computed
- **Unit:** percent
- **Transformation:** `(Incidence Rate - Previous Year Incidence) / Previous Year Incidence × 100`. Always within one LGU, never across LGUs. Empty for 2021
- **Analytical role:** Descriptive year-on-year movement for the trend view of the dashboard
- **Status tag:** computed (inherits the status of the two Population values used)

### Five-Year Average Incidence
- **Meaning:** The LGU's own mean incidence across 2021–2025
- **Source:** Computed
- **Unit:** cases per 100,000
- **Transformation:** Plain mean of that LGU's five annual incidence values, broadcast to all five of its rows
- **Analytical role:** Within-LGU benchmark; the 2025 comparison against it is the second condition of the three-tier priority rule
- **Status tag:** computed

### At or Above Average
- **Meaning:** Whether the LGU's 2025 incidence is at or above its own five-year average
- **Source:** Computed
- **Unit:** boolean
- **Transformation:** `2025 Incidence >= Five-Year Average Incidence`, evaluated on unrounded values
- **Analytical role:** Second of the two conditions in the three-tier priority rule. Present in `outputs/dashboard_exports/lgu_summary_2025.csv` at LGU grain, not in the LGU-year panel
- **Status tag:** computed

### Status
- **Meaning:** Confidence/provenance tag for the Population value used in that row
- **Source:** Derived
- **Unit:** categorical
- **Transformation:** `official` if Year is 2020 or 2024; `interpolated` if strictly between; `extrapolated` if beyond 2024
- **Analytical role:** Disclosure field — flags which years' density/incidence values are derived rather than directly observed
- **Status tag:** descriptive

---

## Makati–Taguig Geographic Boundary Limitation and Sensitivity Analysis

Makati and Taguig require additional interpretation because an administrative
boundary change occurred during the study period. In the third quarter of 2023,
the Philippine Statistics Authority (PSA) updated the Philippine Standard
Geographic Code (PSGC) to reflect the transfer of 10 barangays previously
classified under the City of Makati to the City of Taguig.

The 10 transferred barangays are:

- Cembo
- Comembo
- East Rembo
- Pembo
- Pitogo
- Post Proper Northside
- Post Proper Southside
- Rizal
- South Cembo
- West Rembo

This creates a geographic discontinuity between the population reference points
used by the project's original population-estimation procedure. The project
applies a consistent linear interpolation method to all 17 NCR LGUs, using the
official population reference values contained in the project's PSA 2020 and
2024 source datasets. For Makati and Taguig, however, part of the apparent
change between these reference values may reflect the change in geographic
coverage rather than population growth or decline alone.

Consequently, the interpolated 2021–2023 population estimates for Makati and
Taguig should not be interpreted as evidence that the population affected by
the territorial transfer gradually moved from Makati to Taguig during those
years. The interpolation is a mathematical estimation between the reference
values used in the analytical dataset and does not model the administrative
transfer itself.

The boundary issue also affects the interpretation of population density.
The analytical dataset retains the fixed land-area values contained in the PSA
reference data originally used by the project and applies the same population-
density calculation consistently across all 17 LGUs. Therefore, density values
for Makati and Taguig should be interpreted with caution because the geographic
coverage represented by the population figures changed during the study period
while the land-area values used by the project remained fixed.

The DOH–MMCHD dengue dataset obtained through the Freedom of Information (FOI)
request reports annual dengue case totals at the LGU level. The dataset
available to the project does not provide barangay-level case counts or
sufficient geographic metadata to retrospectively determine and harmonize the
Makati and Taguig dengue totals according to a single boundary definition for
every year from 2021 to 2025.

For this reason, the project retains the consistently applied population
estimation and land-area methodology rather than retrospectively modifying
Makati and Taguig using a boundary-adjusted denominator that may not correspond
to the geographic coverage of the DOH dengue case numerator.

This limitation is particularly relevant when interpreting:

- Makati and Taguig population estimates for 2021–2023;
- their 2025 extrapolated population estimates;
- computed population density;
- computed dengue incidence rates;
- model estimates involving Population Density;
- the population exposure offset used in the Poisson and Negative Binomial
  regression models; and
- downstream LGU risk rankings and priority classifications involving Makati
  and Taguig.

The Makati and Taguig results should therefore be interpreted as LGU-level
estimates based on the official source data and consistent analytical procedure
available to the study, subject to the geographic-boundary limitation described
above. The limitation does not affect the population interpolation procedure
used for the other 15 NCR LGUs, which did not undergo the same Makati–Taguig
boundary transfer during the study period.

### Boundary sensitivity analysis

To assess whether the Makati–Taguig geographic discontinuity materially affects
the study's results, two sensitivity analyses were conducted.

First, Makati and Taguig were excluded from the Negative Binomial model. The
population-density coefficient remained negative and statistically
non-significant, changing from -0.0065 (p = 0.1296) in the primary model to
-0.0059 (p = 0.1843). The relative structural-risk ordering of all remaining
15 LGUs was unchanged.

Second, a boundary-adjusted population scenario was evaluated using
retrospectively comparable 2020 and 2024 population anchors for Makati and
Taguig while retaining the project's linear interpolation/extrapolation
procedure. Under this scenario, the population-density coefficient remained
negative and statistically non-significant at -0.0069 (p = 0.115). The year
effects and dispersion parameter also remained similar to those of the primary
model.

These sensitivity tests indicate that the Makati–Taguig boundary issue does not
materially alter the overall interpretation of the Negative Binomial model or
the relative structural-risk ordering of the unaffected LGUs.

However, Makati's individual downstream priority classification was sensitive
to the alternative population treatment. In the primary analysis, Makati was
ranked 5th and classified as Priority. Under the boundary-adjusted scenario,
Makati was ranked 3rd but classified as Watch because its scenario 2025
incidence (351.24 per 100,000) was below its scenario five-year average
incidence (374.09 per 100,000). Taguig changed from rank 12 to rank 13 and
remained classified as Stable.

The boundary-adjusted values are therefore treated as a sensitivity scenario,
not as replacements for the primary analytical dataset. This avoids imposing a
retrospective geographic adjustment on the population denominator when
corresponding barangay-level dengue case allocations are unavailable to confirm
that the numerator follows the same geographic definition.

### Reference note

The administrative transfer is documented in the Philippine Statistics
Authority's Third Quarter 2023 Philippine Standard Geographic Code (PSGC)
updates. PSA's 2024 Census of Population (POPCEN) publications subsequently
identify Makati population figures as excluding, and Taguig population figures
as including, the 10 transferred barangays.

These later PSA publications provide important context for interpreting the
project's Makati and Taguig observations but are not used to retrospectively
alter the geographic coverage of the DOH–MMCHD dengue case counts where
corresponding barangay-level case data are unavailable.

---

## Excluded from the panel (used descriptively only)

### Age Group
- **Meaning:** Dengue case counts by age band, aggregated at the NCR level
- **Source:** DOH–MMCHD (via FOI)
- **Unit:** count, by age band
- **Transformation:** None
- **Analytical role:** Descriptive profile of dengue cases NCR-wide; not an LGU-level predictor
- **Status tag:** descriptive

### Sex
- **Meaning:** Dengue case counts by sex, aggregated at the NCR level
- **Source:** DOH–MMCHD (via FOI)
- **Unit:** count, by sex
- **Transformation:** None
- **Analytical role:** Descriptive profile of dengue cases NCR-wide; not an LGU-level predictor
- **Status tag:** descriptive

Age and sex data are excluded from the regression because they are released only
at the NCR level, not disaggregated by LGU — including them as LGU-level
predictors would mismatch the unit of analysis used throughout the rest of the
panel. They are retained for the dashboard's descriptive age-sex panel only.

---

## Status tag definitions

- **official** — value taken directly from an official government source (DOH–MMCHD or PSA) with no transformation.
- **interpolated** — value estimated for a year *between* two known official reference points (2020 and 2024), using linear interpolation. Bounded by real data on both sides.
- **extrapolated** — value estimated for a year *beyond* the last known official reference point (2025), using the same linear annual change projected forward. Carries more uncertainty than interpolation because no second anchor constrains it; flagged as lower-confidence in the dashboard and documentation.
- **computed** — value derived arithmetically from other panel variables (density, incidence rate). Its confidence level is inherited from the Population value used in that row.
- **descriptive** — value used for context/description only, not as a model input.
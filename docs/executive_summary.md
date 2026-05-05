# Executive Summary — TEMPURA EDA

> **Project:** Prokaryote Growth Temperature EDA
> **Dataset:** TogoDB / TEMPURA (n = 8,639 strains, 2020 vintage)
> **Audience:** Research manager scoping an extremophile programme
> **Date:** 2026-05-06
> **Rubric items covered:** Q7 (tasks performed) · Q8 (variability) · Q9 (next steps)

---

## 1. Tasks performed in this project (Q7)

1. **Data acquisition.** Downloaded the TEMPURA database from
   TogoDB under its academic licence (file dated 2020-06-17,
   8,639 rows × 20 columns).
2. **Structural review.** Loaded the CSV into pandas and inspected
   it with `head()`, `info()` and `describe()` to understand the
   schema, the dtypes, the missingness pattern, and the numeric
   ranges.
3. **Quality assessment.** Computed the missing-value rate for
   every column and identified which fields are safe to rely on
   for analysis.
4. **Variability evaluation.** Summarised the distribution of
   `Tmin`, `Topt_ave`, `Tmax` and their cross-correlations,
   both overall and split by `superkingdom`.
5. **Categorical enrichment.** Derived a `temp_cat` label
   (psychrophile / mesophile / thermophile / hyperthermophile)
   and cross-tabulated it against `superkingdom`.
6. **Visualisation.** Produced a histogram, a boxplot and a
   correlation heatmap to communicate the three main findings.
7. **Documentation.** Wrote a PACE strategy document, this
   executive summary, and the repository README so that the
   analysis is reproducible.

---

## 2. Data variability — what we found (Q8)

### 2.1 Headline numbers

| Metric | `Tmin` | `Topt_ave` | `Tmax` |
|---|---|---|---|
| n (non-null) | 8,639 | 8,639 | 8,639 |
| mean (°C) | 15.79 | 33.07 | 41.87 |
| std (°C) | 12.05 | **11.56** | 12.01 |
| min / max (°C) | −20 / 90 | 2 / 106 | 10 / 122 |
| median (°C) | 15 | 30 | 40 |
| IQR (°C) | 10 | 8 | 8 |

**Read:** The three endpoints have similar spreads (σ ≈ 12 °C) but
different centres. The IQR is narrow (≤ 10 °C) everywhere, so the
"typical" organism is mesophilic — but the long upper tail carries
all the biologically interesting variation.

### 2.2 Superkingdom asymmetry

| Superkingdom | n | `Topt_ave` median | `Topt_ave` IQR | `Topt_ave` max |
|---|---|---|---|---|
| **Bacteria** | 8,090 (93.6 %) | 30 °C | 27.5–33.5 (6 °C) | 85 °C |
| **Archaea**  | 549 (6.4 %)    | 40 °C | 37.0–67.5 (30.5 °C) | 106 °C |

**Read:** Archaea are **5 × more variable** than Bacteria and occupy
a much higher median temperature. This is the biggest structural
feature of the dataset and has consequences for modelling (see §3).

### 2.3 Temperature-category breakdown

| Category (Topt °C) | Bacteria | Archaea | Total |
|---|---|---|---|
| Psychrophile (< 20)       |   203 |     3 |   206 |
| Mesophile (20–45)         | 7,249 |   327 | 7,576 |
| Thermophile (45–80)       |   628 |   104 |   732 |
| **Hyperthermophile (≥ 80)** | **10** | **115** | **125** |

**Read:** Of the 125 hyperthermophiles in the catalogue, **115 (92 %)
are Archaea** — a striking concentration that aligns with the
established biology and makes Archaea the right target population
for any extremophile study.

### 2.4 How the temperature endpoints relate

| Pair | Pearson r |
|---|---|
| `Tmin` ↔ `Topt_ave` | 0.844 |
| `Topt_ave` ↔ `Tmax` | 0.930 |
| `Tmin` ↔ `Tmax`    | 0.790 |
| `Topt_ave` ↔ `Genome_GC` | −0.114 |
| `Topt_ave` ↔ `16S_GC`    | +0.519 |

**Read:** The three temperature endpoints are near-collinear, so
they should not all be fed into a regression as independent features
without regularisation. GC content adds only modest extra signal,
with `16S_GC` (r ≈ 0.52) more informative than whole-genome GC.

### 2.5 Data-quality caveats

- `Topt_low`, `Topt_high` are missing for ~64 % of strains —
  avoid using them directly.
- `Genome_size`, `assembly_or_accession` are missing for ~88 % —
  treat as optional enrichment.
- The four core temperature endpoints (`Tmin`, `Topt_ave`, `Tmax`,
  `Tmax_Tmin`) are **100 % populated** — the analysis rests on them.

---

## 3. Recommended next steps — toward a predictive model (Q9)

The variability findings above support a clear path forward:

### 3.1 Regression — predict `Topt_ave`

- **Target.** `Topt_ave` (continuous, °C).
- **Features.** `Tmin`, `Tmax`, `16S_GC`, `Genome_GC`,
  superkingdom/phylum dummies.
- **Model family.** Ridge or PLS regression — the temperature
  endpoints are highly collinear (r ≥ 0.79) and plain OLS will
  over-fit.
- **Validation.** 5-fold CV, **stratified by `superkingdom`**
  so Archaea are represented in every fold.

### 3.2 Classification — predict `temp_cat`

- **Target.** Four-class label (psychrophile / mesophile /
  thermophile / hyperthermophile).
- **Why a second model.** The classes are actionable for the
  research manager (sampling strategy, growth-medium selection).
- **Imbalance.** Classes are 2.4 % / 87.7 % / 8.5 % / 1.4 %.
  Use class weights or focal loss; report **macro-F1**, not accuracy.

### 3.3 Data enrichment

- Join on `taxonomy_id` against NCBI Taxonomy to pull habitat /
  isolation-source metadata; this may add predictive power beyond
  pure taxonomy.
- Consider adding oceanographic / geographic context for
  marine isolates.

### 3.4 Fairness and model governance

- The 93:6 Bacteria:Archaea ratio is a representation risk.
  All evaluation metrics should be reported **per superkingdom**
  so Bacteria-dominated accuracy cannot hide poor Archaea
  performance.
- Any production model should carry a "2020 vintage" note — the
  taxonomy has since evolved (e.g. NCBI renames) and predictions
  for strains added after 2020 should be treated with caution.

---

## 4. Summary one-liner for the research manager

> TEMPURA contains 8,639 strains with complete temperature endpoints.
> Bacteria dominate the catalogue but Archaea — though only 6 % of the
> rows — account for 92 % of the hyperthermophiles. A `Topt_ave`
> regression with ridge regularisation, stratified by superkingdom,
> is the right next step.

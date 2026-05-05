# PACE Strategy Document — TEMPURA EDA

> **Project:** Prokaryote Growth Temperature EDA
> **Dataset:** TogoDB / TEMPURA (n = 8,639 strains)
> **Author:** Data Professional (Course 1 final project)
> **Date:** 2026-05-06
> **Rubric item covered:** Q6 — PACE strategy document (all questions answered)

---

## 0. Executive framing

A research manager at a biotech company is scoping a study of
extremophilic prokaryotes. Before running any expensive wet-lab work,
they want a data-driven picture of the growth-temperature landscape
across the publicly catalogued strains, plus a clear recommendation
on where a predictive model could add value later on.

The PACE framework (Plan → Analyze → Construct → Execute) structures
how the data professional tackles this request end-to-end.

---

## 1. Plan

### 1.1 Stakeholders

| Role | Interest | Deliverable they care about |
|---|---|---|
| Research manager (primary) | Scope of the extremophile programme | Executive summary, temperature categories |
| Bioinformatics lead | Data quality, model feasibility | Notebook, data-quality report |
| Ethics / IP officer | Licence compliance, citation | Data README, licence statement |
| Course grader (secondary) | Rubric completeness | Notebook + 2 markdown docs |

### 1.2 Business task

> **"Characterise the growth-temperature landscape of catalogued
> prokaryotes and tell me whether a predictive model is worth building."**

### 1.3 Guiding questions

| ID | Question | Why it matters |
|---|---|---|
| Q-A | How is `Topt_ave` distributed overall? | Tells us where "typical" strains sit |
| Q-B | Do Bacteria and Archaea differ? | Drives sampling strategy for the programme |
| Q-C | How correlated are `Tmin`, `Topt_ave`, `Tmax`? | Tells us which features carry unique signal |
| Q-D | Where are the data-quality issues? | Tells us what to trust in modelling |

### 1.4 Data

- **Source:** TogoDB / TEMPURA (Sato et al., 2020, *Microbes Environ*)
- **Size:** 8,639 rows × 20 columns
- **Key numeric:** `Tmin`, `Topt_ave`, `Topt_low`, `Topt_high`,
  `Tmax`, `Tmax_Tmin`, `Genome_GC`, `Genome_size`, `16S_GC`
- **Key categorical:** `superkingdom`, `phylum`, `class`, `order`,
  `family`, `genus`, `genus_and_species`

### 1.5 Scope limits (what we are *not* doing in this iteration)

- No model training — only EDA and a recommendation.
- No joins against external databases (e.g. NCBI Taxonomy) —
  saved for a later course iteration.
- No custom imputation of `Topt_low` / `Topt_high` missingness —
  we rely on the point estimate `Topt_ave` instead.

---

## 2. Analyze

### 2.1 Structural inspection

Three canonical pandas calls, each chosen for a specific purpose:

| Call | Purpose | Finding |
|---|---|---|
| `df.head()` | Plausibility check on raw values | Taxonomy + temperature columns present; extreme values (122 °C) appear immediately — authentic, not errors |
| `df.info()` | Dtypes + non-null counts | Temperature endpoints are 100 % populated; `Topt_low/high` and `Genome_size` are ~64 % / ~88 % missing |
| `df.describe()` | Summary statistics | `Topt_ave` median 30 °C, range 2–106 °C; `Tmin` range −20 to +90 °C; `Tmax` up to 122 °C |

### 2.2 Quality risks flagged

- **Severe missingness** in genomic metadata (`assembly_or_accession`,
  `Genome_size`) — usable only as an optional feature.
- **Class imbalance:** Archaea (n = 549) vs Bacteria (n = 8,090).
  Any model must handle this explicitly.
- **Heavy-tailed numeric distributions** → transformations or robust
  estimators recommended for regression.

### 2.3 Exploratory questions answered at this stage

- **Q-D resolved.** Data quality is good for the four core temperature
  columns; it degrades for the genomic and range columns.

---

## 3. Construct

### 3.1 Visualisations (each tied back to a guiding question)

| Chart | Question answered | Key takeaway |
|---|---|---|
| `Topt_ave` histogram | Q-A | Right-skewed; 88 % mesophile, long hyperthermophile tail |
| Boxplot of `Topt_ave` by `superkingdom` | Q-B | Archaea 5× wider IQR; dominate ≥ 80 °C tail |
| Temperature category cross-tab | Q-B | 115 of 125 hyperthermophiles are Archaea |
| Correlation heatmap | Q-C | `Topt_ave`↔`Tmax` r=0.93, `Topt_ave`↔`Tmin` r=0.84, GC weakly negative |

### 3.2 Derived features created

- `temp_cat` (categorical): Psychrophile / Mesophile / Thermophile /
  Hyperthermophile — a reusable bucket for downstream reporting.

### 3.3 Reproducibility

- The notebook runs end-to-end from the raw CSV.
- Random seeds are not needed (no sampling / no modelling yet).
- Library versions are pinned via `requirements.txt`.

---

## 4. Execute

### 4.1 Findings to share with the research manager

1. The population is dominated by mesophilic Bacteria
   (Topt 27.5–33.5 °C, IQR 6 °C).
2. Archaea are the right population to target for extremophile work
   — their IQR (37.0–67.5 °C) is 5 × wider than Bacteria's.
3. The temperature endpoints carry mostly overlapping information
   (r ≥ 0.79) — modelling a single target (`Topt_ave`) is sufficient.
4. Data quality is **good enough** to move on to a predictive model.

### 4.2 Recommended next steps

- **Ridge / PLS regression** predicting `Topt_ave` from `Tmin`,
  `Tmax`, `Genome_GC`, `16S_GC` and taxonomic dummies.
- **Four-class classifier** over the `temp_cat` buckets, evaluated
  with class-weighted metrics (macro-F1) because of the 93:6 imbalance.
- **Stratified evaluation** — always split by `superkingdom` to avoid
  Bacteria-only accuracy masking poor Archaea performance.

### 4.3 How findings are communicated

- **Notebook** (`notebooks/tempura_eda.ipynb`) — technical audience.
- **Executive summary** (`docs/executive_summary.md`) — research manager.
- **This strategy document** — the bioinformatics lead and the ethics officer.

---

## 5. Ethics and fairness

- **Licence compliance.** Data pulled from TogoDB under its academic
  licence. The raw CSV is **not** redistributed in this repository;
  `data/README.md` documents how to obtain it.
- **Representation bias.** Archaea are ~ 6 % of the rows; a naïve
  random split would leave some evaluation folds with almost no Archaea.
  Mitigation: **stratified splits** and **subgroup metrics**.
- **Data vintage.** The file is dated **2020-06-17**; taxonomy has
  evolved since (e.g. NCBI Taxonomy renames). All findings should be
  labelled "as of 2020".
- **Citation.** Any downstream publication must cite Sato Y, Okano K,
  Kimura H, Honda K (2020) *Microbes and Environments* 35:ME20074.

---

## 6. Risks and mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Licence violation by redistributing CSV | Low | High | Keep `data/raw/` in `.gitignore`; document acquisition in `data/README.md` |
| Model trained only on Bacteria → poor on Archaea | High | Medium | Stratified evaluation; subgroup metrics; up-weighting Archaea |
| Over-fitting on 549 Archaea rows | Medium | Medium | Cross-validation; regularised regression |
| Stale taxonomy (2020 vintage) | Medium | Low | Flag the vintage in every deliverable |

---

## 7. Hand-off checklist (end of Course 1)

- [x] Notebook reproducibly runs from raw CSV
- [x] PACE strategy document (this file)
- [x] Executive summary with variability evaluation + next steps
- [x] README, data README, requirements.txt
- [x] No PII or license-restricted data committed

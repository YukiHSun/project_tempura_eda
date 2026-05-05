"""
Build the Jupyter Notebook programmatically using nbformat.
Run: python build_notebook.py
Produces: tempura_eda.ipynb
"""
import nbformat as nbf

nb = nbf.v4.new_notebook()
cells = []

# Title
cells.append(nbf.v4.new_markdown_cell("""# Prokaryote Growth Temperature EDA — TEMPURA

**Course 1 Final Project — Google Advanced Data Analytics Certificate**
**Dataset:** TogoDB / TEMPURA (Sato et al., 2020)
**Goal:** Explore the growth temperature profiles of 8,639 prokaryote strains with pandas, then recommend next steps toward predictive modelling.

This notebook is structured along the **PACE framework**:

- **Plan** — define the business task and the questions we want to answer
- **Analyze** — load the data, inspect its structure and quality
- **Construct** — summarise and visualise the data
- **Execute** — summarise findings and recommend next steps
"""))

# Q1 — Import libraries
cells.append(nbf.v4.new_markdown_cell("""## 1. Plan — Import packages and set-up (rubric Q1)

We import the core Python data-analysis stack:
`pandas` for tabular data, `numpy` for numerical operations,
`matplotlib` and `seaborn` for visualisation."""))

cells.append(nbf.v4.new_code_cell("""import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 160)
sns.set_theme(style='whitegrid')

print(f"pandas  : {pd.__version__}")
print(f"numpy   : {np.__version__}")
print(f"seaborn : {sns.__version__}")"""))

# Business task
cells.append(nbf.v4.new_markdown_cell("""### Business task

A research manager wants to scope a study of extremophilic prokaryotes.
Before designing the experiment, they need a clear picture of how
minimum / optimum / maximum growth temperatures are distributed
across the publicly catalogued strains, and whether Archaea and Bacteria
differ systematically.

**Guiding questions**

- **Q-A.** What is the overall distribution of the optimum growth temperature (`Topt_ave`)?
- **Q-B.** Do Bacteria and Archaea show different temperature profiles?
- **Q-C.** How correlated are the three temperature endpoints (`Tmin`, `Topt_ave`, `Tmax`)?
- **Q-D.** Where are the data quality issues (missingness, extreme values)?"""))

# Load data
cells.append(nbf.v4.new_markdown_cell("""## 2. Analyze — Load the TEMPURA dataset

The CSV was downloaded from [TogoDB / TEMPURA](https://togodb.org/db/tempura)
after accepting the database licence. We store it at
`data/raw/tempura.csv` (kept out of version control; see `data/README.md`)."""))

cells.append(nbf.v4.new_code_cell("""df = pd.read_csv('../data/raw/tempura.csv')
print(f"Shape: {df.shape[0]:,} rows × {df.shape[1]} columns")"""))

# Q2 — head()
cells.append(nbf.v4.new_markdown_cell("""### 2.1 `head()` — First look at the data (rubric Q2)

Are the columns what we expect? Do the values look plausible?"""))

cells.append(nbf.v4.new_code_cell("""df.head()"""))

cells.append(nbf.v4.new_markdown_cell("""**Observation.** The table carries a taxonomic block
(`genus_and_species`, `superkingdom`, `phylum`, …, `genus`) alongside the
numeric temperature columns (`Tmin`, `Topt_ave`, `Topt_low`, `Topt_high`,
`Tmax`, `Tmax_Tmin`) and some optional genomic metadata
(`Genome_GC`, `Genome_size`, `16S_GC`). The top rows are dominated by
extremely high `Tmax` values (~110–122 °C) from Archaea such as
*Methanopyrus kandleri* — a useful reminder that this dataset includes
genuine extremophiles."""))

# Q3 — info()
cells.append(nbf.v4.new_markdown_cell("""### 2.2 `info()` — Types and missingness (rubric Q3)

`info()` tells us the dtypes and non-null counts for every column —
this is the fastest way to spot columns with heavy missingness that
we should not trust without care."""))

cells.append(nbf.v4.new_code_cell("""df.info()"""))

cells.append(nbf.v4.new_code_cell("""missing_rate = (df.isna().sum() / len(df) * 100).round(2).sort_values(ascending=False)
missing_rate.to_frame('missing_%')"""))

cells.append(nbf.v4.new_markdown_cell("""**Observation.**

- Temperature **endpoints** (`Tmin`, `Topt_ave`, `Tmax`, `Tmax_Tmin`)
  are complete (0 % missing) — these are safe to use directly.
- The optimum **range** (`Topt_low`, `Topt_high`) is missing for ~64 %
  of strains, so we will rely on the point estimate `Topt_ave` instead.
- Whole-genome metadata (`assembly_or_accession`, `Genome_size`)
  is only available for ~12 % of rows. Any genomics-aware modelling
  will need to account for this.
- The taxonomic columns are almost complete (≤ 2 % missing)."""))

# Q4 — describe()
cells.append(nbf.v4.new_markdown_cell("""### 2.3 `describe()` — Summary statistics (rubric Q4)

`describe(include='all')` gives the numeric summary plus the cardinality
of the object columns in a single call."""))

cells.append(nbf.v4.new_code_cell("""df.describe(include='all')"""))

cells.append(nbf.v4.new_markdown_cell("""**Observation.**

- `Topt_ave` has median **30 °C** and mean **33 °C**; the IQR is tight
  (28–36 °C) but the range is enormous (2 °C → 106 °C).
- `Tmin` reaches **−20 °C** (psychrophiles) and `Tmax` **+122 °C**
  (*Methanopyrus kandleri*, a confirmed hyperthermophile).
- `Genome_GC` varies from 23.9 % to 77.8 % — wide, as expected across
  the prokaryotic tree of life."""))

# Domain split
cells.append(nbf.v4.new_markdown_cell("""## 3. Construct — Explore structure by superkingdom

### 3.1 How are the two domains represented?"""))

cells.append(nbf.v4.new_code_cell("""df['superkingdom'].value_counts(dropna=False)"""))

cells.append(nbf.v4.new_code_cell("""df.groupby('superkingdom')['Topt_ave'].describe().round(2)"""))

cells.append(nbf.v4.new_markdown_cell("""**Observation.** The dataset is strongly imbalanced:
**Bacteria = 8,090 (93.6 %)** vs **Archaea = 549 (6.4 %)**.
Archaea have a much wider `Topt_ave` distribution
(IQR 37.0–67.5 °C, max 106 °C) than Bacteria
(IQR 27.5–33.5 °C, max 85 °C). This asymmetry will drive most of
the interesting findings in the rest of the notebook."""))

# Q5 — annotated visualisations
cells.append(nbf.v4.new_markdown_cell("""### 3.2 Visualisations (rubric Q5 — each chart is explained in prose)

#### 3.2.1 Overall distribution of optimum temperature"""))

cells.append(nbf.v4.new_code_cell("""fig, ax = plt.subplots(figsize=(8, 4))
sns.histplot(df['Topt_ave'], bins=40, ax=ax, color='steelblue')
ax.axvline(df['Topt_ave'].mean(), color='red', linestyle='--', label=f"mean = {df['Topt_ave'].mean():.1f} °C")
ax.axvline(df['Topt_ave'].median(), color='orange', linestyle='--', label=f"median = {df['Topt_ave'].median():.1f} °C")
ax.set_xlabel('Optimum growth temperature Topt_ave (°C)')
ax.set_ylabel('Strain count')
ax.set_title('Topt_ave is concentrated around mesophilic values, with a long hyperthermophilic tail')
ax.legend()
plt.tight_layout()
plt.show()"""))

cells.append(nbf.v4.new_markdown_cell("""**Answer to Q-A.** The distribution is **strongly right-skewed**.
Roughly 88 % of strains are mesophiles (`Topt_ave` in 20–45 °C) but
a long tail extends to the hyperthermophiles (≥ 80 °C)."""))

cells.append(nbf.v4.new_markdown_cell("""#### 3.2.2 Bacteria vs Archaea"""))

cells.append(nbf.v4.new_code_cell("""fig, ax = plt.subplots(figsize=(8, 4))
sns.boxplot(data=df, x='superkingdom', y='Topt_ave', ax=ax,
            order=['Bacteria', 'Archaea'],
            palette={'Bacteria': '#4c72b0', 'Archaea': '#dd8452'})
ax.set_xlabel('Superkingdom')
ax.set_ylabel('Optimum growth temperature Topt_ave (°C)')
ax.set_title('Archaea have a far wider and higher temperature range than Bacteria')
plt.tight_layout()
plt.show()"""))

cells.append(nbf.v4.new_markdown_cell("""**Answer to Q-B.** Bacteria cluster tightly around mesophilic
temperatures (median 30 °C, IQR 6 °C). Archaea are **much more
dispersed** (median 40 °C, IQR 30.5 °C) and dominate the high end
— see the temperature category cross-tab below."""))

cells.append(nbf.v4.new_code_cell("""def temp_category(t):
    if t < 20:  return 'Psychrophile (<20)'
    if t < 45:  return 'Mesophile (20–45)'
    if t < 80:  return 'Thermophile (45–80)'
    return 'Hyperthermophile (≥80)'

df['temp_cat'] = df['Topt_ave'].apply(temp_category)
cat_order = ['Psychrophile (<20)', 'Mesophile (20–45)', 'Thermophile (45–80)', 'Hyperthermophile (≥80)']
ct = (df.groupby(['superkingdom', 'temp_cat']).size()
        .unstack(fill_value=0)[cat_order])
ct"""))

cells.append(nbf.v4.new_markdown_cell("""**Observation.** Of the 125 hyperthermophiles, **115 (92 %) are Archaea**.
This is the single strongest biological signal in the dataset."""))

cells.append(nbf.v4.new_markdown_cell("""#### 3.2.3 Relationships between Tmin, Topt_ave, Tmax"""))

cells.append(nbf.v4.new_code_cell("""corr = df[['Tmin', 'Topt_ave', 'Tmax', 'Tmax_Tmin', 'Genome_GC', '16S_GC']].corr()
fig, ax = plt.subplots(figsize=(6, 5))
sns.heatmap(corr, annot=True, fmt='.2f', cmap='RdBu_r', center=0, ax=ax, vmin=-1, vmax=1)
ax.set_title('Temperature endpoints are tightly linked; GC content is a weaker correlate')
plt.tight_layout()
plt.show()"""))

cells.append(nbf.v4.new_markdown_cell("""**Answer to Q-C.** `Topt_ave` is almost collinear with the endpoints
(`r` = 0.844 with `Tmin`, `r` = 0.930 with `Tmax`) — unsurprising
biologically, but important for modelling: we should **not** include
all three as predictors of each other without regularisation.
`Genome_GC` is only weakly correlated with temperature (`r` ≈ −0.11)."""))

cells.append(nbf.v4.new_markdown_cell("""#### 3.2.4 Outliers / extreme values"""))

cells.append(nbf.v4.new_code_cell("""extreme = df[(df['Topt_ave'] >= 80) | (df['Tmin'] <= 0)][
    ['genus_and_species', 'superkingdom', 'Tmin', 'Topt_ave', 'Tmax']
].sort_values('Topt_ave', ascending=False)
print(f"Extreme-temperature strains: {len(extreme)} (of {len(df)})")
extreme.head(10)"""))

cells.append(nbf.v4.new_markdown_cell("""**Answer to Q-D.** There are 228 "extreme" rows (125 hyperthermophiles
with `Topt_ave` ≥ 80 °C plus 103 strains with `Tmin` ≤ 0 °C). These are
**not data errors** — they correspond to real, well-documented
extremophile species — so they should be retained but flagged in any
downstream model."""))

# Execute section
cells.append(nbf.v4.new_markdown_cell("""## 4. Execute — Key take-aways

1. The TEMPURA dataset covers **8,639 prokaryote strains**; 93.6 %
   Bacteria, 6.4 % Archaea.
2. `Topt_ave` is right-skewed: 88 % are mesophiles,
   but a long tail reaches 106 °C.
3. Archaea drive almost all of the high-temperature signal
   — **92 % of hyperthermophiles are Archaea**.
4. `Tmin`, `Topt_ave` and `Tmax` are highly correlated
   (0.79–0.93); GC content adds only weak information.
5. Data-quality caveats: `Topt_low/high` and `Genome_size`
   are missing for the majority of rows; the taxonomic columns
   and the three main temperature endpoints are complete.

The narrative write-up lives in `docs/executive_summary.md`,
and the full PACE strategy is in `docs/pace_strategy.md`."""))

cells.append(nbf.v4.new_markdown_cell("""## 5. Recommended next steps

- **Regression.** Predict `Topt_ave` from `Tmin`, `Tmax`, `Genome_GC`,
  `16S_GC` and taxonomic dummies. Expect strong multicollinearity
  between the temperature endpoints → use Ridge / PLS.
- **Classification.** Predict the four temperature categories
  (psychrophile / mesophile / thermophile / hyperthermophile)
  from genomic + taxonomic features.
- **Data enrichment.** Join against NCBI Taxonomy to pull habitat /
  isolation-source metadata; look for geographic or niche effects
  beyond the taxonomy.
- **Fairness.** The Archaea sample (n = 549) is small. Any model
  evaluation must be **stratified** by superkingdom to avoid
  Bacteria-only accuracy masking poor Archaea performance."""))

nb['cells'] = cells

with open('tempura_eda.ipynb', 'w') as f:
    nbf.write(nb, f)

print("tempura_eda.ipynb written.")

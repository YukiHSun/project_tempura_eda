# Prokaryote Growth Temperature EDA (TEMPURA)

Course 1 final project for the **Google Advanced Data Analytics Certificate**.
The project performs an exploratory data analysis of the TEMPURA database
and recommends the next steps toward a predictive temperature model.

## Contents

```
project_tempura_eda/
├── README.md                     ← this file
├── requirements.txt              ← pinned dependencies
├── notebooks/
│   ├── tempura_eda.ipynb        ← main notebook (rubric Q1–Q5)
│   └── build_notebook.py        ← regenerates the notebook from scratch
├── docs/
│   ├── pace_strategy.md         ← PACE strategy document (rubric Q6)
│   └── executive_summary.md     ← executive summary (rubric Q7–Q9)
└── data/
    ├── README.md                ← data source, licence and acquisition steps
    └── raw/                     ← place tempura.csv here (not committed)
```

## Rubric coverage (target 9 / 9)

| # | Rubric item | Deliverable |
|---|---|---|
| Q1 | Imported packages | `tempura_eda.ipynb` §1 |
| Q2 | Used `head()` | `tempura_eda.ipynb` §2.1 |
| Q3 | Used `info()` | `tempura_eda.ipynb` §2.2 |
| Q4 | Used `describe()` | `tempura_eda.ipynb` §2.3 |
| Q5 | Every prompt answered in the notebook | prose in every section |
| Q6 | PACE strategy document | `docs/pace_strategy.md` |
| Q7 | Tasks performed | `docs/executive_summary.md` §1 |
| Q8 | Data variability evaluated | `docs/executive_summary.md` §2 |
| Q9 | Next steps for predictive model | `docs/executive_summary.md` §3 |

## Quick start

```bash
# activate your Python 3.12 env, then:
pip install -r requirements.txt
jupyter notebook notebooks/tempura_eda.ipynb
```

The notebook is already executed — you can also just read it in GitHub.

## Dataset

TEMPURA — *Database of Growth TEMPeratures of Usual and RAre Prokaryotes*.

- Source: https://togodb.org/db/tempura
- Citation: Sato Y, Okano K, Kimura H, Honda K. (2020).
  *Microbes and Environments* 35(3):ME20074.
  [J-STAGE link](https://www.jstage.jst.go.jp/article/jsme2/35/3/35_ME20074/_article)
- File used: `200617_TEMPURA.csv` (2020-06-17 vintage, 8,639 rows × 20 columns)

The raw CSV is **not redistributed**. See `data/README.md` for how to obtain it.

## Licence

Code: MIT. Data: subject to the TEMPURA / TogoDB licence — please cite Sato et al. (2020).

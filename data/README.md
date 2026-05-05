# Data — acquisition and licence

This directory holds the raw TEMPURA database and its documentation.

## Do **not** commit the raw CSV

The file `raw/tempura.csv` is redistributable only under the TogoDB
licence. We therefore keep it **out of version control** (add it to
`.gitignore`). This README documents how to re-create it.

## How to obtain `tempura.csv`

1. Visit https://togodb.org/db/tempura
2. Click "Download CSV" and accept the licence dialog.
3. Save the downloaded file as `data/raw/tempura.csv` inside the project.

Alternatively, if the project shipped with a copy named
`200617_TEMPURA.csv`, rename or symlink it to `tempura.csv`:

```bash
cp /path/to/200617_TEMPURA.csv data/raw/tempura.csv
```

## Dataset at a glance

- **Filename used in this project:** `tempura.csv`
- **Snapshot used for analysis:** 2020-06-17
- **Shape:** 8,639 rows × 20 columns
- **Superkingdom split:** Bacteria 8,090 · Archaea 549
- **Completeness of the core temperature endpoints (`Tmin`, `Topt_ave`, `Tmax`, `Tmax_Tmin`):** 100 %

## Citation

Sato Y, Okano K, Kimura H, Honda K. (2020). *TEMPURA: Database of Growth
TEMPeratures of Usual and RAre Prokaryotes.* **Microbes and Environments**
35(3): ME20074.
[J-STAGE link](https://www.jstage.jst.go.jp/article/jsme2/35/3/35_ME20074/_article)

## Notes on the vintage

The database is a 2020-06-17 snapshot. Taxonomy has evolved since
(e.g. NCBI has renamed or re-classified several strains). All findings
in this project are labelled "as of 2020" and should be refreshed
against the latest NCBI Taxonomy before they are relied upon for
operational decisions.

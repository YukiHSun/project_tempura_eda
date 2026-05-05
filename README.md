# Prokaryote Growth Temperature EDA + Regression (TEMPURA)

Google Advanced Data Analytics Certificate の **Course終了プロジェクト**
をベースに、`Topt_ave`（最適生育温度）を予測する**回帰モデル**まで
実装したプロジェクト。

- **Phase 1 — EDA**: TEMPURA 8,639 株を pandas で構造把握・可視化し、
  データの可変性と次ステップを提示。**ルーブリック 9/9** 達成。
- **Phase 1.5 — Regression**: EDA で立てた次ステップに従い、
  `Topt_ave` の Ridge / HistGradientBoosting 回帰を
  **superkingdom 層化 CV** で実装。
  **全体 MAE 2.50 ℃ / R² 0.918**（計画書目標をすべてクリア）。

---

## ディレクトリ構成

```
project_tempura_eda/
├── README.md                            ← このファイル
├── requirements.txt                     ← 依存パッケージ
├── .gitignore                           ← data/raw/ と *.csv を除外
├── notebooks/
│   ├── tempura_eda.ipynb               ← EDA 本体（rubric Q1–Q5、実行済み）
│   ├── build_notebook.py               ← EDA Notebook 再生成スクリプト
│   ├── topt_regression.ipynb           ← 回帰モデル本体（実行済み）
│   └── build_modeling_notebook.py      ← 回帰 Notebook 再生成スクリプト
├── docs/
│   ├── pace_strategy.md / _ja.md       ← PACE 戦略文書 (rubric Q6) 英/日
│   ├── executive_summary.md / _ja.md   ← エグゼクティブサマリー (Q7–Q9) 英/日
│   ├── modeling_plan_ja.md             ← 回帰モデル計画書（日本語）
│   └── modeling_results_ja.md          ← 回帰モデル結果サマリー（日本語）
├── data/
│   ├── README.md                       ← データ取得手順・ライセンス
│   └── raw/                            ← tempura.csv をローカル配置（未コミット想定）
└── models/
    └── topt_regressor_histgradientboosting.joblib  ← 最終モデル（全データ再学習）
```

---

## Course 1 ルーブリック対応（9 / 9 達成）

| # | ルーブリック項目 | 成果物 |
|---|---|---|
| Q1 | パッケージ import | `notebooks/tempura_eda.ipynb` §1 |
| Q2 | `head()` 使用 | `notebooks/tempura_eda.ipynb` §2.1 |
| Q3 | `info()` 使用 | `notebooks/tempura_eda.ipynb` §2.2 |
| Q4 | `describe()` 使用 | `notebooks/tempura_eda.ipynb` §2.3 |
| Q5 | Notebook 内の設問にすべて回答 | 全セクションで設問 → 観察 → 解釈を記述 |
| Q6 | PACE 戦略文書 | `docs/pace_strategy.md` / `_ja.md` |
| Q7 | 実施タスクの明示 | `docs/executive_summary.md` §1 |
| Q8 | データ可変性評価 | `docs/executive_summary.md` §2 |
| Q9 | 予測モデルへの次ステップ | `docs/executive_summary.md` §3 |

---

## 拡張（Phase 1.5）: `Topt_ave` 回帰モデル

Q9 の推奨に沿って、実際に予測モデルを構築・評価した。
詳細は `docs/modeling_plan_ja.md`（計画）と
`docs/modeling_results_ja.md`（結果）を参照。

### 主要結果（5-fold superkingdom 層化 CV）

| model | 全体 MAE | 全体 R² | Archaea MAE | Archaea R² |
|---|---|---|---|---|
| Dummy (mean) | 7.34 | ~0 | 18.88 | −0.72 |
| **Ridge** | **2.82** | **0.902** | **3.30** | **0.962** |
| **HistGradientBoosting** | **2.50** | **0.918** | **2.85** | **0.968** |

### 計画書目標との突合

| 指標 | 目標 | 実績（HistGB） | 判定 |
|---|---|---|---|
| 全体 MAE ≤ 4.0 ℃ | 4.0 | **2.50** | ✅ |
| 全体 R² ≥ 0.85 | 0.85 | **0.918** | ✅ |
| Bacteria MAE ≤ 3.5 ℃ | 3.5 | **2.48** | ✅ |
| Archaea MAE ≤ 6.0 ℃ | 6.0 | **2.85** | ✅ |
| Archaea R² ≥ 0.70 | 0.70 | **0.968** | ✅ |

**6 項目すべてクリア**。特に Archaea（n=549）でも精度を落とさず、
層化 CV とサブグループメトリクスによる公平性設計が機能している。

### 採用モデル方針

- **初期導入は Ridge**（係数で説明責任を果たしやすい）。
- **精度重視の本番化時に HistGradientBoosting** に切り替え。
- 保存モデル: `models/topt_regressor_histgradientboosting.joblib`

---

## クイックスタート

```bash
# Python 3.12 環境をアクティベートしてから
pip install -r requirements.txt

# EDA ノートブック
jupyter notebook notebooks/tempura_eda.ipynb

# 回帰モデルノートブック
jupyter notebook notebooks/topt_regression.ipynb
```

両 Notebook は**実行済み**のため、GitHub 上でもそのまま閲覧可能。

### Notebook を再生成したい場合

```bash
cd notebooks
python build_notebook.py           # tempura_eda.ipynb を再構築
python build_modeling_notebook.py  # topt_regression.ipynb を再構築
jupyter nbconvert --to notebook --execute tempura_eda.ipynb     --output tempura_eda.ipynb
jupyter nbconvert --to notebook --execute topt_regression.ipynb --output topt_regression.ipynb
```

---

## データセット

TEMPURA — *Database of Growth TEMPeratures of Usual and RAre Prokaryotes*

- 出所: https://togodb.org/db/tempura
- 引用: Sato Y, Okano K, Kimura H, Honda K. (2020).
  *Microbes and Environments* 35(3):ME20074.
  [J-STAGE link](https://www.jstage.jst.go.jp/article/jsme2/35/3/35_ME20074/_article)
- 使用ファイル: `200617_TEMPURA.csv`（2020-06-17 版、8,639 行 × 20 列）

生 CSV は**再配布しない**。取得手順は `data/README.md` を参照。

---

## 依存パッケージ

`requirements.txt` にピン止め済み:

- pandas ≥ 2.1
- numpy ≥ 1.26
- matplotlib ≥ 3.7
- seaborn ≥ 0.13
- jupyter ≥ 1.0
- nbformat ≥ 5.9
- scikit-learn ≥ 1.4（回帰フェーズ用）
- joblib ≥ 1.3（モデル保存用）

---

## ライセンス

- **コード**: MIT
- **データ**: TEMPURA / TogoDB のライセンスに従う。引用必須:
  Sato Y, Okano K, Kimura H, Honda K. (2020) *Microbes and Environments* 35:ME20074.
- **モデル (`models/`)**: プロジェクト成果物として残すが、商用利用は
  TEMPURA のライセンスを尊重すること。

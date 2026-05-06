# 分類モデル 結果サマリー（日本語版）— `temp_cat` 予測

> **計画書:** [`classification_plan_ja.md`](./classification_plan_ja.md)
> **実行 Notebook:** [`../notebooks/topt_classification.ipynb`](../notebooks/topt_classification.ipynb)
> **実行日:** 2026-05-06
> **採用モデル:** **RandomForest (tuned)** — macro F1 = 0.858

---

## 0. 1 行結論

**Random Forest と XGBoost はほぼ互角**（weighted F1 ≈ 0.96）。
最終モデルには **macro F1 = 0.858** の Random Forest を採用した。
計画書の 4 つの目標すべてを達成。

---

## 1. モデル比較サマリ（5-fold CV）

| モデル | Accuracy | Precision<sub>w</sub> | Recall<sub>w</sub> | **F1<sub>w</sub>** | Precision<sub>m</sub> | Recall<sub>m</sub> | **F1<sub>m</sub>** |
|---|---|---|---|---|---|---|---|
| Dummy (most_frequent) | 0.877 | 0.769 | 0.877 | 0.819 | 0.219 | 0.250 | 0.234 |
| **RandomForest (tuned)** | **0.961** | **0.965** | **0.961** | **0.963** | 0.827 | **0.896** | **0.858** |
| **XGBoost (tuned)** | 0.960 | 0.962 | 0.960 | 0.961 | **0.830** | 0.871 | 0.849 |

> **観察:**
> - Dummy はクラス不均衡のため **weighted F1 = 0.82** と高く見えるが、**macro F1 = 0.23**。クラス不均衡で Accuracy が誤解を招く典型。
> - RF と XGB は全指標で Dummy を大きく上回る。
> - **macro F1 では RF 勝ち**、**macro Precision では XGB 勝ち**とわずかに特性が分かれる。

---

## 2. 最適ハイパーパラメータ

### Random Forest（GridSearchCV, f1_macro refit）

| パラメータ | 探索範囲 | 採用値 |
|---|---|---|
| `n_estimators` | [200, 400] | **400** |
| `max_depth` | [6, 12, None] | **None**（制限なし） |
| `min_samples_leaf` | [1, 3] | **3** |

**Best CV macro-F1: 0.8584**

### XGBoost（GridSearchCV, f1_macro refit）

| パラメータ | 探索範囲 | 採用値 |
|---|---|---|
| `n_estimators` | [200, 400] | **400** |
| `max_depth` | [4, 6, 8] | **6** |
| `learning_rate` | [0.05, 0.1] | **0.1** |

**Best CV macro-F1: 0.8491**

---

## 3. クラス別性能

### Random Forest（採用モデル）

| クラス | Precision | Recall | F1 | support |
|---|---|---|---|---|
| **Hyperthermophile** | 0.903 | **0.968** | **0.934** | 125 |
| Mesophile | 0.986 | 0.972 | 0.979 | 7,576 |
| Psychrophile | 0.542 | 0.728 | 0.621 | 206 |
| Thermophile | 0.879 | 0.915 | 0.897 | 732 |

### XGBoost

| クラス | Precision | Recall | F1 | support |
|---|---|---|---|---|
| Hyperthermophile | **0.917** | **0.968** | **0.942** | 125 |
| Mesophile | 0.982 | 0.974 | 0.978 | 7,576 |
| Psychrophile | 0.539 | 0.636 | 0.584 | 206 |
| Thermophile | 0.882 | 0.906 | 0.894 | 732 |

> **観察:**
> - **Hyperthermophile の Recall = 0.968** は両モデル共通で極めて高く、**見逃しはほぼない**。ビジネス上最重要な指標をクリア。
> - **Psychrophile が最難クラス**（F1 = 0.58–0.62）。サンプル数は Hyperthermophile より多い（206）が、`Tmin < 20 ℃` の境界周辺で Mesophile と誤分類される傾向がありそう。

---

## 4. 計画書目標との突合

| 指標 | 目標 | RF 実績 | 判定 |
|---|---|---|---|
| Weighted F1 ≥ 0.95 | 0.95 | **0.963** | ✅ |
| Macro F1 ≥ 0.75 | 0.75 | **0.858** | ✅ |
| Hyperthermophile F1 ≥ 0.80 | 0.80 | **0.934** | ✅ |
| Hyperthermophile Recall ≥ 0.85 | 0.85 | **0.968** | ✅ |

**4 項目すべてクリア**。特に超好熱株の Recall 0.968 は「研究候補の取りこぼしゼロ近傍」を意味し、ビジネス目的に沿った結果。

---

## 5. 最終モデルの特徴量重要度（Top 10）

Random Forest の **feature_importances_** から算出。

| 順位 | 特徴量 | 重要度 |
|---|---|---|
| 1 | **Tmax** | 0.298 |
| 2 | **Tmean**（新規） | 0.276 |
| 3 | **Tmin** | 0.154 |
| 4 | **16S_GC** | 0.102 |
| 5 | superkingdom_Bacteria | 0.036 |
| 6 | **GC_diff**（新規） | 0.028 |
| 7 | superkingdom_Archaea | 0.026 |
| 8 | Genome_GC | 0.024 |
| 9 | Tmax_Tmin | 0.020 |
| 10 | **log_Genome_size**（新規） | 0.012 |

### 読み取り

1. **上位 3 はすべて温度端点系**（Tmax + Tmean + Tmin = 72.7 % の重要度）。
   Phase 2 の仮説検定で示した「温度カテゴリは温度指標と強く関連」と整合。
2. **`Tmean`（新規特徴量）が 2 位**。単純な平均でも `Tmax_Tmin`（9 位）より遥かに情報量が大きい。
   特徴量エンジニアリングの価値が数値で示された。
3. **`16S_GC` が 4 位（0.102）** — Phase 2 ANOVA（η² = 0.249）と整合。
   高温適応の分子指標として確かに効いている。
4. **`superkingdom` の One-Hot が 5〜7 位** — 系統情報は**補完的**な役割。
   温度指標が強すぎるため、系統を直接使わなくても分類可能。
5. **新規特徴量の寄与**:
   - `Tmean` = **2 位**（0.276）: 強力
   - `GC_diff` = **6 位**（0.028）: 中程度
   - `log_Genome_size` = **10 位**（0.012）: 小さいが Top 10 入り

---

## 6. プロジェクトへの含意

1. **RF と XGBoost はほぼ同等**。解釈性・学習速度・ハイパーパラメータ数で **RF が運用に向く**。
2. **`Tmean` という単純な派生特徴量が極めて強力** — 特徴量エンジニアリングの基本（平均・差分・対数）は依然として効果的。
3. **Hyperthermophile 予測は実用レベル**（Recall 0.968）。極限環境微生物プログラムへの**スクリーニングツール**としてすぐに投入可能。
4. **Psychrophile 予測が弱点**（F1 ≈ 0.62）。改善余地として:
   - 寒冷適応の特有マーカー（脂質組成・冷感応答遺伝子など）を特徴量化
   - Psychrophile 専用の二項分類器を追加（二段構成）
5. **Phase 1〜3 の連続性**:
   - Phase 1 EDA: 「Archaea は温度分布が広い」「超好熱の 92 % が Archaea」
   - Phase 2 仮説検定: それらが統計的に有意（Cohen's d=1.17、Cramér's V=0.44）
   - Phase 3 分類: **同じ特徴量**（温度指標 + 16S_GC + superkingdom）で **macro F1=0.858**
   - **記述 → 検証 → 予測**が一貫したストーリーで結実。

---

## 7. 制限事項

- **Psychrophile の F1 = 0.62** は他クラスより明確に低い。
  Mesophile との境界（Tmin < 20 ℃）付近での誤分類が多いと推測される。
- **2020 年版スナップショット**を前提に学習しており、新分類・新種への適用では性能低下の可能性。
- **クラス閾値は固定**（Topt_ave で機械的に決定）。実業務では目的に応じてしきい値を動かす余地がある。
- **解釈性は限定的**。RF の feature_importances_ は平均的貢献で、個別予測の説明には SHAP 等が望ましい。

---

## 8. 次ステップ候補

- [ ] **Psychrophile 改善**: SMOTE / コスト感度 / 寒冷適応マーカーの追加
- [ ] **SHAP 値**でクラスごとの貢献を可視化（個別予測の説明性）
- [ ] **学習曲線**でサンプルサイズ依存性を確認
- [ ] **しきい値調整**（classification_report ではなく predict_proba + カスタム閾値）
- [ ] **二段構成**: (i) 超好熱か否か、(ii) それ以外の温度帯分類
- [ ] **NCBI Taxonomy / 環境メタデータ**の外部結合で特徴量を拡張（Phase 1 EDA で提案済み）

---

## 9. 成果物

| ファイル | 内容 |
|---|---|
| `notebooks/topt_classification.ipynb` | 実行済み Notebook（154 KB、全結果確認可） |
| `notebooks/build_classification_notebook.py` | Notebook 再生成スクリプト |
| `models/temp_cat_classifier_randomforest.joblib` | 全データ再学習した最終モデル |
| `docs/classification_plan_ja.md` | 本計画書 |
| `docs/classification_results_ja.md` | この結果サマリー |

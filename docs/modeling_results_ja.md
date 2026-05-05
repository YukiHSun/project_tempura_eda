# `Topt_ave` 予測モデル 実行結果（日本語版）

> **計画書:** [`modeling_plan_ja.md`](./modeling_plan_ja.md)
> **ノートブック:** [`../notebooks/topt_regression.ipynb`](../notebooks/topt_regression.ipynb)
> **実行日:** 2026-05-06
> **判定:** ✅ すべての目標値を達成（一部は大幅に上回る）

---

## 0. 結論（1 行）

**HistGradientBoosting が全体 MAE 2.50 ℃・R² 0.918 を達成**。
Archaea サブグループでも MAE 2.85 ℃・R² 0.968 と精度を落とさず、
計画書の目標値（全体 MAE ≤ 4.0、Archaea MAE ≤ 6.0）を大幅にクリアした。

---

## 1. CV 分割の健全性チェック

superkingdom を層化キーに 5-fold 分割した結果、
各 fold の Archaea 株数がほぼ均等に配分された:

| fold | Bacteria | Archaea |
|---|---|---|
| 1 | 1,618 | 110 |
| 2 | 1,618 | 110 |
| 3 | 1,618 | 110 |
| 4 | 1,618 | 110 |
| 5 | 1,618 | 109 |

計画書の懸念（Archaea が偏る）は回避できた。

---

## 2. モデル別 CV スコア（全体 / サブグループ）

### 2.1 主要指標

| model | subgroup | MAE | RMSE | R² |
|---|---|---|---|---|
| Dummy (mean) | ALL | 7.340 | 11.559 | −0.000 |
| Dummy (mean) | Bacteria | 6.557 | 9.494 | −0.017 |
| Dummy (mean) | Archaea | 18.875 | 27.829 | −0.720 |
| **Ridge** | **ALL** | **2.824** | **3.620** | **0.902** |
| Ridge | Bacteria | 2.791 | 3.580 | 0.855 |
| Ridge | Archaea | 3.303 | 4.161 | 0.962 |
| **HistGradientBoosting** | **ALL** | **2.504** | **3.315** | **0.918** |
| HistGradientBoosting | Bacteria | 2.481 | 3.281 | 0.879 |
| HistGradientBoosting | Archaea | 2.845 | 3.776 | 0.968 |

### 2.2 横並びの可読ビュー

```
                        MAE                     RMSE                      R²
subgroup                ALL  Archaea  Bacteria   ALL  Archaea  Bacteria    ALL  Archaea  Bacteria
Dummy (mean)          7.340  18.875    6.557  11.559  27.829    9.494 -0.000  -0.720   -0.017
HistGradientBoosting  2.504   2.845    2.481   3.315   3.776    3.281  0.918   0.968    0.879
Ridge                 2.824   3.303    2.791   3.620   4.161    3.580  0.902   0.962    0.855
```

### 2.3 温度カテゴリ別の MAE（監査）

| model | Psychro | Meso | Thermo | Hyperthermo |
|---|---|---|---|---|
| Dummy (mean) | 18.76 | 4.61 | 24.35 | 54.19 |
| Ridge | 4.71 | 2.71 | 3.28 | 3.97 |
| HistGradientBoosting | 4.92 | 2.35 | 3.37 | 3.07 |

**読み取り:**
- 超好熱（≥ 80 ℃）でも **MAE ≤ 5 ℃** に抑えられている。
- 最も難しいのは好冷（< 20 ℃）。株数が 206 と少ないことが一因。

---

## 3. 計画書目標との突合

| 指標 | 目標 | Ridge 実績 | HistGB 実績 | 達成 |
|---|---|---|---|---|
| 全体 MAE ≤ 4.0 ℃ | 4.0 | **2.82** | **2.50** | ✅ |
| 全体 RMSE ≤ 6.0 ℃ | 6.0 | **3.62** | **3.32** | ✅ |
| 全体 R² ≥ 0.85 | 0.85 | **0.902** | **0.918** | ✅ |
| Bacteria MAE ≤ 3.5 ℃ | 3.5 | **2.79** | **2.48** | ✅ |
| Archaea MAE ≤ 6.0 ℃ | 6.0 | **3.30** | **2.85** | ✅ |
| Archaea R² ≥ 0.70 | 0.70 | **0.962** | **0.968** | ✅ |

→ **全目標をクリア**。最良は HistGradientBoosting だが、
解釈性を重視するなら Ridge も十分実用レベル。

---

## 4. Ridge 係数（特徴量の解釈）

（`alpha = 10.0` が CV で選択された。標準化後の係数絶対値 Top-12）

| 順位 | 特徴量 | 係数 | 解釈 |
|---|---|---|---|
| 1 | `Tmax` | +5.42 | 上限温度が高いほど Topt も高い（当然） |
| 2 | `Tmin` | +5.35 | 下限温度が高いほど Topt も高い |
| 3 | `phylum_grouped_Other` | +1.49 | マイナー門に属する株は高温寄り |
| 4 | `Tmax_Tmin` | +1.42 | 温度幅が広いほど高温寄りになる傾向 |
| 5 | `phylum_grouped_Euryarchaeota` | −1.04 | 古細菌の一門 |
| 6 | `superkingdom_Bacteria` | −0.99 | Bacteria は相対的に低温寄り |
| 7 | `superkingdom_Archaea` | +0.99 | Archaea は相対的に高温寄り |
| 8 | `Genome_GC` | −0.88 | GC 含量が高い株は低温寄り（弱い関係） |
| 9 | `16S_GC` | +0.74 | 16S rRNA の GC は高温と正相関 |
| 10 | `phylum_grouped_Actinobacteria` | −0.59 | — |

**主要知見:**
- 予測の主軸は **`Tmin` と `Tmax`**。温度端点を与えれば Topt はほぼ決まる。
- 分類情報（superkingdom / phylum）は**補助的**だが無視できない寄与をする。
- `Genome_GC` と `16S_GC` の**符号が逆**であるのは、
  16S GC には温度環境の直接的シグナル（熱安定性）が乗りやすいためと解釈できる。

---

## 5. 残差分析（ノートブック §9 の図から）

- 残差は **0 付近に集中** し、superkingdom 別に偏りなし。
- 大きな残差（|r| ≥ 15 ℃）は **40 株未満**。これらはほぼ
  psychrophile（極端に低い Tmin）と超好熱 Archaea（極端に高い Tmax）。
- 単純な外れ値除外では解決しない**実在のシグナル**。

---

## 6. 最終モデルとしての選択

### 6.1 採用モデル

| 評価観点 | 最適 |
|---|---|
| 精度（CV MAE 最小） | **HistGradientBoosting** |
| 解釈性 | **Ridge** |
| 推論速度 | ほぼ同等（数百ミリ秒オーダー） |
| 実装の単純さ | Ridge > HistGB |

**推奨:** **初期導入は Ridge**（係数で説明責任を果たせる）、
**精度重視の本番化時に HistGradientBoosting** に切り替える。

### 6.2 保存ファイル

- `models/topt_regressor_histgradientboosting.joblib`（HistGB、全データ再学習）
- 必要に応じて `topt_regressor_ridge.joblib` も出力可能。

---

## 7. 残る制限と今後

| 項目 | 内容 | 次アクション |
|---|---|---|
| Psychrophile の MAE が相対的に高い | 株数が 206 と少ない | データ追加 or 重み付け |
| 未見の `phylum` への対応 | 2020 年版の分類体系 | NCBI Taxonomy と突合してリネームを反映 |
| 温度 × 分類の交互作用 | Ridge では捉えにくい | HistGB を本番採用 or 特徴量交互作用を明示 |
| モデルカード未整備 | 倫理・ガバナンスは文書化のみ | `docs/model_card_ja.md` を追加予定 |

---

## 8. まとめ

- **全体 MAE 2.50 ℃・R² 0.918** は `Topt_ave` 予測として**十分実用域**。
- 層化 CV とサブグループメトリクスにより、
  **Archaea でも精度を落とさない**ことを確認できた。
- 次ステップは **4 クラス分類（`temp_cat`）** と、
  **NCBI Taxonomy 連携による特徴量拡張**。

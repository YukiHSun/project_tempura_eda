# 分類モデル計画書（日本語版）— `temp_cat` 予測

> **対象:** 原核生物 8,639 株（TEMPURA）を温度カテゴリ（好冷/中温/好熱/超好熱）に分類する
> **位置づけ:** Phase 1 (EDA) → 1.5 (回帰) → 2 (仮説検定) に続く **Phase 3: 分類 + 特徴量エンジニアリング**
> **作成日:** 2026-05-06
> **作成者:** データプロフェッショナル（TEMPURA プロジェクト）

---

## 0. なぜこのフェーズか

- **Phase 1.5 の回帰**は `Topt_ave`（連続値）を予測した。
- 一方、研究マネージャーの**アクション**は「**どのカテゴリに属するか**」で決まることが多い:
  - 超好熱（≥ 80 ℃）株 → 極限環境プログラムの優先候補
  - 好熱（45–80 ℃）株 → 産業用酵素スクリーニング候補
  - 中温・好冷 → 一般参照株
- 連続値 `Topt_ave` より**カテゴリ予測**のほうが意思決定に直結する。
- 分類タスクは、データサイエンスのコア工程である
  **特徴量エンジニアリング + ハイパーパラメータチューニング + モデル比較**
  を練習するのに最適。

---

## 1. 目的・成功基準（Ask）

### 1.1 事業目的

新規株の `Tmin`・`Tmax`・GC 含量・分類情報から **温度カテゴリ**を予測し、
研究マネージャーが「スクリーニングの初期仮説」を立てる段階で使えるモデルを提供する。

### 1.2 目的変数

`temp_cat`（4 クラス）:

| カテゴリ | Topt 範囲 | 該当数 | 割合 |
|---|---|---|---|
| Psychrophile | < 20 ℃ | 206 | 2.4 % |
| Mesophile | 20–45 ℃ | 7,576 | 87.7 % |
| Thermophile | 45–80 ℃ | 732 | 8.5 % |
| Hyperthermophile | ≥ 80 ℃ | 125 | 1.4 % |

**典型的なクラス不均衡**であり、Accuracy だけでは評価不十分。

### 1.3 数値目標

| 指標 | 目標値 | 根拠 |
|---|---|---|
| **Weighted F1** | ≥ 0.95 | 総合評価。多数派 Mesophile に引きずられすぎない |
| **Macro F1** | ≥ 0.75 | 各クラスを**等しく**重視。少数派への公平性 |
| **Hyperthermophile の F1** | ≥ 0.80 | ビジネス上最重要カテゴリ |
| **Hyperthermophile の Recall** | ≥ 0.85 | 見逃し（FN）を最小化。研究候補を取りこぼさない |

---

## 2. 想定外・スコープ外

- 時系列予測ではない。
- 2020 年版以降の新種への適用（taxonomy 体系変化）。
- ハードラベルのしきい値は固定（`Topt_ave` で機械的に決定）。

---

## 3. データと特徴量エンジニアリング（Prepare）

### 3.1 入力

- `data/raw/tempura.csv` — 8,639 行 × 20 列。

### 3.2 既存特徴量（Phase 1.5 から継続）

| 名前 | 型 | 備考 |
|---|---|---|
| `Tmin`, `Tmax`, `Tmax_Tmin` | 数値 | 100 % 埋まっている |
| `16S_GC`, `Genome_GC` | 数値 | 欠損少 |
| `superkingdom` | カテゴリ | Bacteria / Archaea |
| `phylum_grouped` | カテゴリ | 出現率 ≥ 1 % の門 + Other |

### 3.3 新規特徴量（Feature Engineering）

Phase 3 で追加する派生特徴量:

| 名前 | 計算式 | 狙い |
|---|---|---|
| **`log_Genome_size`** | log1p(Genome_size) | 歪んだ分布を対数正規化（data-train-21 の教訓） |
| **`GC_diff`** | Genome_GC − 16S_GC | 分子特性の差分として温度適応を捉える |
| **`Tmean`** | (Tmin + Tmax) / 2 | 温度範囲の中心。Topt と強相関が見込まれる |

**注意:** Phase 1.5 では `Tmin`・`Tmax` から `Topt_ave` を予測したが、
本フェーズは**温度カテゴリ（`Topt_ave` の離散化）**を予測するため、
`Tmin` / `Tmax` から間接的に `Topt` を**再構成する形**になる。これはデータ
リークではなく「**温度端点から最適温度帯を推論**」という問題設定。

### 3.4 前処理

- 数値: `SimpleImputer(strategy='median')` + `StandardScaler`（RF は不要だが XGBoost のツリー前提でも害なし）
- カテゴリ: `SimpleImputer(fill_value='Unknown')` + `OneHotEncoder(handle_unknown='ignore')`
- クラス不均衡対策: XGBoost は `sample_weight`、RF は `class_weight='balanced'`

---

## 4. モデル候補（Construct）

### 4.1 ベースライン
- **DummyClassifier（most_frequent）**: 常に多数派（Mesophile）を予測
- Accuracy は高く出るが、macro F1 はほぼゼロ → クラス不均衡の指標ギャップを示す

### 4.2 本命モデル 1 — Random Forest
- 特徴量重要度が自然に計算できる
- `class_weight='balanced'` で不均衡対応
- 多重共線性・外れ値に強い（data-train-23 の教訓）

### 4.3 本命モデル 2 — XGBoost
- 勾配ブースティングの高精度
- 少数派クラスに強く反応する性質
- `sample_weight` で不均衡対応

### 4.4 ハイパーパラメータ（GridSearchCV）

**Random Forest:**
| パラメータ | 探索範囲 |
|---|---|
| `n_estimators` | [200, 400] |
| `max_depth` | [6, 12, None] |
| `min_samples_leaf` | [1, 3] |

**XGBoost:**
| パラメータ | 探索範囲 |
|---|---|
| `n_estimators` | [200, 400] |
| `max_depth` | [4, 6, 8] |
| `learning_rate` | [0.05, 0.1] |

（グリッド総数が過大にならないよう控えめに設定）

---

## 5. 検証プロトコル（Analyze）

### 5.1 分割戦略
- **StratifiedKFold(n_splits=5)**: `temp_cat` で層化。各 fold に全クラスが含まれる
- `random_state=42` を固定
- GridSearchCV の refit 基準: **macro F1**（少数派重視）

### 5.2 評価指標（すべて報告）

| 指標 | なぜ必要か |
|---|---|
| **Accuracy** | 全体の正解率（多数派に引きずられるので補助指標） |
| **Precision (macro / weighted)** | 誤陽性（他クラスを間違って超好熱と分類）の回避 |
| **Recall (macro / weighted)** | 見逃し（超好熱を中温と分類）の回避 |
| **F1 (macro / weighted)** | Precision と Recall のバランス指標 |
| **Confusion Matrix** | クラス間の誤分類パターンを可視化 |

### 5.3 最適モデルの検証スコア
- GridSearchCV の best_score_（macro F1 の CV 平均）を最適モデルの検証スコアとして報告

### 5.4 特徴量重要度
- 最終モデル（RF または XGBoost のうち性能が優れた方）について
  **上位 10 件の特徴量**を bar chart で可視化
- One-Hot で分解されたカテゴリも個別にランキング

---

## 6. 公平性・ガバナンス

- **Hyperthermophile は n=125** と少なく、CV fold あたり ~25 件。
  - 層化 CV で fold ごとに必ず含まれるようにする
  - Recall を最重要指標に据える（見逃し回避）
- **2020 年版スナップショット**への注記はモデルカードに記載

---

## 7. 成果物

| ファイル | 目的 |
|---|---|
| `notebooks/topt_classification.ipynb` | 分類モデル学習・評価の Notebook |
| `notebooks/build_classification_notebook.py` | Notebook 再生成スクリプト |
| `docs/classification_results_ja.md` | 結果サマリー |
| `README.md`（更新） | Phase 3 セクション追加 |
| `requirements.txt`（更新） | xgboost を追加 |

---

## 8. 実行ステップ（チェックリスト）

- [ ] Step 1. 依存環境チェック（xgboost）
- [ ] Step 2. データ読み込み + 新規特徴量エンジニアリング
- [ ] Step 3. 前処理パイプライン構築
- [ ] Step 4. ベースライン（Dummy）実行
- [ ] Step 5. Random Forest GridSearchCV
- [ ] Step 6. XGBoost GridSearchCV
- [ ] Step 7. 最適モデルの指標集計（Accuracy/Precision/Recall/F1）
- [ ] Step 8. 混同行列の可視化（両モデル）
- [ ] Step 9. 最終モデル（より優秀な方）の特徴量重要度 Top 10 を可視化
- [ ] Step 10. 結果を `classification_results_ja.md` に清書

---

## 9. リスクと緩和

| リスク | 影響 | 緩和策 |
|---|---|---|
| Hyperthermophile n=125 で fold ごとのばらつき | 中 | 層化 CV + sample_weight / class_weight |
| XGBoost と RF が同等性能 → 選択の判断基準 | 低 | macro F1 を最優先、同点なら解釈性の高い RF |
| GridSearch が時間超過 | 低 | グリッドを控えめに設定、n_jobs=-1 |
| 特徴量リーケージ | 高 | `Topt_ave` / `Topt_low` / `Topt_high` は特徴量から除外 |

---

## 10. 実行後の判断ポイント

- **両目標達成**: そのまま確定し、モデルを保存
- **Hyperthermophile の Recall 未達**: SMOTE などのオーバーサンプリング、コスト感度しきい値調整を次ステップとして提案
- **過学習の兆候**: 訓練 F1 ≫ CV F1 なら正則化を強化

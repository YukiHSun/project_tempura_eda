"""Build topt_classification.ipynb programmatically using nbformat."""
import nbformat as nbf

nb = nbf.v4.new_notebook()
cells = []

cells.append(nbf.v4.new_markdown_cell("""# Temp_cat Classification — TEMPURA (Phase 3)

**計画書:** [`../docs/classification_plan_ja.md`](../docs/classification_plan_ja.md)

本ノートは、原核生物 8,639 株の **温度カテゴリ `temp_cat`**
（Psychrophile / Mesophile / Thermophile / Hyperthermophile）を
`Tmin` / `Tmax` / GC 含量 / 分類情報から予測する分類モデルを学習・比較する。

1. **特徴量エンジニアリング**: `log_Genome_size`、`GC_diff`、`Tmean` を追加
2. **5-fold StratifiedKFold** + **GridSearchCV** でハイパーパラメータ調整
3. **Random Forest** vs **XGBoost** を比較
4. **Accuracy / Precision / Recall / F1** を報告
5. **混同行列**を両モデルで可視化
6. **最終モデルの特徴量重要度 Top 10** を表示"""))

cells.append(nbf.v4.new_markdown_cell("## 1. セットアップ"))
cells.append(nbf.v4.new_code_cell("""import warnings
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report, confusion_matrix, ConfusionMatrixDisplay,
)
from sklearn.model_selection import StratifiedKFold, GridSearchCV, cross_val_predict
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder, OneHotEncoder, StandardScaler

import xgboost as xgb

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 160)
sns.set_theme(style='whitegrid')
RNG = 42
print(f'xgboost {xgb.__version__}')"""))

cells.append(nbf.v4.new_markdown_cell("""## 2. データ読み込み + 派生列（特徴量エンジニアリング）

- `temp_cat` は EDA と同じ 4 カテゴリ。
- `phylum_grouped` は出現率 ≥ 1 % の門だけ残し、それ以外は `Other`。
- **新規特徴量**: `log_Genome_size`、`GC_diff`、`Tmean`"""))
cells.append(nbf.v4.new_code_cell("""df = pd.read_csv('../data/raw/tempura.csv')

def temp_category(t):
    if t < 20:  return 'Psychrophile'
    if t < 45:  return 'Mesophile'
    if t < 80:  return 'Thermophile'
    return 'Hyperthermophile'
df['temp_cat'] = df['Topt_ave'].apply(temp_category)

# 門の集約
phylum_counts = df['phylum'].value_counts(normalize=True)
top_phyla = phylum_counts[phylum_counts >= 0.01].index.tolist()
df['phylum_grouped'] = np.where(df['phylum'].isin(top_phyla), df['phylum'], 'Other')
df['phylum_grouped'] = df['phylum_grouped'].fillna('Unknown')

# --- 新規特徴量 ---
df['log_Genome_size'] = np.log1p(df['Genome_size'])     # 歪んだ分布を対数正規化
df['GC_diff']         = df['Genome_GC'] - df['16S_GC']  # GC 差分
df['Tmean']           = (df['Tmin'] + df['Tmax']) / 2   # 温度範囲の中心

print(f"Rows : {len(df):,}")
print(f"Kept phyla (≥1%): {len(top_phyla)}")
print()
print("temp_cat distribution:")
print(df['temp_cat'].value_counts())
print()
print("New features summary:")
print(df[['log_Genome_size', 'GC_diff', 'Tmean']].describe().round(3))"""))

cells.append(nbf.v4.new_markdown_cell("## 3. 特徴量 / 目的変数の定義"))
cells.append(nbf.v4.new_code_cell("""NUMERIC_FEATURES = [
    'Tmin', 'Tmax', 'Tmax_Tmin', 'Tmean',
    '16S_GC', 'Genome_GC', 'GC_diff',
    'log_Genome_size',
]
CATEGORICAL_FEATURES = ['superkingdom', 'phylum_grouped']

X = df[NUMERIC_FEATURES + CATEGORICAL_FEATURES].copy()

# ラベルエンコード（0=Psychro, 1=Meso, 2=Thermo, 3=Hyper の順に固定）
CLASS_ORDER = ['Psychrophile', 'Mesophile', 'Thermophile', 'Hyperthermophile']
le = LabelEncoder()
le.fit(CLASS_ORDER)
y = le.transform(df['temp_cat'])
class_names = list(le.classes_)

print('X shape :', X.shape)
print('y shape :', y.shape)
print('classes :', class_names)
print('class counts:', np.bincount(y))"""))

cells.append(nbf.v4.new_markdown_cell("""## 4. 前処理パイプライン

- 数値: median 補完 → 標準化
- カテゴリ: Unknown 補完 → One-Hot"""))
cells.append(nbf.v4.new_code_cell("""numeric_pipe = Pipeline([
    ('imputer', SimpleImputer(strategy='median')),
    ('scaler', StandardScaler()),
])
categorical_pipe = Pipeline([
    ('imputer', SimpleImputer(strategy='constant', fill_value='Unknown')),
    ('onehot', OneHotEncoder(handle_unknown='ignore')),
])
preprocess = ColumnTransformer([
    ('num', numeric_pipe, NUMERIC_FEATURES),
    ('cat', categorical_pipe, CATEGORICAL_FEATURES),
])
preprocess"""))

cells.append(nbf.v4.new_markdown_cell("""## 5. CV 定義（temp_cat で層化）"""))
cells.append(nbf.v4.new_code_cell("""cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RNG)
for i, (tr, va) in enumerate(cv.split(X, y), 1):
    dist = pd.Series(y[va]).value_counts().sort_index()
    print(f'fold {i} valid: ' + ', '.join(f'{class_names[k]}={v}' for k, v in dist.items()))"""))

cells.append(nbf.v4.new_markdown_cell("""## 6. ベースライン（Dummy Classifier）

常に多数派（Mesophile）を予測するモデル。Accuracy は高く、macro F1 はほぼゼロ
になるはず。クラス不均衡の典型症状を確認する。"""))
cells.append(nbf.v4.new_code_cell("""dummy = Pipeline([
    ('preprocess', preprocess),
    ('model', DummyClassifier(strategy='most_frequent', random_state=RNG)),
])
y_pred_dummy = cross_val_predict(dummy, X, y, cv=cv, n_jobs=-1)

def score_row(name, y_true, y_pred):
    return {
        'model':        name,
        'accuracy':     accuracy_score(y_true, y_pred),
        'precision_w':  precision_score(y_true, y_pred, average='weighted', zero_division=0),
        'recall_w':     recall_score(y_true, y_pred, average='weighted', zero_division=0),
        'f1_w':         f1_score(y_true, y_pred, average='weighted', zero_division=0),
        'precision_m':  precision_score(y_true, y_pred, average='macro', zero_division=0),
        'recall_m':     recall_score(y_true, y_pred, average='macro', zero_division=0),
        'f1_m':         f1_score(y_true, y_pred, average='macro', zero_division=0),
    }

rows = [score_row('Dummy (most_frequent)', y, y_pred_dummy)]
pd.DataFrame(rows).round(3)"""))

cells.append(nbf.v4.new_markdown_cell("""## 7. Random Forest — GridSearchCV

`class_weight='balanced'` で不均衡対応。`refit` 基準は **macro F1**（少数派重視）。"""))
cells.append(nbf.v4.new_code_cell("""rf_pipe = Pipeline([
    ('preprocess', preprocess),
    ('model', RandomForestClassifier(class_weight='balanced', random_state=RNG, n_jobs=-1)),
])
rf_grid = {
    'model__n_estimators':     [200, 400],
    'model__max_depth':        [6, 12, None],
    'model__min_samples_leaf': [1, 3],
}
rf_search = GridSearchCV(
    rf_pipe, rf_grid,
    scoring='f1_macro',
    cv=cv, n_jobs=-1, verbose=0, refit=True,
)
rf_search.fit(X, y)

print('Best RF params    :', rf_search.best_params_)
print(f'Best RF CV macro-F1: {rf_search.best_score_:.4f}')"""))

cells.append(nbf.v4.new_code_cell("""# ベストモデルで CV 予測を取得して指標計算
y_pred_rf = cross_val_predict(rf_search.best_estimator_, X, y, cv=cv, n_jobs=-1)
rows.append(score_row('RandomForest (tuned)', y, y_pred_rf))
pd.DataFrame(rows).round(3)"""))

cells.append(nbf.v4.new_markdown_cell("""## 8. XGBoost — GridSearchCV

`sample_weight` で不均衡を反映させる。"""))
cells.append(nbf.v4.new_code_cell("""# クラスごとの重みを算出（sample_weight）
class_counts = np.bincount(y)
sample_weight = np.array([len(y) / (len(class_counts) * class_counts[c]) for c in y])

xgb_pipe = Pipeline([
    ('preprocess', preprocess),
    ('model', xgb.XGBClassifier(
        objective='multi:softprob',
        num_class=len(class_names),
        tree_method='hist',
        random_state=RNG,
        n_jobs=-1,
        eval_metric='mlogloss',
    )),
])
xgb_grid = {
    'model__n_estimators':  [200, 400],
    'model__max_depth':     [4, 6, 8],
    'model__learning_rate': [0.05, 0.1],
}
xgb_search = GridSearchCV(
    xgb_pipe, xgb_grid,
    scoring='f1_macro',
    cv=cv, n_jobs=-1, verbose=0, refit=True,
)
xgb_search.fit(X, y, model__sample_weight=sample_weight)

print('Best XGB params    :', xgb_search.best_params_)
print(f'Best XGB CV macro-F1: {xgb_search.best_score_:.4f}')"""))

cells.append(nbf.v4.new_code_cell("""y_pred_xgb = cross_val_predict(
    xgb_search.best_estimator_, X, y, cv=cv, n_jobs=-1,
    fit_params={'model__sample_weight': sample_weight},
)
rows.append(score_row('XGBoost (tuned)', y, y_pred_xgb))
pd.DataFrame(rows).round(3)"""))

cells.append(nbf.v4.new_markdown_cell("""## 9. モデル比較サマリ"""))
cells.append(nbf.v4.new_code_cell("""summary = pd.DataFrame(rows).round(3)
summary"""))

cells.append(nbf.v4.new_code_cell("""# 各モデルのクラス別 classification_report
print('\\n=== Random Forest (tuned) ===')
print(classification_report(y, y_pred_rf, target_names=class_names, digits=3))

print('\\n=== XGBoost (tuned) ===')
print(classification_report(y, y_pred_xgb, target_names=class_names, digits=3))"""))

cells.append(nbf.v4.new_markdown_cell("""## 10. 混同行列

両モデルを横並びで可視化。"""))
cells.append(nbf.v4.new_code_cell("""fig, axes = plt.subplots(1, 2, figsize=(14, 5))

for ax, title, y_pred in [
    (axes[0], 'Random Forest', y_pred_rf),
    (axes[1], 'XGBoost',       y_pred_xgb),
]:
    cm = confusion_matrix(y, y_pred)
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=class_names)
    disp.plot(ax=ax, colorbar=False, cmap='Blues', values_format='d')
    ax.set_title(title)
    ax.set_xticklabels(class_names, rotation=30, ha='right')

plt.tight_layout()
plt.show()"""))

cells.append(nbf.v4.new_markdown_cell("""## 11. 最終モデル選定と特徴量重要度 Top 10

macro F1（CV）で優れた方を最終モデルとする。"""))
cells.append(nbf.v4.new_code_cell("""rf_f1  = rf_search.best_score_
xgb_f1 = xgb_search.best_score_
print(f'RF  macro-F1 (CV): {rf_f1:.4f}')
print(f'XGB macro-F1 (CV): {xgb_f1:.4f}')

if xgb_f1 >= rf_f1:
    best_name, best_pipe = 'XGBoost', xgb_search.best_estimator_
else:
    best_name, best_pipe = 'RandomForest', rf_search.best_estimator_
print(f'\\n=> 最終モデル: {best_name}')"""))

cells.append(nbf.v4.new_code_cell("""# 前処理後の特徴量名を復元
preprocess_fitted = best_pipe.named_steps['preprocess']
num_names = NUMERIC_FEATURES
cat_enc = preprocess_fitted.named_transformers_['cat']['onehot']
cat_names = cat_enc.get_feature_names_out(CATEGORICAL_FEATURES).tolist()
feat_names = num_names + cat_names

# 特徴量重要度（どちらのモデルでも feature_importances_ が使える）
importances = best_pipe.named_steps['model'].feature_importances_
imp_df = (pd.DataFrame({'feature': feat_names, 'importance': importances})
            .sort_values('importance', ascending=False)
            .reset_index(drop=True))
print(f'=== {best_name}: Top 10 feature importances ===')
imp_df.head(10)"""))

cells.append(nbf.v4.new_code_cell("""# 可視化
top = imp_df.head(10).iloc[::-1]  # 上から大きい順に見せるため逆順
fig, ax = plt.subplots(figsize=(8, 5))
ax.barh(top['feature'], top['importance'], color='#4c72b0')
ax.set_xlabel('Feature importance')
ax.set_title(f'{best_name}: Top 10 Feature Importances')
plt.tight_layout()
plt.show()"""))

cells.append(nbf.v4.new_markdown_cell("""## 12. 計画書目標との突合

| 指標 | 目標 | 判定 |
|---|---|---|
| Weighted F1 ≥ 0.95 | TBD | §9 の結果を参照 |
| Macro F1 ≥ 0.75 | TBD |  |
| Hyperthermophile F1 ≥ 0.80 | TBD | §9 の classification_report |
| Hyperthermophile Recall ≥ 0.85 | TBD |  |

→ 結果は `docs/classification_results_ja.md` に清書する。"""))

cells.append(nbf.v4.new_markdown_cell("""## 13. 最終モデルの保存"""))
cells.append(nbf.v4.new_code_cell("""import os, joblib
os.makedirs('../models', exist_ok=True)
path = f'../models/temp_cat_classifier_{best_name.lower()}.joblib'
joblib.dump(best_pipe, path)
print('saved:', path)"""))

nb['cells'] = cells
with open('topt_classification.ipynb', 'w') as f:
    nbf.write(nb, f)
print('topt_classification.ipynb written.')

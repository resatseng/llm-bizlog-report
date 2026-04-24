# -*- coding: utf-8 -*-
"""產生 L-PhaseM分層聚類.ipynb"""
import json

OUT = r"d:\yujui\痛點需求地圖\prompt定版\L-PhaseM分層聚類.ipynb"

def cc(cid, src):
    return {"cell_type":"code","id":cid,"metadata":{},"outputs":[],"execution_count":None,"source":src}
def mc(cid, src):
    return {"cell_type":"markdown","id":cid,"metadata":{},"source":src}

# ── Cell 內容 ─────────────────────────────────────────────────────────────────

SRC_TITLE = "\n".join([
    "# L-1 Phase M：分層聚類 + Map + 熱路徑",
    "",
    "從 `company_labels.jsonl`（法人標籤）與 `phase_l_final.csv`（L層事件）：",
    "",
    "1. **分層聚類**：依法人標籤向量將公司分群（KMeans k=7）",
    "2. **Map**：PCA 2D 降維視覺化座標",
    "3. **熱路徑**：公司在 L1–L7 間的時序路徑 Top-N 分析",
    "",
    "**執行前提**：`company_labels.jsonl` 及 `phase_l_final.csv` 均已存在。",
])

SRC_S0 = "!pip install scikit-learn pandas tqdm numpy"

SRC_S1 = "\n".join([
    "import os, json, re",
    "from pathlib import Path",
    "from collections import Counter",
    "import numpy as np",
    "import pandas as pd",
    "from sklearn.preprocessing import StandardScaler",
    "from sklearn.cluster import KMeans",
    "from sklearn.decomposition import PCA",
    "from tqdm.auto import tqdm",
    "",
    "# ── 路徑設定 ──────────────────────────────────────────",
    'BASE_DIR       = Path(r"D:\\yujui\\痛點需求地圖")',
    'CORP_JSONL     = BASE_DIR / "corp_label_output" / "company_labels.jsonl"',
    'PHASE_L_CSV    = BASE_DIR / "step3_output"       / "phase_l_final.csv"',
    'OUTPUT_DIR     = BASE_DIR / "phaseM_output"',
    "OUTPUT_DIR.mkdir(parents=True, exist_ok=True)",
    "",
    "# ── 聚類設定 ──────────────────────────────────────────",
    "N_CLUSTERS   = 7      # 分群數（對應 L1–L7 層數）",
    "RANDOM_STATE = 42",
    "TOP_PATH_N   = 30     # 熱路徑顯示前 N 條",
    "MIN_PATH_LEN = 2      # 最短路徑長度（至少 2 個 L 層）",
    "",
    'print("設定完成")',
    'print(f"  CORP_JSONL  : {CORP_JSONL}")',
    'print(f"  PHASE_L_CSV : {PHASE_L_CSV}")',
    'print(f"  OUTPUT_DIR  : {OUTPUT_DIR}")',
    'print(f"  N_CLUSTERS={N_CLUSTERS}  TOP_PATH_N={TOP_PATH_N}")',
])

SRC_MD_A = "\n".join([
    "---",
    "## 子任務 A：載入法人標籤 → 特徵矩陣",
    "",
    "從 `company_labels.jsonl` 解析 8 大類標籤，轉換成數值特徵：",
    "- **布林欄位**（外商/家族企業/集團）→ 0/1",
    "- **列表欄位**（競爭者/關注議題等）→ 元素個數",
    "- **文字欄位**（商業模式/員工人數）→ 分類編碼",
])

SRC_A1 = "\n".join([
    "# ── A1：解析 company_labels.jsonl ─────────────────────",
    "",
    "def _bool(v) -> int:",
    "    if v is True:  return 1",
    "    if v is False: return 0",
    "    return 0",
    "",
    "def _cnt(v) -> int:",
    '    """list → 元素數；str → 1；None → 0"""',
    "    if isinstance(v, list): return len(v)",
    "    if isinstance(v, str) and v.strip(): return 1",
    "    return 0",
    "",
    "def _biz(v) -> int:",
    '    """商業模式：B2B=2, B2C=1, B2B2C/混合=2, 其他=0"""',
    "    if not isinstance(v, str): return 0",
    '    v = v.upper()',
    '    if "B2B" in v: return 2',
    '    if "B2C" in v: return 1',
    "    return 0",
    "",
    "def _headcount(v) -> int:",
    '    """員工人數 → 數值"""',
    "    if not isinstance(v, str): return 0",
    "    m = re.search(r'\\d+', v)",
    "    return int(m.group()) if m else 0",
    "",
    "records = []",
    "with open(CORP_JSONL, encoding='utf-8') as f:",
    "    for line in f:",
    "        if not line.strip(): continue",
    "        r = json.loads(line)",
    "        lb = r.get('labels', {})",
    "        cid = r.get('company_id', '')",
    "",
    "        basic   = lb.get('基本資料', {})",
    "        contact = lb.get('聯絡人', {})",
    "        trade   = lb.get('進出口資訊', {})",
    "        sales   = lb.get('銷售資訊', {})",
    "        group   = lb.get('集團資訊', {})",
    "        pref    = lb.get('偏好及總結', {})",
    "        ind     = lb.get('產業', {})",
    "        chain   = lb.get('產業鏈', {})",
    "",
    "        records.append({",
    "            'company_id':     cid,",
    "            'f_foreign':      _bool(basic.get('外商')),",
    "            'f_family':       _bool(basic.get('家族企業')),",
    "            'f_biz_model':    _biz(basic.get('商業模式')),",
    "            'f_headcount':    _headcount(basic.get('員工人數')),",
    "            'f_n_decision':   _cnt(contact.get('決策者')),",
    "            'f_n_family_mbr': _cnt(contact.get('家族企業人員')),",
    "            'f_n_trade_ctry': _cnt(trade.get('國家')),",
    "            'f_n_competitor': _cnt(sales.get('競爭者')),",
    "            'f_group':        _bool(group.get('集團')),",
    "            'f_n_subsidiary': _cnt(group.get('分公司')),",
    "            'f_n_brand':      _cnt(group.get('品牌名稱')),",
    "            'f_n_issues':     _cnt(pref.get('關注議題')),",
    "            'f_industry_ldr': 1 if ind.get('產業龍頭') else 0,",
    "            'f_n_customer':   _cnt(chain.get('法人的客戶')),",
    "            'f_n_supplier':   _cnt(chain.get('法人的供應商')),",
    "        })",
    "",
    "corp_df = pd.DataFrame(records)",
    "print(f'公司數：{len(corp_df):,} 家')",
    "print(f'特徵欄位數：{len([c for c in corp_df.columns if c.startswith(\"f_\")]) }')",
    "corp_df.head(3)",
])

SRC_A2 = "\n".join([
    "# ── A2：載入 phase_l_final.csv (L 層事件) ─────────────",
    "phase_df = pd.read_csv(PHASE_L_CSV, encoding='utf-8-sig',",
    "                       usecols=['event_id','company_id','ym','l_layer','source'])",
    "phase_df['ym'] = phase_df['ym'].astype(str)",
    "",
    "n_company = phase_df['company_id'].nunique()",
    "print(f'phase_l_final：{len(phase_df):,} 筆  /  {n_company:,} 家公司')",
    "print(phase_df['l_layer'].value_counts().to_string())",
])

SRC_MD_B = "\n".join([
    "---",
    "## 子任務 B：聚類 + PCA Map",
    "",
    "1. StandardScaler 標準化特徵矩陣",
    "2. KMeans（k=N_CLUSTERS）分群",
    "3. PCA(n_components=2) 降維 → 2D 座標",
])

SRC_B1 = "\n".join([
    "# ── B1：特徵矩陣標準化 ─────────────────────────────────",
    "FEAT_COLS = [c for c in corp_df.columns if c.startswith('f_')]",
    "X = corp_df[FEAT_COLS].fillna(0).values.astype(float)",
    "",
    "scaler = StandardScaler()",
    "X_scaled = scaler.fit_transform(X)",
    "",
    "print(f'特徵矩陣：{X_scaled.shape}  (公司數 × 特徵數)')",
    "print('特徵欄：', FEAT_COLS)",
])

SRC_B2 = "\n".join([
    "# ── B2：KMeans 聚類 ─────────────────────────────────────",
    "km = KMeans(n_clusters=N_CLUSTERS, random_state=RANDOM_STATE, n_init=20)",
    "labels = km.fit_predict(X_scaled)",
    "corp_df['cluster'] = labels",
    "",
    "print(f'KMeans 完成  k={N_CLUSTERS}')",
    "print('各群人數：')",
    "print(corp_df['cluster'].value_counts().sort_index().to_string())",
])

SRC_B3 = "\n".join([
    "# ── B3：PCA 降維 → 2D Map 座標 ──────────────────────────",
    "pca = PCA(n_components=2, random_state=RANDOM_STATE)",
    "coords = pca.fit_transform(X_scaled)",
    "corp_df['pca_x'] = coords[:, 0]",
    "corp_df['pca_y'] = coords[:, 1]",
    "",
    "print(f'PCA 完成  解釋變異：{pca.explained_variance_ratio_.sum():.1%}')",
    "print(f'PC1={pca.explained_variance_ratio_[0]:.1%}  PC2={pca.explained_variance_ratio_[1]:.1%}')",
    "",
    "# 各群重心",
    "centroids = corp_df.groupby('cluster')[['pca_x','pca_y']].mean()",
    "print('\\n各群 PCA 重心：')",
    "print(centroids.round(3).to_string())",
])

SRC_MD_C = "\n".join([
    "---",
    "## 子任務 C：熱路徑分析",
    "",
    "依公司 ID 將 `phase_l_final.csv` 的事件按年月排序，",
    "提取每家公司的 L 層時序字串（如 `L1→L3→L5`），",
    "統計出現頻率最高的路徑 Top-N。",
])

SRC_C1 = "\n".join([
    "# ── C1：產生公司 L 層時序路徑 ─────────────────────────",
    "# 每家公司：按 ym 排序 → 取不重複相鄰層序列（壓縮連續相同層）",
    "",
    "def compress_path(layers):",
    '    """去除連續重複：[L1,L1,L3,L3,L5] → [L1,L3,L5]"""',
    "    out = []",
    "    for l in layers:",
    "        if not out or l != out[-1]:",
    "            out.append(l)",
    "    return out",
    "",
    "grp = phase_df.sort_values(['company_id','ym']).groupby('company_id')",
    "",
    "path_counter = Counter()",
    "company_paths = {}",
    "",
    "for cid, gdf in tqdm(grp, desc='熱路徑', total=grp.ngroups):",
    "    layers = gdf['l_layer'].tolist()",
    "    path   = compress_path(layers)",
    "    if len(path) >= MIN_PATH_LEN:",
    "        path_str = '→'.join(path)",
    "        path_counter[path_str] += 1",
    "        company_paths[cid] = path_str",
    "",
    "print(f'有效公司路徑：{len(company_paths):,} 家')",
    "print(f'不同路徑種類：{len(path_counter):,} 種')",
])

SRC_C2 = "\n".join([
    "# ── C2：Top-N 熱路徑統計 ───────────────────────────────",
    "top_paths = path_counter.most_common(TOP_PATH_N)",
    "path_df = pd.DataFrame(top_paths, columns=['path','count'])",
    "path_df['pct'] = (path_df['count'] / len(company_paths) * 100).round(2)",
    "path_df['n_steps'] = path_df['path'].str.count('→') + 1",
    "",
    "print(f'Top-{TOP_PATH_N} 熱路徑（共 {len(company_paths):,} 家）：')",
    "print(path_df.to_string(index=False))",
])

SRC_MD_E = "\n".join([
    "---",
    "## 子任務 E：統計報告 & 輸出",
])

SRC_E1 = "\n".join([
    "# ── E1：各群特徵側寫報告 ─────────────────────────────",
    "print('=' * 60)",
    "print(f'Phase M 聚類報告  k={N_CLUSTERS}')",
    "print('=' * 60)",
    "",
    "for cid in sorted(corp_df['cluster'].unique()):",
    "    sub = corp_df[corp_df['cluster'] == cid]",
    "    n   = len(sub)",
    "    print(f'\\n── Cluster {cid}（{n} 家）─────────────────────────')",
    "    for col in FEAT_COLS:",
    "        mean = sub[col].mean()",
    "        if mean > 0.05:",
    "            print(f'   {col:<20s} {mean:.2f}')",
    "",
    "print()",
    "# 熱路徑 × 聚類分析",
    "corp_df['path'] = corp_df['company_id'].astype(str).map(company_paths)",
    "has_path = corp_df.dropna(subset=['path'])",
    "print(f'\\n法人標籤 × 熱路徑 交集：{len(has_path):,} 家')",
])

SRC_E2 = "\n".join([
    "# ── E2：輸出 CSV ──────────────────────────────────────",
    "# 1) company_clusters.csv",
    "CLUSTER_CSV = OUTPUT_DIR / 'company_clusters.csv'",
    "out_cols = ['company_id','cluster','pca_x','pca_y'] + FEAT_COLS + ['path']",
    "corp_df[out_cols].to_csv(CLUSTER_CSV, index=False, encoding='utf-8-sig')",
    "print(f'✅ company_clusters.csv → {CLUSTER_CSV}  ({len(corp_df):,} 行)')",
    "",
    "# 2) cluster_profiles.csv  (各群平均特徵)",
    "PROFILE_CSV = OUTPUT_DIR / 'cluster_profiles.csv'",
    "profiles = corp_df.groupby('cluster')[FEAT_COLS].mean().round(3)",
    "profiles.to_csv(PROFILE_CSV, encoding='utf-8-sig')",
    "print(f'✅ cluster_profiles.csv → {PROFILE_CSV}  ({len(profiles)} 群)')",
    "",
    "# 3) hotpaths.csv",
    "HOTPATH_CSV = OUTPUT_DIR / 'hotpaths.csv'",
    "path_df.to_csv(HOTPATH_CSV, index=False, encoding='utf-8-sig')",
    "print(f'✅ hotpaths.csv → {HOTPATH_CSV}  ({len(path_df):,} 條路徑)')",
    "",
    "print()",
    "print('Phase M 完成！')",
    "print(f'  輸出目錄：{OUTPUT_DIR}')",
])

# ── 組裝 Notebook ─────────────────────────────────────────────────────────────
cells = [
    mc("md-title", SRC_TITLE),
    mc("md-s0",    "## 0. 安裝套件"),
    cc("code-s0",  SRC_S0),
    mc("md-s1",    "## 1. 匯入套件 & 全域設定"),
    cc("code-s1",  SRC_S1),
    mc("md-a",     SRC_MD_A),
    cc("code-a1",  SRC_A1),
    cc("code-a2",  SRC_A2),
    mc("md-b",     SRC_MD_B),
    cc("code-b1",  SRC_B1),
    cc("code-b2",  SRC_B2),
    cc("code-b3",  SRC_B3),
    mc("md-c",     SRC_MD_C),
    cc("code-c1",  SRC_C1),
    cc("code-c2",  SRC_C2),
    mc("md-e",     SRC_MD_E),
    cc("code-e1",  SRC_E1),
    cc("code-e2",  SRC_E2),
]

nb = {
    "nbformat": 4,
    "nbformat_minor": 5,
    "metadata": {
        "kernelspec": {"display_name": "Python 3","language": "python","name": "python3"},
        "language_info": {"name": "python","version": "3.11.0"},
    },
    "cells": cells,
}

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

print(f"OK → {OUT}")
print(f"Cells: {len(cells)}")

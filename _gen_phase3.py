# -*- coding: utf-8 -*-
"""
生成 L-Phase3痛需熱圖.ipynb
Phase 3 = Phase 2（L1–L7深度標籤）× 商機等級（E/D/C2/C1/B/A）× PhaseM（聚類）
輸出：痛需熱圖 + 三輸出（推薦問項 / 開發方案卡 / 機會卡）
"""
import json, pathlib

CELLS = []

def md(src):
    CELLS.append({"cell_type": "markdown", "metadata": {}, "source": src})

def code(src):
    CELLS.append({"cell_type": "code", "execution_count": None,
                  "metadata": {}, "outputs": [], "source": src})

# ═══════════════════════════════════════════════════════════════════
md("""# Phase 3：痛需熱圖 + 三輸出

**輸入三路合流：**
| 來源 | 檔案 | 說明 |
|------|------|------|
| Phase 2 | `results/phase2/phase2_deep_labels.jsonl` | L1–L7 深度標籤 |
| 商機等級 | `D:\\yujui\\痛點需求地圖\\lead_stage_results.csv` | E/D/C2/C1/B/A 銷售階段 |
| Phase M | `results/phaseM/company_clusters.csv` | 法人聚類 C0–C6 |
| Phase 1 | `results/phase1/company_labels_flat.csv` | 法人 8 大屬性 |

**輸出：**
1. `results/phase3/pain_heatmap.csv` — 痛需熱圖核心表
2. `results/phase3/output1_recommended_questions.csv` — 推薦業務問項
3. `results/phase3/output2_development_cards.csv` — 推薦開發方案卡
4. `results/phase3/output3_opportunity_cards.csv` — 機會卡（B+A 高溫標的）

**Schema 設計：**
```
company_dim   = company_id + cluster + stage_heat + 法人屬性
pain_records  = company_id + pain_type + impact + urgency（L1 非 null 明細）
layer_coverage= company_id + has_L1~L7（Boolean 覆蓋旗標）
pain_heatmap  = cluster × pain_type → company_count / ba_ratio / heat_score
```
""")

# ─── S1 匯入 ─────────────────────────────────────────────────────
md("## S1：匯入套件")
code("""\
import json
import pathlib
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import warnings
warnings.filterwarnings("ignore")

# CJK 字型
try:
    fm.fontManager.addfont(r"C:\\Windows\\Fonts\\msjh.ttc")
    matplotlib.rcParams["font.family"] = "Microsoft JhengHei"
except Exception:
    pass

BASE = pathlib.Path(r"d:\\yujui\\痛點需求地圖\\prompt定版")
OUT  = BASE / "results" / "phase3"
OUT.mkdir(parents=True, exist_ok=True)
print("✅ 套件載入完成")
print(f"   輸出目錄：{OUT}")
""")

# ─── S2 載入資料 ─────────────────────────────────────────────────
md("## S2：載入四路資料")
code("""\
# ── Phase M：聚類 ─────────────────────────────────────────────────
clusters_df = pd.read_csv(BASE / "results/phaseM/company_clusters.csv", dtype=str)
clusters_df.columns = clusters_df.columns.str.strip()
# 欄位可能是 company_id / cluster
if "cluster" not in clusters_df.columns:
    clusters_df.columns = ["company_id", "cluster"]
clusters_df["cluster"] = clusters_df["cluster"].astype(int)

CLUSTER_NAMES = {
    0: "C0 微型內銷", 1: "C1 標準內銷", 2: "C2 大型外商",
    3: "C3 多面型強者", 4: "C4 品牌驅動", 5: "C5 家族外銷", 6: "C6 外資貿易"
}
clusters_df["cluster_name"] = clusters_df["cluster"].map(CLUSTER_NAMES)
print(f"PhaseM clusters：{len(clusters_df):,} 家")

# ── Phase 1：法人屬性 ──────────────────────────────────────────────
labels_df = pd.read_csv(BASE / "results/phase1/company_labels_flat.csv", dtype=str)
labels_df.columns = labels_df.columns.str.strip()
# 確保 company_id 存在
cid_col = [c for c in labels_df.columns if "company" in c.lower() or c == "GY001"]
if cid_col:
    labels_df = labels_df.rename(columns={cid_col[0]: "company_id"})
print(f"Phase 1 法人屬性：{len(labels_df):,} 家")

# ── 商機等級 ───────────────────────────────────────────────────────
STAGE_FILE = pathlib.Path(r"D:\\yujui\\痛點需求地圖\\lead_stage_results.csv")
if STAGE_FILE.exists():
    stage_df = pd.read_csv(STAGE_FILE, encoding="utf-8-sig", dtype=str)
    stage_df = stage_df.rename(columns={"LD005": "company_id"})
    # 每家公司取最高商機階段
    STAGE_ORDER = {"A": 6, "B": 5, "C1": 4, "C2": 3, "D": 2, "E": 1, "none": 0}
    stage_df["stage_val"] = stage_df["top_stage"].map(STAGE_ORDER).fillna(0).astype(int)
    stage_agg = (stage_df.sort_values("stage_val", ascending=False)
                 .groupby("company_id", as_index=False)
                 .first()[["company_id", "top_stage", "stage_val"]]
                 .rename(columns={"stage_val": "stage_heat", "top_stage": "best_stage"}))
    print(f"商機等級：{len(stage_agg):,} 家（best_stage 分布↓）")
    print(stage_agg["best_stage"].value_counts().to_string())
else:
    print("⚠️  lead_stage_results.csv 尚未產生，以空表代替（商機等級跑完後重執行）")
    stage_agg = pd.DataFrame(columns=["company_id", "best_stage", "stage_heat"])

# ── Phase 2：深度標籤 ──────────────────────────────────────────────
P2_FILE = BASE / "results/phase2/phase2_deep_labels.jsonl"
raw_records = []
with open(P2_FILE, encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        try:
            raw_records.append(json.loads(line))
        except Exception:
            pass
print(f"\\nPhase 2 原始筆數：{len(raw_records):,}")
""")

# ─── A1 公司維度表 ────────────────────────────────────────────────
md("## A1：建立公司維度表 (company_dim)")
code("""\
# JOIN：cluster + stage + 法人屬性
company_dim = clusters_df[["company_id", "cluster", "cluster_name"]].copy()

# 商機等級
company_dim = company_dim.merge(stage_agg[["company_id", "best_stage", "stage_heat"]],
                                 on="company_id", how="left")
company_dim["best_stage"] = company_dim["best_stage"].fillna("none")
company_dim["stage_heat"]  = company_dim["stage_heat"].fillna(0).astype(int)

# 法人屬性（取常用欄位）
attr_cols = ["company_id"] + [c for c in labels_df.columns
             if c.startswith("f_") or c in ["f_foreign","f_family","f_biz_model","f_headcount"]]
attr_cols = list(dict.fromkeys(attr_cols))  # 去重
if len(attr_cols) > 1:
    company_dim = company_dim.merge(labels_df[attr_cols], on="company_id", how="left")

print(f"company_dim：{len(company_dim):,} 家 × {len(company_dim.columns)} 欄")
print(company_dim.dtypes.to_string())
company_dim.to_csv(OUT / "company_dim.csv", index=False, encoding="utf-8-sig")
print("✅ company_dim.csv 已存")
""")

# ─── A2 L1 痛點明細表 ─────────────────────────────────────────────
md("## A2：解析 L1 痛點明細 (pain_records)")
code("""\
pain_rows = []
layer_rows = []

for rec in raw_records:
    cid = rec.get("company_id", "")
    labels = rec.get("labels", {})
    if not labels or "_error" in str(labels):
        continue

    # Layer coverage flags
    layer_row = {"company_id": cid}
    for L in ["L1","L2","L3","L4","L5","L6","L7"]:
        layer_data = labels.get(L, {})
        has = layer_data and any(v is not None for v in layer_data.values()) if layer_data else False
        layer_row[f"has_{L}"] = has
    layer_rows.append(layer_row)

    # L1 痛點明細
    l1 = labels.get("L1", {})
    if l1 and l1.get("pain_type") is not None:
        pain_rows.append({
            "company_id": cid,
            "pain_type": str(l1.get("pain_type", "")).strip(),
            "impact":    str(l1.get("impact",    "")).strip(),
            "urgency":   str(l1.get("urgency",   "")).strip(),
        })

pain_df   = pd.DataFrame(pain_rows).drop_duplicates()
layer_cov = pd.DataFrame(layer_rows).drop_duplicates("company_id")

# 過濾空字串
pain_df = pain_df[pain_df["pain_type"].str.len() > 0].copy()

print(f"pain_records（L1 非 null）：{len(pain_df):,} 筆 / {pain_df['company_id'].nunique():,} 家")
print(f"layer_coverage：{len(layer_cov):,} 家")
print("\\n衝擊程度分布："); print(pain_df["impact"].value_counts().to_string())
print("\\n緊迫度分布：");   print(pain_df["urgency"].value_counts().to_string())

pain_df.to_csv(OUT / "pain_records.csv",    index=False, encoding="utf-8-sig")
layer_cov.to_csv(OUT / "layer_coverage.csv", index=False, encoding="utf-8-sig")
print("\\n✅ pain_records.csv / layer_coverage.csv 已存")
""")

# ─── B1 JOIN 合併 ─────────────────────────────────────────────────
md("## B1：JOIN 合併核心分析表")
code("""\
# pain_records + company_dim → 帶 cluster + stage_heat
pain_full = pain_df.merge(company_dim[["company_id","cluster","cluster_name",
                                        "best_stage","stage_heat"]],
                           on="company_id", how="left")

# 商機熱度旗標
pain_full["is_BA"] = pain_full["best_stage"].isin(["A","B"])
pain_full["urgency_high"] = pain_full["urgency"].str.contains("急迫", na=False)

print(f"pain_full：{len(pain_full):,} 筆")
print(f"B+A 比例：{pain_full['is_BA'].mean():.1%}")
pain_full.head(5)
""")

# ─── B2 痛需熱圖聚合 ───────────────────────────────────────────────
md("## B2：痛需熱圖聚合 (pain_heatmap)")
code("""\
# 每個 (cluster, pain_type) 組合的指標
grp = pain_full.groupby(["cluster","cluster_name","pain_type"])

heatmap = grp.agg(
    company_count   = ("company_id", "nunique"),
    ba_count        = ("is_BA",       "sum"),
    urgency_hi_count= ("urgency_high","sum"),
    avg_stage_heat  = ("stage_heat",  "mean"),
).reset_index()

# 總公司數（for 規模分數）
total_company = pain_full["company_id"].nunique()

heatmap["ba_ratio"]         = heatmap["ba_count"] / heatmap["company_count"]
heatmap["urgency_high_pct"] = heatmap["urgency_hi_count"] / heatmap["company_count"]
heatmap["scale_score"]      = np.log1p(heatmap["company_count"]) / np.log1p(total_company)

# ── 熱度公式 ──────────────────────────────────────────────────────
# heat_score = ba_ratio × 0.5 + urgency_high_pct × 0.3 + scale_score × 0.2
heatmap["heat_score"] = (
    heatmap["ba_ratio"]        * 0.5 +
    heatmap["urgency_high_pct"]* 0.3 +
    heatmap["scale_score"]     * 0.2
)
heatmap = heatmap.sort_values("heat_score", ascending=False).reset_index(drop=True)

print(f"痛需熱圖：{len(heatmap):,} 個 cluster × pain_type 組合")
print("\\nTop 15 最熱痛點組合：")
print(heatmap[["cluster_name","pain_type","company_count","ba_ratio",
               "urgency_high_pct","heat_score"]].head(15).to_string(index=False))

heatmap.to_csv(OUT / "pain_heatmap.csv", index=False, encoding="utf-8-sig")
print("\\n✅ pain_heatmap.csv 已存")
""")

# ─── C1 視覺化 ────────────────────────────────────────────────────
md("## C1：視覺化痛需熱圖")
code("""\
# 取 Top-N pain_type × 7 clusters 做熱圖
N_PAIN = 15   # 顯示最熱的 N 種痛點類型

top_pains = (heatmap.groupby("pain_type")["heat_score"]
             .max().nlargest(N_PAIN).index.tolist())

pivot = (heatmap[heatmap["pain_type"].isin(top_pains)]
         .pivot_table(index="pain_type", columns="cluster_name",
                      values="heat_score", aggfunc="max", fill_value=0))

# 確保欄位順序
col_order = [v for k, v in sorted(CLUSTER_NAMES.items()) if v in pivot.columns]
pivot = pivot[col_order]

fig, ax = plt.subplots(figsize=(14, 8))
im = ax.imshow(pivot.values, cmap="YlOrRd", aspect="auto", vmin=0, vmax=1)
plt.colorbar(im, ax=ax, label="heat_score")

ax.set_xticks(range(len(pivot.columns)))
ax.set_xticklabels(pivot.columns, rotation=30, ha="right", fontsize=10)
ax.set_yticks(range(len(pivot.index)))
ax.set_yticklabels(pivot.index, fontsize=10)

# 標注數值
for i in range(len(pivot.index)):
    for j in range(len(pivot.columns)):
        val = pivot.values[i, j]
        if val > 0:
            ax.text(j, i, f"{val:.2f}", ha="center", va="center",
                    fontsize=8, color="black" if val < 0.6 else "white")

ax.set_title("痛需熱圖：法人類型 × L1 痛點類型（顏色=heat_score）", fontsize=14, pad=15)
plt.tight_layout()
plt.savefig(OUT / "pain_heatmap.png", dpi=150, bbox_inches="tight")
plt.show()
print("✅ pain_heatmap.png 已存")
""")

# ─── D1 輸出 1：推薦問項 ──────────────────────────────────────────
md("""\
## D1：輸出 1 — 推薦業務問項

**邏輯：** 有 L1 痛點（確認問題存在）但 L4/L5 空白（議題/評估未深入），且商機溫度 ≥ C2 的公司
→ 業務還沒問到「是什麼議題驅動的」、「在評估哪些方案」，值得主動補問。
""")
code("""\
# 有 L1 且 (L4 或 L5) 空白 且商機溫度 >= C2(3)
q_base = layer_cov.merge(company_dim[["company_id","cluster","cluster_name",
                                       "best_stage","stage_heat"]], on="company_id", how="left")

rec_q = q_base[
    q_base["has_L1"] &
    (~q_base["has_L4"] | ~q_base["has_L5"]) &
    (q_base["stage_heat"] >= 3)   # C2 以上
].copy()

rec_q["missing_layers"] = rec_q.apply(
    lambda r: "/".join([L for L in ["L4","L5","L6"]
                        if not r.get(f"has_{L}", True)]), axis=1
)

# 推薦問項（按缺失層映射）
QUESTION_MAP = {
    "L4": "請問目前有哪些外部環境或法規壓力影響您的決策方向？",
    "L5": "您目前在評估哪些解決方案或供應商？決策的主要標準是什麼？",
    "L6": "您對現有方向的態度與溫度如何？有什麼近期的觸發事件嗎？",
}
rec_q["recommended_question"] = rec_q["missing_layers"].apply(
    lambda s: " / ".join([QUESTION_MAP.get(L, "") for L in s.split("/") if L])
)

output1 = rec_q[["company_id","cluster_name","best_stage","missing_layers","recommended_question"]]
print(f"推薦問項：{len(output1):,} 家")
print("\\n按法人類型分布：")
print(output1["cluster_name"].value_counts().to_string())

output1.to_csv(OUT / "output1_recommended_questions.csv", index=False, encoding="utf-8-sig")
print("\\n✅ output1_recommended_questions.csv 已存")
""")

# ─── D2 輸出 2：開發方案卡 ────────────────────────────────────────
md("""\
## D2：輸出 2 — 推薦開發方案卡

**邏輯：** `pain_heatmap` 中 `heat_score ≥ 0.5` 的組合
→ 需求明確 + 商機熱 + 規模夠 → 值得針對這個法人類型的痛點開發對應產品/功能。
""")
code("""\
HEAT_THRESHOLD = 0.5

output2 = heatmap[heatmap["heat_score"] >= HEAT_THRESHOLD].copy()
output2 = output2[["cluster_name","pain_type","company_count","ba_ratio",
                    "urgency_high_pct","avg_stage_heat","heat_score"]]

print(f"開發方案卡：{len(output2):,} 個高熱組合（heat_score ≥ {HEAT_THRESHOLD}）")
print()
print(output2.to_string(index=False))

output2.to_csv(OUT / "output2_development_cards.csv", index=False, encoding="utf-8-sig")
print("\\n✅ output2_development_cards.csv 已存")
""")

# ─── D3 輸出 3：機會卡 ────────────────────────────────────────────
md("""\
## D3：輸出 3 — 機會卡（B+A 高溫標的）

**邏輯：** `best_stage` 為 B 或 A 的公司 + 其 L1 痛點
→ 商機最熱、最近成交可能最高的公司清單，業務可立即跟進。
""")
code("""\
ba_companies = company_dim[company_dim["best_stage"].isin(["A","B"])].copy()

# 取出這些公司的 L1 痛點
ba_pain = ba_companies.merge(
    pain_df[["company_id","pain_type","impact","urgency"]],
    on="company_id", how="left"
)

output3 = ba_pain[["company_id","cluster_name","best_stage","stage_heat",
                    "pain_type","impact","urgency"]].sort_values(
    ["stage_heat","cluster"], ascending=[False, True]
)

print(f"機會卡（B+A 階段）：{len(ba_companies):,} 家")
print("\\n按法人類型：")
print(ba_companies["cluster_name"].value_counts().to_string())
print("\\n按商機階段：")
print(ba_companies["best_stage"].value_counts().to_string())

output3.to_csv(OUT / "output3_opportunity_cards.csv", index=False, encoding="utf-8-sig")
print("\\n✅ output3_opportunity_cards.csv 已存")
""")

# ─── E1 總覽報告 ─────────────────────────────────────────────────
md("## E1：總覽報告")
code("""\
print("=" * 60)
print("Phase 3 痛需熱圖 — 執行摘要")
print("=" * 60)
print(f"\\n輸入：")
print(f"  Phase 2 處理公司數：{layer_cov['company_id'].nunique():,}")
print(f"  有 L1 痛點的公司：  {pain_df['company_id'].nunique():,}")
print(f"  商機等級公司數：    {len(stage_agg):,}")
print(f"  PhaseM 聚類公司數：  {len(clusters_df):,}")

print(f"\\n痛需熱圖：")
print(f"  cluster × pain_type 組合：{len(heatmap):,}")
print(f"  heat_score ≥ 0.5 組合：   {len(output2):,}")

print(f"\\n三輸出：")
print(f"  Output 1 推薦問項：  {len(output1):,} 家")
print(f"  Output 2 開發方案卡：{len(output2):,} 個組合")
print(f"  Output 3 機會卡：    {len(ba_companies):,} 家（B+A）")

print(f"\\n輸出目錄：{OUT}")
print("=" * 60)
""")

# ═══════════════════════════════════════════════════════════════════
# 產生 notebook
NB = {
    "nbformat": 4, "nbformat_minor": 5,
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.10.0"}
    },
    "cells": CELLS
}

# 補 cell id
import uuid
for c in NB["cells"]:
    c["id"] = uuid.uuid4().hex[:8]
    if c["cell_type"] == "code":
        c["source"] = c["source"].strip()
    if isinstance(c["source"], str):
        c["source"] = c["source"]

OUT_NB = pathlib.Path(r"d:\yujui\痛點需求地圖\prompt定版\L-Phase3痛需熱圖.ipynb")
OUT_NB.write_text(json.dumps(NB, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"✅ {OUT_NB.name} 已生成（{len(CELLS)} 個 cell）")

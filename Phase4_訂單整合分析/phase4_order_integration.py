# Phase 4：訂單整合分析
# 整合訂單資料，驗證痛需熱圖，計算實際轉換率與產值

import os
import json
import pathlib
import pyodbc
import configparser
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings("ignore")

# ══════════════════════════════════════════════════════════════════
# S0：全域設定
# ══════════════════════════════════════════════════════════════════

# CJK 字型
try:
    fm.fontManager.addfont(r"C:\Windows\Fonts\msjh.ttc")
    plt.rcParams["font.family"] = "Microsoft JhengHei"
except Exception:
    pass

# 路徑設定
BASE = pathlib.Path(__file__).parent
ROOT = BASE.parent
OUT = BASE / "results"
OUT.mkdir(parents=True, exist_ok=True)

# SQL 連線設定
SQL_INI = r"D:\yujui\SqlServer18.txt"
cfg = configparser.ConfigParser()
cfg.read(SQL_INI, encoding="utf-8")
sec = cfg["mssql"]

CONN_STR = (
    f"DRIVER={{SQL Server}};SERVER={sec['server']};"
    f"DATABASE=DSC_CRM_SP;UID={sec['uid']};PWD={sec['pwd']}"
)

print("✅ Phase 4 訂單整合分析")
print(f"   輸出目錄：{OUT}")
print()

# ══════════════════════════════════════════════════════════════════
# S1：載入 Phase 1-3 資料
# ══════════════════════════════════════════════════════════════════

print("📂 載入 Phase 1-3 資料...")

# Phase M：聚類
clusters_df = pd.read_csv(
    ROOT / "PhaseM_聚類分析/results/company_clusters.csv",
    dtype={"company_id": str, "cluster": int}
)
# 只保留需要的欄位
clusters_df = clusters_df[["company_id", "cluster"]].copy()
print(f"   PhaseM 聚類：{len(clusters_df):,} 家")

# Phase 3：痛需熱圖
pain_heatmap = pd.read_csv(
    ROOT / "Phase3_痛需熱圖/results/pain_heatmap.csv"
)
print(f"   Phase3 熱圖：{len(pain_heatmap):,} 個痛點組合")

# Phase 3：痛點明細
pain_records = pd.read_csv(
    ROOT / "Phase3_痛需熱圖/results/pain_records.csv",
    dtype={"company_id": str}
)
print(f"   Phase3 痛點：{len(pain_records):,} 筆 / {pain_records['company_id'].nunique():,} 家")

# Phase 3：Output 3 機會卡
output3 = pd.read_csv(
    ROOT / "Phase3_痛需熱圖/results/output3_opportunity_cards.csv",
    dtype={"company_id": str}
)
print(f"   Phase3 機會卡：{len(output3):,} 家 (B+A)")

# 商機等級
stage_df = pd.read_csv(
    ROOT.parent / "lead_stage_results.csv",
    encoding="utf-8-sig",
    dtype=str,
    on_bad_lines='skip'
)
stage_df["LD005"] = stage_df["LD005"].str.zfill(10)
stage_df = stage_df.rename(columns={"LD005": "company_id"})
print(f"   商機等級：{len(stage_df):,} 筆 / {stage_df['company_id'].nunique():,} 家")

print()

# ══════════════════════════════════════════════════════════════════
# S2：載入訂單資料
# ══════════════════════════════════════════════════════════════════

print("💰 載入訂單資料...")

conn = pyodbc.connect(CONN_STR, autocommit=True)

# 查詢 2024-2026 訂單（有效潛客代號）
order_sql = """
SELECT
    HC015 as company_id,
    CREATE_DATE,
    MODI_DATE,
    HC018 as order_amount,
    HC021 as total_amount,
    HC043 as product_code,
    HC001 as order_type,
    HC002 as order_no
FROM DSC_CRM_SP.dbo.CRMHC
WHERE LEN(HC015) = 10
AND MODI_DATE >= '20240101'
AND HC018 IS NOT NULL
ORDER BY MODI_DATE DESC
"""

orders_df = pd.read_sql(order_sql, conn)
conn.close()

# 資料清理
orders_df["order_amount"] = pd.to_numeric(orders_df["order_amount"], errors="coerce")
orders_df["total_amount"] = pd.to_numeric(orders_df["total_amount"], errors="coerce")
orders_df["order_date"] = pd.to_datetime(orders_df["MODI_DATE"], format="%Y%m%d", errors="coerce")

print(f"   訂單筆數：{len(orders_df):,}")
print(f"   公司數：{orders_df['company_id'].nunique():,}")
print(f"   日期範圍：{orders_df['order_date'].min()} ~ {orders_df['order_date'].max()}")
print(f"   總金額：{orders_df['order_amount'].sum():,.0f} 元")
print()

# ══════════════════════════════════════════════════════════════════
# 分析 A：熱圖驗證
# ══════════════════════════════════════════════════════════════════

print("=" * 70)
print("📊 分析 A：熱圖驗證（heat_score vs 實際成交）")
print("=" * 70)

# A1：為每個痛點組合計算實際成交率
# 合併 痛點記錄 + 聚類 + 訂單
pain_with_cluster = pain_records.merge(
    clusters_df[["company_id", "cluster"]],
    on="company_id",
    how="left"
)

# 標記是否成交（2024-2026）
pain_with_cluster["has_order"] = pain_with_cluster["company_id"].isin(
    orders_df["company_id"]
)

# 聚合到 (cluster, pain_type) 層級
validation = pain_with_cluster.groupby(["cluster", "pain_type"]).agg(
    total_companies=("company_id", "nunique"),
    ordered_companies=("has_order", "sum"),
).reset_index()

validation["actual_conversion_rate"] = (
    validation["ordered_companies"] / validation["total_companies"]
)

# 合併熱圖的 heat_score
validation = validation.merge(
    pain_heatmap[["cluster", "pain_type", "heat_score"]],
    on=["cluster", "pain_type"],
    how="left"
)

# 計算相關係數
correlation = validation[["heat_score", "actual_conversion_rate"]].corr().iloc[0, 1]

print(f"\n✓ heat_score vs 實際成交率相關係數：{correlation:.3f}")
print(f"✓ 有效痛點組合數：{len(validation):,}")

# 儲存驗證結果
validation.sort_values("heat_score", ascending=False).to_csv(
    OUT / "A1_heat_score_validation.csv",
    index=False,
    encoding="utf-8-sig"
)
print(f"✓ 已儲存：A1_heat_score_validation.csv")

# A2：各聚類實際產值分析
cluster_revenue = pain_with_cluster.merge(
    orders_df[["company_id", "order_amount"]],
    on="company_id",
    how="left"
)

cluster_stats = cluster_revenue.groupby("cluster").agg(
    total_companies=("company_id", "nunique"),
    ordered_companies=("order_amount", lambda x: x.notna().sum()),
    total_revenue=("order_amount", "sum"),
    avg_order=("order_amount", "mean"),
).reset_index()

cluster_stats["conversion_rate"] = (
    cluster_stats["ordered_companies"] / cluster_stats["total_companies"]
)

print(f"\n各聚類產值分析：")
print(cluster_stats.to_string(index=False))

cluster_stats.to_csv(
    OUT / "A2_cluster_revenue.csv",
    index=False,
    encoding="utf-8-sig"
)
print(f"✓ 已儲存：A2_cluster_revenue.csv")

print()

# ══════════════════════════════════════════════════════════════════
# 分析 B：痛點價值分析
# ══════════════════════════════════════════════════════════════════

print("=" * 70)
print("💰 分析 B：痛點價值分析（pain_type → 成交率與產值）")
print("=" * 70)

# B1：痛點轉換率
pain_conversion = pain_records.merge(
    orders_df[["company_id", "order_amount"]],
    on="company_id",
    how="left"
)

pain_stats = pain_conversion.groupby("pain_type").agg(
    total_companies=("company_id", "nunique"),
    ordered_companies=("order_amount", lambda x: x.notna().sum()),
    total_revenue=("order_amount", "sum"),
    avg_order=("order_amount", "mean"),
    max_order=("order_amount", "max"),
).reset_index()

pain_stats["conversion_rate"] = (
    pain_stats["ordered_companies"] / pain_stats["total_companies"]
)

# 計算 ROI（產值 / 影響公司數）
pain_stats["roi_per_company"] = (
    pain_stats["total_revenue"] / pain_stats["total_companies"]
)

# 排序
pain_stats_sorted = pain_stats.sort_values("total_revenue", ascending=False)

print(f"\nTop 20 最高產值痛點：")
print(pain_stats_sorted.head(20)[
    ["pain_type", "total_companies", "conversion_rate", "total_revenue", "avg_order"]
].to_string(index=False))

pain_stats_sorted.to_csv(
    OUT / "B1_pain_conversion_rate.csv",
    index=False,
    encoding="utf-8-sig"
)
print(f"\n✓ 已儲存：B1_pain_conversion_rate.csv")

# B3：痛點 ROI 排名
pain_roi = pain_stats.sort_values("roi_per_company", ascending=False)

print(f"\nTop 20 最高 ROI 痛點：")
print(pain_roi.head(20)[
    ["pain_type", "total_companies", "conversion_rate", "roi_per_company"]
].to_string(index=False))

pain_roi.to_csv(
    OUT / "B3_pain_roi_ranking.csv",
    index=False,
    encoding="utf-8-sig"
)
print(f"✓ 已儲存：B3_pain_roi_ranking.csv")

print()

# ══════════════════════════════════════════════════════════════════
# 分析 C：商機週期分析
# ══════════════════════════════════════════════════════════════════

print("=" * 70)
print("⏱️  分析 C：商機週期分析（階段 → 成交時間）")
print("=" * 70)

# 合併商機階段 + 訂單
stage_with_order = stage_df[["company_id", "top_stage"]].merge(
    orders_df[["company_id", "order_date", "order_amount"]],
    on="company_id",
    how="inner"
)

# 按階段統計
stage_stats = stage_with_order.groupby("top_stage").agg(
    order_count=("company_id", "count"),
    total_revenue=("order_amount", "sum"),
    avg_revenue=("order_amount", "mean"),
).reset_index()

STAGE_ORDER = {"A": 1, "B": 2, "C1": 3, "C2": 4, "D": 5, "E": 6, "none": 7}
stage_stats["stage_rank"] = stage_stats["top_stage"].map(STAGE_ORDER)
stage_stats = stage_stats.sort_values("stage_rank")

print(f"\n各階段成交統計：")
print(stage_stats[["top_stage", "order_count", "total_revenue", "avg_revenue"]].to_string(index=False))

stage_stats.to_csv(
    OUT / "C1_stage_conversion.csv",
    index=False,
    encoding="utf-8-sig"
)
print(f"\n✓ 已儲存：C1_stage_conversion.csv")

print()

# ══════════════════════════════════════════════════════════════════
# 分析 D：預測特徵工程
# ══════════════════════════════════════════════════════════════════

print("=" * 70)
print("🎯 分析 D：預測特徵工程（準備建模）")
print("=" * 70)

# D1：建立完整特徵矩陣
# 合併所有維度
feature_base = clusters_df.copy()

# 加入痛點（每家公司取主要痛點）
main_pain = pain_records.groupby("company_id").first().reset_index()[
    ["company_id", "pain_type", "impact", "urgency"]
]
feature_base = feature_base.merge(main_pain, on="company_id", how="left")

# 加入商機階段
main_stage = stage_df.groupby("company_id").first().reset_index()[
    ["company_id", "top_stage"]
]
feature_base = feature_base.merge(main_stage, on="company_id", how="left")

# 加入訂單標記（目標變數）
order_companies = orders_df.groupby("company_id").agg(
    has_order=("order_amount", lambda x: 1),
    total_orders=("order_amount", "count"),
    total_revenue=("order_amount", "sum"),
    last_order_date=("order_date", "max"),
).reset_index()

feature_matrix = feature_base.merge(
    order_companies,
    on="company_id",
    how="left"
)

# 填充缺失值
feature_matrix["has_order"] = feature_matrix["has_order"].fillna(0).astype(int)
feature_matrix["total_orders"] = feature_matrix["total_orders"].fillna(0)
feature_matrix["total_revenue"] = feature_matrix["total_revenue"].fillna(0)

print(f"\n特徵矩陣：{len(feature_matrix):,} 家公司 × {len(feature_matrix.columns)} 個特徵")
print(f"目標變數（has_order）分布：")
print(feature_matrix["has_order"].value_counts())

feature_matrix.to_csv(
    OUT / "D1_feature_matrix.csv",
    index=False,
    encoding="utf-8-sig"
)
print(f"\n✓ 已儲存：D1_feature_matrix.csv")

# D2：特徵重要性（簡易版：計算各維度與成交的關聯）
print(f"\n特徵統計：")
print(f"  聚類特徵：{feature_matrix['cluster'].nunique()} 種")
print(f"  痛點類型：{feature_matrix['pain_type'].nunique()} 種")
print(f"  商機階段：{feature_matrix['top_stage'].nunique()} 種")
print(f"  成交公司：{feature_matrix['has_order'].sum():,} / {len(feature_matrix):,} ({feature_matrix['has_order'].mean():.1%})")

print()

# ══════════════════════════════════════════════════════════════════
# 總結報告
# ══════════════════════════════════════════════════════════════════

print("=" * 70)
print("📋 Phase 4 執行摘要")
print("=" * 70)

print(f"\n輸入資料：")
print(f"  Phase M 聚類：{len(clusters_df):,} 家")
print(f"  Phase 3 痛點：{pain_records['company_id'].nunique():,} 家")
print(f"  商機等級：{stage_df['company_id'].nunique():,} 家")
print(f"  訂單資料：{orders_df['company_id'].nunique():,} 家 / {len(orders_df):,} 筆")

print(f"\n分析輸出：")
print(f"  A. 熱圖驗證：相關係數 {correlation:.3f}")
print(f"  B. 痛點價值：{len(pain_stats):,} 種痛點分析")
print(f"  C. 商機週期：{len(stage_stats):,} 個階段統計")
print(f"  D. 特徵矩陣：{len(feature_matrix):,} 家公司")

print(f"\n關鍵洞察：")
print(f"  整體成交率：{feature_matrix['has_order'].mean():.1%}")
print(f"  平均訂單金額：{orders_df['order_amount'].mean():,.0f} 元")
print(f"  總產值（2024-2026）：{orders_df['order_amount'].sum():,.0f} 元")

print(f"\n輸出目錄：{OUT}")
print("=" * 70)

print("\n✅ Phase 4 分析完成！")

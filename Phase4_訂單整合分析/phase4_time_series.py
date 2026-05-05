# Phase 4：訂單整合分析（時間序列版）
# 使用「成交前最後一次商機評估」進行對應

import os
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

# CJK 字型
try:
    fm.fontManager.addfont(r"C:\Windows\Fonts\msjh.ttc")
    plt.rcParams["font.family"] = "Microsoft JhengHei"
except Exception:
    pass

# 路徑設定
BASE = pathlib.Path(__file__).parent
ROOT = BASE.parent
OUT = BASE / "results_timeseries"
OUT.mkdir(parents=True, exist_ok=True)

print("="*70)
print("Phase 4：訂單整合分析（時間序列版）")
print("="*70)
print(f"輸出目錄：{OUT}")
print()

# ══════════════════════════════════════════════════════════════════
# S1：載入基礎資料
# ══════════════════════════════════════════════════════════════════

print("載入 Phase 1-3 資料...")

# Phase M：聚類
clusters_df = pd.read_csv(
    ROOT / "PhaseM_聚類分析/results/company_clusters.csv",
    dtype={"company_id": str, "cluster": int}
)
clusters_df = clusters_df[["company_id", "cluster"]].copy()
print(f"   PhaseM 聚類：{len(clusters_df):,} 家")

# Phase 3：痛點明細
pain_records = pd.read_csv(
    ROOT / "Phase3_痛需熱圖/results/pain_records.csv",
    dtype={"company_id": str}
)
print(f"   Phase3 痛點：{len(pain_records):,} 筆 / {pain_records['company_id'].nunique():,} 家")

print()

# ══════════════════════════════════════════════════════════════════
# S2：載入訂單資料
# ══════════════════════════════════════════════════════════════════

print("載入訂單資料...")

SQL_INI = r"D:\yujui\SqlServer18.txt"
cfg = configparser.ConfigParser()
cfg.read(SQL_INI, encoding="utf-8")
sec = cfg["mssql"]

CONN_STR = (
    f"DRIVER={{SQL Server}};SERVER={sec['server']};"
    f"DATABASE=DSC_CRM_SP;UID={sec['uid']};PWD={sec['pwd']}"
)

conn = pyodbc.connect(CONN_STR, autocommit=True)

order_sql = """
SELECT
    HC015 as company_id,
    MODI_DATE,
    HC018 as order_amount,
    HC043 as product_code
FROM DSC_CRM_SP.dbo.CRMHC
WHERE LEN(HC015) = 10
AND MODI_DATE >= '20240101'
AND HC018 IS NOT NULL
ORDER BY MODI_DATE DESC
"""

orders_df = pd.read_sql(order_sql, conn)
conn.close()

orders_df["order_amount"] = pd.to_numeric(orders_df["order_amount"], errors="coerce")
orders_df["order_date"] = pd.to_datetime(orders_df["MODI_DATE"], format="%Y%m%d", errors="coerce")

print(f"   訂單筆數：{len(orders_df):,}")
print(f"   公司數：{orders_df['company_id'].nunique():,}")
print(f"   總金額：{orders_df['order_amount'].sum():,.0f} 元")
print()

# ══════════════════════════════════════════════════════════════════
# S3：載入商機階段（帶日期）
# ══════════════════════════════════════════════════════════════════

print("載入商機階段資料（帶日期）...")

stage_path = r"d:\yujui\痛點需求地圖\lead_stage_with_date.csv"
stage_df = pd.read_csv(stage_path, encoding='utf-8-sig')
stage_df['log_date'] = pd.to_datetime(stage_df['log_date'])

print(f"   商機日誌：{len(stage_df):,} 筆")
print(f"   涵蓋公司：{stage_df['company_id'].nunique():,} 家")
print(f"   日期範圍：{stage_df['log_date'].min()} ~ {stage_df['log_date'].max()}")
print()

# ══════════════════════════════════════════════════════════════════
# 核心邏輯：時間序列對應
# ══════════════════════════════════════════════════════════════════

print("="*70)
print("核心處理：為每筆訂單找「成交前最後一次商機評估」")
print("="*70)

# 合併訂單與商機日誌
merged = orders_df.merge(
    stage_df[['company_id', 'log_date', 'stage']],
    on='company_id',
    how='left'
)

print(f"\n初步合併：{len(merged):,} 筆（訂單 × 商機日誌）")

# 篩選：只保留「日誌日期 <= 訂單日期」的記錄
merged = merged[merged['log_date'] <= merged['order_date']].copy()

print(f"篩選後：{len(merged):,} 筆（只保留成交前的日誌）")

# 計算時間差（天數）
merged['days_before_order'] = (merged['order_date'] - merged['log_date']).dt.days

# 為每筆訂單找「最接近成交日期」的商機評估
# 方法：按 company_id + order_date 分組，取 days_before_order 最小的
matched_orders = merged.sort_values('days_before_order').groupby(
    ['company_id', 'MODI_DATE', 'order_amount', 'order_date']
).first().reset_index()

print(f"\n最終匹配：{len(matched_orders):,} 筆訂單")
print(f"匹配率：{len(matched_orders) / len(orders_df) * 100:.1f}%")

# 統計無法匹配的訂單
unmatched = len(orders_df) - len(matched_orders)
print(f"無法匹配：{unmatched:,} 筆（成交前無商機日誌記錄）")

print()

# ══════════════════════════════════════════════════════════════════
# 分析 C（更新版）：各階段成交統計
# ══════════════════════════════════════════════════════════════════

print("="*70)
print("分析 C：商機階段成交統計（時間序列版）")
print("="*70)

stage_stats = matched_orders.groupby('stage').agg(
    order_count=('company_id', 'count'),
    total_revenue=('order_amount', 'sum'),
    avg_revenue=('order_amount', 'mean'),
    avg_days_to_close=('days_before_order', 'mean'),
    median_days_to_close=('days_before_order', 'median'),
).reset_index()

STAGE_ORDER = {"A": 1, "B": 2, "C1": 3, "C2": 4, "D": 5, "E": 6}
stage_stats["stage_rank"] = stage_stats["stage"].map(STAGE_ORDER)
stage_stats = stage_stats.sort_values("stage_rank")

print("\n各階段成交統計：")
print(stage_stats[[
    'stage', 'order_count', 'total_revenue', 'avg_revenue',
    'avg_days_to_close', 'median_days_to_close'
]].to_string(index=False))

stage_stats.to_csv(
    OUT / "C1_stage_conversion_timeseries.csv",
    index=False,
    encoding="utf-8-sig"
)
print(f"\nOK 已儲存：C1_stage_conversion_timeseries.csv")

# ══════════════════════════════════════════════════════════════════
# 新分析：成交週期分析
# ══════════════════════════════════════════════════════════════════

print("\n" + "="*70)
print("分析 C2：成交週期分布")
print("="*70)

# 按天數區間分組
bins = [0, 7, 30, 90, 180, 365, 9999]
labels = ['<7天', '7-30天', '30-90天', '90-180天', '180-365天', '>365天']

matched_orders['cycle_group'] = pd.cut(
    matched_orders['days_before_order'],
    bins=bins,
    labels=labels
)

cycle_stats = matched_orders.groupby(['stage', 'cycle_group']).size().unstack(fill_value=0)

print("\n各階段成交週期分布（筆數）：")
print(cycle_stats)

cycle_stats.to_csv(
    OUT / "C2_cycle_distribution.csv",
    encoding="utf-8-sig"
)
print(f"\nOK 已儲存：C2_cycle_distribution.csv")

# ══════════════════════════════════════════════════════════════════
# 視覺化：成交週期 boxplot
# ══════════════════════════════════════════════════════════════════

print("\n" + "="*70)
print("生成視覺化圖表")
print("="*70)

# 過濾極端值（避免圖表失真）
plot_data = matched_orders[matched_orders['days_before_order'] <= 365].copy()

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# 左圖：各階段成交週期 boxplot
stage_order = ['E', 'D', 'C2', 'C1', 'B', 'A']
data_to_plot = [
    plot_data[plot_data['stage'] == s]['days_before_order'].values
    for s in stage_order if s in plot_data['stage'].unique()
]

ax1.boxplot(data_to_plot, labels=[s for s in stage_order if s in plot_data['stage'].unique()])
ax1.set_xlabel('商機階段', fontsize=12)
ax1.set_ylabel('評估 → 成交天數', fontsize=12)
ax1.set_title('各階段成交週期分布', fontsize=13, fontweight='bold')
ax1.grid(axis='y', alpha=0.3)

# 右圖：各階段訂單數與平均週期
x = np.arange(len(stage_stats))
ax2_1 = ax2
color1 = '#3498db'
ax2_1.bar(x, stage_stats['order_count'], color=color1, alpha=0.7, label='訂單數')
ax2_1.set_xlabel('商機階段', fontsize=12)
ax2_1.set_ylabel('訂單數', color=color1, fontsize=12)
ax2_1.tick_params(axis='y', labelcolor=color1)
ax2_1.set_xticks(x)
ax2_1.set_xticklabels(stage_stats['stage'])

ax2_2 = ax2_1.twinx()
color2 = '#e74c3c'
ax2_2.plot(x, stage_stats['avg_days_to_close'],
           marker='o', color=color2, linewidth=2, markersize=8, label='平均週期')
ax2_2.set_ylabel('平均成交週期（天）', color=color2, fontsize=12)
ax2_2.tick_params(axis='y', labelcolor=color2)

ax2.set_title('各階段訂單數與平均成交週期', fontsize=13, fontweight='bold')

plt.suptitle('商機階段成交週期分析（時間序列版）', fontsize=15, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig(OUT / "C_stage_cycle_analysis.png", dpi=150, bbox_inches="tight")
print(f"\nOK 已儲存圖表：C_stage_cycle_analysis.png")
plt.close()

# ══════════════════════════════════════════════════════════════════
# 總結報告
# ══════════════════════════════════════════════════════════════════

print("\n" + "="*70)
print("執行摘要")
print("="*70)

print(f"\n輸入資料：")
print(f"  訂單總數：{len(orders_df):,} 筆")
print(f"  商機日誌：{len(stage_df):,} 筆")

print(f"\n時間序列匹配：")
print(f"  成功匹配：{len(matched_orders):,} 筆 ({len(matched_orders)/len(orders_df)*100:.1f}%)")
print(f"  無法匹配：{unmatched:,} 筆")

print(f"\n關鍵發現：")
print(f"  平均成交週期：{matched_orders['days_before_order'].mean():.1f} 天")
print(f"  中位數週期：{matched_orders['days_before_order'].median():.1f} 天")
print(f"  最快成交：{matched_orders['days_before_order'].min():.0f} 天")
print(f"  最慢成交：{matched_orders['days_before_order'].max():.0f} 天")

print(f"\n各階段平均週期：")
for _, row in stage_stats.iterrows():
    print(f"  {row['stage']:4s}: {row['avg_days_to_close']:6.1f} 天 ({row['order_count']:,} 筆訂單)")

print(f"\n輸出目錄：{OUT}")
print("="*70)
print("\nOK Phase 4（時間序列版）分析完成！")

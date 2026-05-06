#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成 Phase 4 各個獨立視覺化圖表
從 results_timeseries/ 的 CSV 資料中提取，生成 6 張獨立圖片
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
from pathlib import Path

# 設定中文字體
matplotlib.rcParams['font.sans-serif'] = ['Microsoft JhengHei', 'SimHei']
matplotlib.rcParams['axes.unicode_minus'] = False

# 資料路徑
DATA_DIR = Path("results_timeseries")
OUTPUT_DIR = Path("results_timeseries/individual_charts")
OUTPUT_DIR.mkdir(exist_ok=True)

# 讀取資料
matched_orders = pd.read_csv(DATA_DIR / "matched_orders.csv")
cycle_dist = pd.read_csv(DATA_DIR / "C2_cycle_distribution.csv")

# 確保日期欄位格式正確
if 'order_date' in matched_orders.columns:
    matched_orders['order_date'] = pd.to_datetime(matched_orders['order_date'])
    matched_orders['order_month'] = matched_orders['order_date'].dt.to_period('M').astype(str)

print(f"載入訂單資料：{len(matched_orders)} 筆")
print(f"載入週期分布資料：{len(cycle_dist)} 筆")

# ============ Chart 1: 各階段成交週期分布（堆疊橫條圖）============
def generate_chart1():
    print("\n生成 Chart 1: 各階段成交週期分布...")

    # 計算各階段的週期分布百分比
    cycle_pct = cycle_dist.pivot_table(
        index='final_stage',
        columns='cycle_bin',
        values='order_count',
        fill_value=0
    )
    cycle_pct = cycle_pct.div(cycle_pct.sum(axis=1), axis=0) * 100

    # 按階段排序
    stage_order = ['A', 'B', 'C1', 'C2', 'D', 'E']
    cycle_pct = cycle_pct.reindex([s for s in stage_order if s in cycle_pct.index])

    fig, ax = plt.subplots(figsize=(12, 6))

    colors = ['#4CAF50', '#8BC34A', '#CDDC39', '#FFEB3B', '#FFC107', '#FF9800', '#FF5722']
    cycle_pct.plot(kind='barh', stacked=True, ax=ax, color=colors, width=0.7)

    ax.set_xlabel('百分比 (%)', fontsize=12)
    ax.set_ylabel('商機階段', fontsize=12)
    ax.set_title('各階段成交週期分布', fontsize=14, fontweight='bold')
    ax.legend(title='成交週期', bbox_to_anchor=(1.05, 1), loc='upper left')
    ax.grid(axis='x', alpha=0.3)

    # 添加百分比標籤
    for i, stage in enumerate(cycle_pct.index):
        cumsum = 0
        for col in cycle_pct.columns:
            val = cycle_pct.loc[stage, col]
            if val > 3:  # 只標記大於3%的區塊
                ax.text(cumsum + val/2, i, f'{val:.1f}%',
                       ha='center', va='center', fontsize=8,
                       color='white', fontweight='bold')
            cumsum += val

    plt.tight_layout()
    output_path = OUTPUT_DIR / "chart1_cycle_distribution.png"
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"✓ 已儲存: {output_path}")

# ============ Chart 2: 訂單數與平均週期（按月）============
def generate_chart2():
    print("\n生成 Chart 2: 訂單數與平均週期（按月）...")

    if 'order_month' not in matched_orders.columns:
        print("! 跳過 Chart 2: 缺少 order_month 欄位")
        return

    monthly = matched_orders.groupby('order_month').agg({
        'order_id': 'count',
        'days_before_order': 'mean'
    }).rename(columns={'order_id': 'order_count'})

    fig, ax1 = plt.subplots(figsize=(12, 6))

    color1 = '#2196F3'
    ax1.bar(range(len(monthly)), monthly['order_count'], color=color1, alpha=0.7, label='訂單數')
    ax1.set_xlabel('月份', fontsize=12)
    ax1.set_ylabel('訂單數', fontsize=12, color=color1)
    ax1.tick_params(axis='y', labelcolor=color1)
    ax1.set_xticks(range(len(monthly)))
    ax1.set_xticklabels(monthly.index, rotation=45, ha='right')

    ax2 = ax1.twinx()
    color2 = '#FF5722'
    ax2.plot(range(len(monthly)), monthly['days_before_order'],
             color=color2, marker='o', linewidth=2, label='平均週期')
    ax2.set_ylabel('平均成交週期（天）', fontsize=12, color=color2)
    ax2.tick_params(axis='y', labelcolor=color2)

    ax1.set_title('訂單數與平均週期（按月）', fontsize=14, fontweight='bold')
    ax1.legend(loc='upper left')
    ax2.legend(loc='upper right')
    ax1.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    output_path = OUTPUT_DIR / "chart2_monthly_trend.png"
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"✓ 已儲存: {output_path}")

# ============ Chart 3: 訂單金額 vs 成交週期（散佈圖）============
def generate_chart3():
    print("\n生成 Chart 3: 訂單金額 vs 成交週期...")

    # 客戶分群顏色
    customer_colors = {
        '新客戶 - 小客戶': '#3498db',
        '新客戶 - 大客戶': '#9b59b6',
        '老客戶 - 小客戶': '#2ecc71',
        '老客戶 - 大客戶': '#e74c3c',
    }

    fig, ax = plt.subplots(figsize=(12, 6))

    for segment, color in customer_colors.items():
        if 'customer_segment' in matched_orders.columns:
            segment_data = matched_orders[matched_orders['customer_segment'] == segment]
            if len(segment_data) > 0:
                ax.scatter(segment_data['order_amount'], segment_data['days_before_order'],
                          alpha=0.6, s=30, color=color, label=segment)

    # 添加趨勢線
    if len(matched_orders) > 0:
        x = matched_orders['order_amount'].values
        y = matched_orders['days_before_order'].values
        z = np.polyfit(x, y, 1)
        p = np.poly1d(z)
        ax.plot(x, p(x), "r--", alpha=0.5, linewidth=2)

        # 計算 R²
        residuals = y - p(x)
        ss_res = np.sum(residuals**2)
        ss_tot = np.sum((y - np.mean(y))**2)
        r_squared = 1 - (ss_res / ss_tot)
        ax.text(0.05, 0.95, f'R² = {r_squared:.3f}',
               transform=ax.transAxes, fontsize=10,
               verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    ax.set_xlabel('訂單金額（元）', fontsize=12)
    ax.set_ylabel('成交週期（天）', fontsize=12)
    ax.set_title('訂單金額 vs 成交週期', fontsize=14, fontweight='bold')
    ax.legend(loc='upper right')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    output_path = OUTPUT_DIR / "chart3_amount_vs_cycle.png"
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"✓ 已儲存: {output_path}")

# ============ Chart 4: 客戶分群分析 ============
def generate_chart4():
    print("\n生成 Chart 4: 客戶分群分析...")

    if 'customer_segment' not in matched_orders.columns:
        print("! 跳過 Chart 4: 缺少 customer_segment 欄位")
        return

    segment_stats = matched_orders.groupby('customer_segment').agg({
        'order_id': 'count',
        'order_amount': 'mean'
    }).rename(columns={'order_id': 'count', 'order_amount': 'avg_amount'})

    segment_order = ['新客戶 - 小客戶', '新客戶 - 大客戶', '老客戶 - 小客戶', '老客戶 - 大客戶']
    segment_stats = segment_stats.reindex([s for s in segment_order if s in segment_stats.index])

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    colors = ['#3498db', '#9b59b6', '#2ecc71', '#e74c3c']

    # 訂單數
    ax1.bar(range(len(segment_stats)), segment_stats['count'], color=colors)
    ax1.set_xlabel('客戶分群', fontsize=12)
    ax1.set_ylabel('訂單數', fontsize=12)
    ax1.set_title('各分群訂單數', fontsize=12, fontweight='bold')
    ax1.set_xticks(range(len(segment_stats)))
    ax1.set_xticklabels(segment_stats.index, rotation=15, ha='right')
    ax1.grid(axis='y', alpha=0.3)

    # 平均金額
    ax2.bar(range(len(segment_stats)), segment_stats['avg_amount'], color=colors)
    ax2.set_xlabel('客戶分群', fontsize=12)
    ax2.set_ylabel('平均訂單金額（元）', fontsize=12)
    ax2.set_title('各分群平均金額', fontsize=12, fontweight='bold')
    ax2.set_xticks(range(len(segment_stats)))
    ax2.set_xticklabels(segment_stats.index, rotation=15, ha='right')
    ax2.grid(axis='y', alpha=0.3)

    plt.suptitle('客戶分群分析', fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    output_path = OUTPUT_DIR / "chart4_customer_segments.png"
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"✓ 已儲存: {output_path}")

# ============ Chart 5: 各階段週期分布（箱型圖）============
def generate_chart5():
    print("\n生成 Chart 5: 各階段週期分布（箱型圖）...")

    if 'final_stage' not in matched_orders.columns:
        print("! 跳過 Chart 5: 缺少 final_stage 欄位")
        return

    stage_order = ['A', 'B', 'C1', 'C2', 'D', 'E']
    stage_data = [matched_orders[matched_orders['final_stage'] == s]['days_before_order'].values
                  for s in stage_order if s in matched_orders['final_stage'].values]
    stage_labels = [s for s in stage_order if s in matched_orders['final_stage'].values]

    fig, ax = plt.subplots(figsize=(12, 6))

    bp = ax.boxplot(stage_data, labels=stage_labels, patch_artist=True,
                    boxprops=dict(facecolor='#64B5F6', alpha=0.7),
                    medianprops=dict(color='#D32F2F', linewidth=2),
                    whiskerprops=dict(color='#424242'),
                    capprops=dict(color='#424242'))

    ax.set_xlabel('商機階段', fontsize=12)
    ax.set_ylabel('成交週期（天）', fontsize=12)
    ax.set_title('各階段週期分布（箱型圖）', fontsize=14, fontweight='bold')
    ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    output_path = OUTPUT_DIR / "chart5_cycle_boxplot.png"
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"✓ 已儲存: {output_path}")

# ============ Chart 6: 累積分布曲線（CDF）============
def generate_chart6():
    print("\n生成 Chart 6: 累積分布曲線（CDF）...")

    if 'final_stage' not in matched_orders.columns:
        print("! 跳過 Chart 6: 缺少 final_stage 欄位")
        return

    fig, ax = plt.subplots(figsize=(12, 6))

    stage_order = ['A', 'B', 'C1', 'C2', 'D', 'E']
    colors = ['#F44336', '#FF9800', '#FFC107', '#8BC34A', '#4CAF50', '#2196F3']

    for stage, color in zip(stage_order, colors):
        if stage in matched_orders['final_stage'].values:
            data = matched_orders[matched_orders['final_stage'] == stage]['days_before_order'].values
            data_sorted = np.sort(data)
            cdf = np.arange(1, len(data_sorted) + 1) / len(data_sorted)
            ax.plot(data_sorted, cdf * 100, label=f'{stage} 階段', linewidth=2, color=color)

    ax.set_xlabel('成交週期（天）', fontsize=12)
    ax.set_ylabel('累積百分比 (%)', fontsize=12)
    ax.set_title('累積分布曲線（CDF）', fontsize=14, fontweight='bold')
    ax.legend(loc='lower right')
    ax.grid(True, alpha=0.3)
    ax.set_xlim(left=0)
    ax.set_ylim([0, 100])

    plt.tight_layout()
    output_path = OUTPUT_DIR / "chart6_cdf.png"
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"✓ 已儲存: {output_path}")

# ============ 主程式 ============
if __name__ == "__main__":
    print("=" * 60)
    print("Phase 4 獨立圖表生成器")
    print("=" * 60)

    generate_chart1()
    generate_chart2()
    generate_chart3()
    generate_chart4()
    generate_chart5()
    generate_chart6()

    print("\n" + "=" * 60)
    print("✓ 所有圖表生成完成！")
    print(f"✓ 輸出目錄: {OUTPUT_DIR.absolute()}")
    print("=" * 60)

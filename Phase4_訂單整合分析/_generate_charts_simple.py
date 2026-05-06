#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
從 Phase4 notebook 的輸出資料生成 6 張獨立圖表
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

print("讀取資料...")
matched_orders = pd.read_csv(DATA_DIR / "matched_orders.csv")
cycle_dist_raw = pd.read_csv(DATA_DIR / "C2_cycle_distribution.csv")

# 準備資料
matched_orders['order_date'] = pd.to_datetime(matched_orders['order_date'])
matched_orders['order_month'] = matched_orders['order_date'].dt.to_period('M').astype(str)

# 客戶分群
matched_orders['order_sequence'] = matched_orders.groupby('company_id').cumcount() + 1
matched_orders['customer_type'] = matched_orders['order_sequence'].apply(
    lambda x: '新客戶' if x == 1 else '老客戶'
)
matched_orders['customer_size'] = matched_orders['order_amount'].apply(
    lambda x: '大客戶' if x >= 1000000 else '小客戶'
)
matched_orders['customer_segment'] = (
    matched_orders['customer_type'] + ' - ' +
    matched_orders['customer_size']
)

# 重命名 final_stage
matched_orders['final_stage'] = matched_orders['stage']

print(f"載入 {len(matched_orders)} 筆訂單資料")

# Chart 1: 週期分布堆疊橫條圖
def chart1():
    print("\n生成 Chart 1...")
    cycle_dist = cycle_dist_raw.set_index('stage')

    # 轉換為百分比
    cycle_pct = cycle_dist.div(cycle_dist.sum(axis=1), axis=0) * 100

    # 排序
    stage_order = ['A', 'B', 'C1', 'C2', 'D', 'E']
    cycle_pct = cycle_pct.reindex([s for s in stage_order if s in cycle_pct.index])

    fig, ax = plt.subplots(figsize=(14, 7))
    colors = ['#4CAF50', '#8BC34A', '#CDDC39', '#FFEB3B', '#FFC107', '#FF9800', '#FF5722']

    cycle_pct.plot(kind='barh', stacked=True, ax=ax, color=colors, width=0.7, edgecolor='white', linewidth=0.5)

    ax.set_xlabel('百分比 (%)', fontsize=14, fontweight='bold')
    ax.set_ylabel('商機階段', fontsize=14, fontweight='bold')
    ax.set_title('各階段成交週期分布', fontsize=16, fontweight='bold', pad=20)
    ax.legend(title='成交週期', bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=11)
    ax.grid(axis='x', alpha=0.3, linestyle='--')
    ax.set_xlim(0, 100)

    # 添加百分比標籤
    for i, stage in enumerate(cycle_pct.index):
        cumsum = 0
        for col in cycle_pct.columns:
            val = cycle_pct.loc[stage, col]
            if val > 3:
                ax.text(cumsum + val/2, i, f'{val:.1f}%',
                       ha='center', va='center', fontsize=9,
                       color='white', fontweight='bold')
            cumsum += val

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "chart1_cycle_distribution.png", dpi=200, bbox_inches='tight')
    plt.close()
    print("OK - Chart 1 完成")

# Chart 2: 月度趨勢
def chart2():
    print("\n生成 Chart 2...")
    monthly = matched_orders.groupby('order_month').agg({
        'company_id': 'count',
        'days_before_order': 'mean'
    }).rename(columns={'company_id': 'order_count'})

    fig, ax1 = plt.subplots(figsize=(14, 7))

    x = range(len(monthly))
    ax1.bar(x, monthly['order_count'], color='#2196F3', alpha=0.7, label='訂單數', width=0.6)
    ax1.set_xlabel('月份', fontsize=14, fontweight='bold')
    ax1.set_ylabel('訂單數', fontsize=14, fontweight='bold', color='#2196F3')
    ax1.tick_params(axis='y', labelcolor='#2196F3')
    ax1.set_xticks(x)
    ax1.set_xticklabels(monthly.index, rotation=45, ha='right', fontsize=10)
    ax1.grid(axis='y', alpha=0.3, linestyle='--')

    ax2 = ax1.twinx()
    ax2.plot(x, monthly['days_before_order'], color='#FF5722', marker='o',
             linewidth=3, markersize=8, label='平均週期')
    ax2.set_ylabel('平均成交週期（天）', fontsize=14, fontweight='bold', color='#FF5722')
    ax2.tick_params(axis='y', labelcolor='#FF5722')

    ax1.set_title('訂單數與平均週期趨勢（按月）', fontsize=16, fontweight='bold', pad=20)

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', fontsize=11)

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "chart2_monthly_trend.png", dpi=200, bbox_inches='tight')
    plt.close()
    print("OK - Chart 2 完成")

# Chart 3: 金額 vs 週期散佈圖
def chart3():
    print("\n生成 Chart 3...")
    customer_colors = {
        '新客戶 - 小客戶': '#3498db',
        '新客戶 - 大客戶': '#9b59b6',
        '老客戶 - 小客戶': '#2ecc71',
        '老客戶 - 大客戶': '#e74c3c',
    }

    fig, ax = plt.subplots(figsize=(14, 7))

    for segment, color in customer_colors.items():
        seg_data = matched_orders[matched_orders['customer_segment'] == segment]
        if len(seg_data) > 0:
            ax.scatter(seg_data['order_amount'], seg_data['days_before_order'],
                      alpha=0.6, s=50, color=color, label=segment, edgecolors='white', linewidth=0.5)

    # 趨勢線
    x = matched_orders['order_amount'].values
    y = matched_orders['days_before_order'].values
    valid = ~(np.isnan(x) | np.isnan(y))
    if np.sum(valid) > 1:
        z = np.polyfit(x[valid], y[valid], 1)
        p = np.poly1d(z)
        ax.plot(x[valid], p(x[valid]), "r--", alpha=0.5, linewidth=3, label='趨勢線')

        residuals = y[valid] - p(x[valid])
        ss_res = np.sum(residuals**2)
        ss_tot = np.sum((y[valid] - np.mean(y[valid]))**2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
        ax.text(0.05, 0.95, f'R² = {r_squared:.3f}',
               transform=ax.transAxes, fontsize=12, fontweight='bold',
               verticalalignment='top', bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))

    ax.set_xlabel('訂單金額（元）', fontsize=14, fontweight='bold')
    ax.set_ylabel('成交週期（天）', fontsize=14, fontweight='bold')
    ax.set_title('訂單金額 vs 成交週期（含客戶分群）', fontsize=16, fontweight='bold', pad=20)
    ax.legend(loc='upper right', fontsize=11, framealpha=0.9)
    ax.grid(True, alpha=0.3, linestyle='--')

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "chart3_amount_vs_cycle.png", dpi=200, bbox_inches='tight')
    plt.close()
    print("OK - Chart 3 完成")

# Chart 4: 客戶分群
def chart4():
    print("\n生成 Chart 4...")
    segment_stats = matched_orders.groupby('customer_segment').agg({
        'company_id': 'count',
        'order_amount': 'mean'
    }).rename(columns={'company_id': 'count', 'order_amount': 'avg_amount'})

    segment_order = ['新客戶 - 小客戶', '新客戶 - 大客戶', '老客戶 - 小客戶', '老客戶 - 大客戶']
    segment_stats = segment_stats.reindex([s for s in segment_order if s in segment_stats.index])

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))
    colors = ['#3498db', '#9b59b6', '#2ecc71', '#e74c3c']

    # 訂單數
    bars1 = ax1.bar(range(len(segment_stats)), segment_stats['count'], color=colors,
                    edgecolor='white', linewidth=1, width=0.7)
    ax1.set_xlabel('客戶分群', fontsize=12, fontweight='bold')
    ax1.set_ylabel('訂單數', fontsize=12, fontweight='bold')
    ax1.set_title('各分群訂單數', fontsize=14, fontweight='bold')
    ax1.set_xticks(range(len(segment_stats)))
    ax1.set_xticklabels(segment_stats.index, rotation=20, ha='right', fontsize=10)
    ax1.grid(axis='y', alpha=0.3, linestyle='--')

    for i, bar in enumerate(bars1):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}', ha='center', va='bottom', fontsize=10, fontweight='bold')

    # 平均金額
    bars2 = ax2.bar(range(len(segment_stats)), segment_stats['avg_amount'], color=colors,
                    edgecolor='white', linewidth=1, width=0.7)
    ax2.set_xlabel('客戶分群', fontsize=12, fontweight='bold')
    ax2.set_ylabel('平均訂單金額（元）', fontsize=12, fontweight='bold')
    ax2.set_title('各分群平均金額', fontsize=14, fontweight='bold')
    ax2.set_xticks(range(len(segment_stats)))
    ax2.set_xticklabels(segment_stats.index, rotation=20, ha='right', fontsize=10)
    ax2.grid(axis='y', alpha=0.3, linestyle='--')

    for i, bar in enumerate(bars2):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height):,}', ha='center', va='bottom', fontsize=10, fontweight='bold')

    plt.suptitle('客戶分群分析', fontsize=16, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "chart4_customer_segments.png", dpi=200, bbox_inches='tight')
    plt.close()
    print("OK - Chart 4 完成")

# Chart 5: 箱型圖
def chart5():
    print("\n生成 Chart 5...")
    stage_order = ['A', 'B', 'C1', 'C2', 'D', 'E']
    stage_data = []
    stage_labels = []

    for s in stage_order:
        data = matched_orders[matched_orders['final_stage'] == s]['days_before_order'].values
        if len(data) > 0:
            stage_data.append(data)
            stage_labels.append(s)

    fig, ax = plt.subplots(figsize=(14, 7))

    bp = ax.boxplot(stage_data, labels=stage_labels, patch_artist=True, widths=0.6,
                    boxprops=dict(facecolor='#64B5F6', alpha=0.8, linewidth=1.5),
                    medianprops=dict(color='#D32F2F', linewidth=3),
                    whiskerprops=dict(color='#424242', linewidth=1.5),
                    capprops=dict(color='#424242', linewidth=1.5),
                    flierprops=dict(marker='o', markerfacecolor='#FF5722', markersize=4, alpha=0.5))

    ax.set_xlabel('商機階段', fontsize=14, fontweight='bold')
    ax.set_ylabel('成交週期（天）', fontsize=14, fontweight='bold')
    ax.set_title('各階段成交週期分布（箱型圖）', fontsize=16, fontweight='bold', pad=20)
    ax.grid(axis='y', alpha=0.3, linestyle='--')

    # 添加統計標註
    for i, data in enumerate(stage_data):
        median = np.median(data)
        ax.text(i+1, median, f'{median:.0f}', ha='left', va='center',
                fontsize=9, fontweight='bold', color='#D32F2F')

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "chart5_cycle_boxplot.png", dpi=200, bbox_inches='tight')
    plt.close()
    print("OK - Chart 5 完成")

# Chart 6: CDF
def chart6():
    print("\n生成 Chart 6...")
    stage_order = ['A', 'B', 'C1', 'C2', 'D', 'E']
    colors = ['#F44336', '#FF9800', '#FFC107', '#8BC34A', '#4CAF50', '#2196F3']

    fig, ax = plt.subplots(figsize=(14, 7))

    for stage, color in zip(stage_order, colors):
        data = matched_orders[matched_orders['final_stage'] == stage]['days_before_order'].values
        if len(data) > 0:
            data_sorted = np.sort(data)
            cdf = np.arange(1, len(data_sorted) + 1) / len(data_sorted)
            ax.plot(data_sorted, cdf * 100, label=f'{stage} 階段', linewidth=3, color=color)

    ax.set_xlabel('成交週期（天）', fontsize=14, fontweight='bold')
    ax.set_ylabel('累積百分比 (%)', fontsize=14, fontweight='bold')
    ax.set_title('成交週期累積分布曲線（CDF）', fontsize=16, fontweight='bold', pad=20)
    ax.legend(loc='lower right', fontsize=11, framealpha=0.9)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_xlim(left=0)
    ax.set_ylim([0, 100])

    # 添加參考線
    for pct in [25, 50, 75]:
        ax.axhline(y=pct, color='gray', linestyle=':', alpha=0.5, linewidth=1)
        ax.text(ax.get_xlim()[1] * 0.98, pct, f'{pct}%',
               ha='right', va='bottom', fontsize=9, color='gray')

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "chart6_cdf.png", dpi=200, bbox_inches='tight')
    plt.close()
    print("OK - Chart 6 完成")

# 執行
if __name__ == "__main__":
    print("=" * 60)
    print("Phase 4 獨立圖表生成器")
    print("=" * 60)

    chart1()
    chart2()
    chart3()
    chart4()
    chart5()
    chart6()

    print("\n" + "=" * 60)
    print(f"✓ 所有圖表已儲存至: {OUTPUT_DIR.absolute()}")
    print("=" * 60)

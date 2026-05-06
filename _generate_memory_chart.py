"""
生成記憶體需求折線圖（近一年實測 + 未來五年預測）
"""
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from pathlib import Path
import numpy as np
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

# 設定中文字體
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei', 'SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

def calculate_memory_requirement(daily_logs):
    """根據日均處理量計算記憶體需求（GB）"""
    # 基於實測數據的線性關係：685筆=5GB, 1030筆=6GB, 1356筆=8GB
    # 平均：記憶體(GB) ≈ 處理量 / 170 + 1
    return daily_logs / 170 + 1

def generate_memory_chart():
    """生成記憶體需求折線圖"""

    # ===== 近一年實測數據（基於之前查詢的每月數據）=====
    historical_months = [
        '2025-05', '2025-06', '2025-07', '2025-08', '2025-09', '2025-10',
        '2025-11', '2025-12', '2026-01', '2026-02', '2026-03', '2026-04'
    ]

    # 每月新增量（筆）
    monthly_logs = [15361, 15154, 15703, 14399, 15462, 15228,
                    14773, 15250, 15592, 6813, 18658, 16105]

    # 計算每月平日日均（除以22個工作日）
    daily_avg = [m / 22 for m in monthly_logs]

    # 計算所需記憶體（峰值，日均 + 1.5σ）
    # 標準差約為 231（從實測數據）
    sigma = 231
    peak_daily = [d + 1.5 * (sigma / np.sqrt(22)) for d in daily_avg]
    memory_historical = [calculate_memory_requirement(p) for p in peak_daily]

    # ===== 未來預測（三種情境）=====
    # 基準點：2026-05 的平日日均 = 685 筆
    base_daily = 685
    base_memory = calculate_memory_requirement(base_daily + 1.5 * sigma)

    # 未來月份
    future_months = []
    base_date = datetime(2026, 5, 1)
    for i in range(1, 61):  # 未來60個月（5年）
        future_date = base_date + relativedelta(months=i)
        future_months.append(future_date.strftime('%Y-%m'))

    # 三種情境預測
    scenarios = {
        '基準情境 (+5%/年)': 0.05,
        '樂觀情境 (+15%/年)': 0.15,
        '悲觀情境 (0%)': 0.00
    }

    memory_forecast = {}
    for scenario_name, annual_growth in scenarios.items():
        monthly_growth = (1 + annual_growth) ** (1/12) - 1
        forecast = []
        current_daily = base_daily

        for month_idx in range(60):
            current_daily *= (1 + monthly_growth)
            peak = current_daily + 1.5 * sigma
            memory = calculate_memory_requirement(peak)
            forecast.append(memory)

        memory_forecast[scenario_name] = forecast

    # ===== 繪製圖表 =====
    fig, ax = plt.subplots(figsize=(14, 7))

    # X 軸標籤（合併歷史與未來）
    all_months = historical_months + future_months
    x_positions = range(len(all_months))

    # 歷史數據（實線，粗）
    ax.plot(range(len(memory_historical)), memory_historical,
            marker='o', linewidth=2.5, color='#2E75B6',
            label='實測數據 (2025-05 ~ 2026-04)', markersize=6, zorder=3)

    # 未來預測（虛線）
    colors = {'基準情境 (+5%/年)': '#70AD47',
              '樂觀情境 (+15%/年)': '#C55A11',
              '悲觀情境 (0%)': '#7F7F7F'}

    offset = len(memory_historical)
    for scenario_name, forecast in memory_forecast.items():
        ax.plot(range(offset, offset + len(forecast)), forecast,
                linestyle='--', linewidth=2, color=colors[scenario_name],
                label=scenario_name, alpha=0.8)

    # 標記關鍵時間點
    key_points = {
        11: ('當前', '#2E75B6'),  # 2026-04
        23: ('1年後', '#70AD47'),  # 2027-04
        47: ('3年後', '#70AD47'),  # 2029-04
        71: ('5年後', '#70AD47'),  # 2031-04
    }

    for month_idx, (label, color) in key_points.items():
        if month_idx == 11:
            y_val = memory_historical[-1]
        else:
            y_val = memory_forecast['基準情境 (+5%/年)'][month_idx - offset]

        ax.axvline(x=month_idx, color=color, linestyle=':', linewidth=1, alpha=0.5)
        ax.annotate(label, xy=(month_idx, y_val),
                   xytext=(5, 10), textcoords='offset points',
                   fontsize=10, color=color, weight='bold',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                            edgecolor=color, alpha=0.8))

    # 標記記憶體升級點
    upgrade_points = [
        (35, 7, '建議升級至 16GB', '#C55A11'),  # 第3年，樂觀情境
        (59, 11.5, '建議升級至 20GB', '#C55A11'),  # 第5年，樂觀情境
    ]

    for x, y, text, color in upgrade_points:
        ax.scatter([x], [y], s=100, marker='X', color=color, zorder=5, edgecolors='white', linewidths=1.5)
        ax.annotate(text, xy=(x, y), xytext=(10, -15),
                   textcoords='offset points', fontsize=9,
                   color=color, weight='bold',
                   arrowprops=dict(arrowstyle='->', color=color, lw=1.5),
                   bbox=dict(boxstyle='round,pad=0.4', facecolor='#FFF2CC',
                            edgecolor=color, alpha=0.9))

    # 圖表美化
    ax.set_xlabel('時間（年-月）', fontsize=12, weight='bold')
    ax.set_ylabel('記憶體需求（GB）', fontsize=12, weight='bold')
    ax.set_title('記憶體需求趨勢分析：近一年實測 + 未來五年預測',
                fontsize=14, weight='bold', pad=20)

    # X 軸標籤（每6個月顯示一次）
    xtick_positions = list(range(0, len(all_months), 6))
    xtick_labels = [all_months[i] for i in xtick_positions]
    ax.set_xticks(xtick_positions)
    ax.set_xticklabels(xtick_labels, rotation=45, ha='right', fontsize=9)

    # Y 軸範圍
    ax.set_ylim(3, 13)
    ax.set_yticks(range(3, 14, 1))

    # 網格
    ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
    ax.set_axisbelow(True)

    # 圖例
    ax.legend(loc='upper left', fontsize=10, framealpha=0.95,
             edgecolor='gray', fancybox=True, shadow=True)

    # 添加陰影區域（建議配置）
    ax.axhspan(0, 8, alpha=0.05, color='green', label='_nolegend_')
    ax.axhspan(8, 12, alpha=0.05, color='orange', label='_nolegend_')
    ax.axhspan(12, 13, alpha=0.08, color='red', label='_nolegend_')

    # 添加註解文字
    ax.text(1, 7.5, '安全範圍\n(8GB以下)', fontsize=9, color='green',
           alpha=0.6, weight='bold', ha='left')
    ax.text(1, 10, '需升級\n(8-12GB)', fontsize=9, color='orange',
           alpha=0.6, weight='bold', ha='left')
    ax.text(1, 12.5, '需重構\n(12GB以上)', fontsize=9, color='red',
           alpha=0.6, weight='bold', ha='left')

    plt.tight_layout()

    # 保存圖表
    output_path = Path(r"d:\yujui\痛點需求地圖\prompt定版\memory_forecast_chart.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"[OK] Chart saved: {output_path.name}")
    print(f"  Resolution: 300 DPI")
    print(f"  Size: {output_path.stat().st_size / 1024:.1f} KB")

    plt.close()

    return output_path

if __name__ == "__main__":
    print("Generating memory requirement forecast chart...")
    print("-" * 80)
    chart_path = generate_memory_chart()
    print("-" * 80)
    print(f"Chart file: {chart_path}")

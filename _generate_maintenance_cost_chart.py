"""
生成人力維運成本分析圖表
"""
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from pathlib import Path
import numpy as np

# 設定中文字體
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei', 'SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

def generate_maintenance_cost_chart():
    """生成維運成本分析圖表"""

    # 創建 2x2 子圖
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('系統維運人力成本分析', fontsize=16, weight='bold', y=0.995)

    # ===== 圖表 1：年度維運工時分布 =====
    tasks = ['索引維護\n(月度)', '效能監控\n(日常)', '問題排查\n(季度)',
             '備份驗證\n(月度)', '系統優化\n(年度)']

    # 每次執行時間（小時）
    time_per_execution = [0.5, 0.1, 1.5, 0.3, 4]
    # 年度執行次數
    executions_per_year = [12, 250, 4, 12, 1]
    # 年度總工時
    annual_hours = [t * e for t, e in zip(time_per_execution, executions_per_year)]

    colors = ['#4472C4', '#ED7D31', '#A5A5A5', '#FFC000', '#70AD47']

    bars = ax1.barh(tasks, annual_hours, color=colors, alpha=0.8)
    ax1.set_xlabel('年度工時 (小時)', fontsize=10, weight='bold')
    ax1.set_title('圖 1：年度維運工時分布', fontsize=11, weight='bold')
    ax1.grid(axis='x', alpha=0.3, linestyle='--')

    # 添加數值標籤
    for bar, hours in zip(bars, annual_hours):
        width = bar.get_width()
        ax1.text(width + 1, bar.get_y() + bar.get_height()/2,
                f'{hours:.1f}h',
                ha='left', va='center', fontsize=9, weight='bold')

    # 總計標註
    total_hours = sum(annual_hours)
    ax1.text(0.98, 0.02, f'年度總工時：{total_hours:.1f} 小時',
            transform=ax1.transAxes, fontsize=10, weight='bold',
            ha='right', va='bottom',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.3))

    # ===== 圖表 2：維運成本 vs 系統總成本（餅圖）=====
    # 第 1 年成本結構
    cost_labels = ['API 費用\n$155', '伺服器租用\n$1,800',
                   '維運人力\n$1,025', '索引建置\n$110']
    cost_values = [155, 1800, 1025, 110]
    cost_colors = ['#4472C4', '#ED7D31', '#70AD47', '#FFC000']

    wedges, texts, autotexts = ax2.pie(cost_values, labels=cost_labels,
                                        autopct='%1.1f%%', colors=cost_colors,
                                        startangle=90, textprops={'fontsize': 9})

    # 強調維運人力
    wedges[2].set_edgecolor('red')
    wedges[2].set_linewidth(2)

    ax2.set_title('圖 2：第 1 年成本結構（總計 $3,090）', fontsize=11, weight='bold')

    # ===== 圖表 3：5 年累積成本對比 =====
    years = ['第 1 年', '第 2 年', '第 3 年', '第 4 年', '第 5 年']

    # 基準情境（+5%成長）
    api_costs = [155, 163, 180, 189, 198]
    server_costs = [1800, 1800, 1920, 1920, 2400]
    maintenance_costs = [1025, 1025, 1025, 1025, 1025]  # 維運成本相對穩定
    index_costs = [110, 0, 0, 0, 0]  # 索引建置一次性

    x = np.arange(len(years))
    width = 0.6

    bars1 = ax3.bar(x, api_costs, width, label='API 費用', color='#4472C4', alpha=0.8)
    bars2 = ax3.bar(x, server_costs, width, bottom=api_costs,
                    label='伺服器租用', color='#ED7D31', alpha=0.8)
    bars3 = ax3.bar(x, maintenance_costs, width,
                    bottom=[a+s for a, s in zip(api_costs, server_costs)],
                    label='維運人力', color='#70AD47', alpha=0.8)
    bars4 = ax3.bar(x, index_costs, width,
                    bottom=[a+s+m for a, s, m in zip(api_costs, server_costs, maintenance_costs)],
                    label='索引建置', color='#FFC000', alpha=0.8)

    ax3.set_ylabel('年度成本 ($)', fontsize=10, weight='bold')
    ax3.set_title('圖 3：5 年成本演進（基準情境）', fontsize=11, weight='bold')
    ax3.set_xticks(x)
    ax3.set_xticklabels(years, fontsize=9)
    ax3.legend(fontsize=9, loc='upper left')
    ax3.grid(axis='y', alpha=0.3, linestyle='--')

    # 添加總計標籤
    totals = [a+s+m+i for a, s, m, i in zip(api_costs, server_costs, maintenance_costs, index_costs)]
    for i, total in enumerate(totals):
        ax3.text(i, total + 100, f'${total:,}',
                ha='center', va='bottom', fontsize=9, weight='bold')

    # ===== 圖表 4：維運工時趨勢（月度）=====
    months = range(1, 13)

    # 模擬月度工時波動
    monthly_hours = []
    for month in months:
        base = 2.0  # 基礎監控時間

        # 月度索引維護
        if month % 1 == 0:  # 每月
            base += 0.5

        # 季度深度檢查
        if month % 3 == 0:  # 每季
            base += 1.5

        # 年度大維護
        if month == 12:
            base += 4.0

        monthly_hours.append(base)

    ax4.plot(months, monthly_hours, marker='o', linewidth=2,
            color='#70AD47', markersize=6, label='實際工時')
    ax4.axhline(y=np.mean(monthly_hours), color='orange', linestyle='--',
               linewidth=2, label=f'月均工時 ({np.mean(monthly_hours):.1f}h)')

    ax4.set_xlabel('月份', fontsize=10, weight='bold')
    ax4.set_ylabel('工時 (小時)', fontsize=10, weight='bold')
    ax4.set_title('圖 4：月度維運工時趨勢', fontsize=11, weight='bold')
    ax4.set_xticks(months)
    ax4.set_xticklabels([f'{m}月' for m in months], fontsize=8)
    ax4.legend(fontsize=9)
    ax4.grid(True, alpha=0.3, linestyle='--')
    ax4.set_ylim(0, 10)

    # 標記高峰月份
    peak_months = [3, 6, 9, 12]
    for pm in peak_months:
        ax4.axvspan(pm-0.3, pm+0.3, alpha=0.1, color='red')

    ax4.text(6, 9, '季度/年度維護高峰',
            fontsize=9, ha='center',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.3))

    plt.tight_layout()

    # 保存圖表
    output_path = Path(r"d:\yujui\痛點需求地圖\prompt定版\maintenance_cost_chart.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"[OK] Maintenance cost chart saved")
    print(f"  File: {output_path.name}")
    print(f"  Size: {output_path.stat().st_size / 1024:.1f} KB")

    plt.close()
    return output_path, total_hours

if __name__ == "__main__":
    print("Generating maintenance cost analysis chart...")
    print("-" * 80)
    chart_path, total_hours = generate_maintenance_cost_chart()
    print("-" * 80)
    print(f"Chart saved: {chart_path}")
    print(f"Annual maintenance hours: {total_hours:.1f}")

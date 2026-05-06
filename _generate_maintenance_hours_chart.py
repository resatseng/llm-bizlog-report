"""
生成人力維運工時分析圖表（僅工時，不含成本）
"""
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from pathlib import Path
import numpy as np

# 設定中文字體
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei', 'SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

def generate_maintenance_hours_chart():
    """生成維運工時分析圖表"""

    # 創建 2x2 子圖
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('系統維運工時分析', fontsize=16, weight='bold', y=0.995)

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

    # ===== 圖表 2：工時分配（人員別）=====
    personnel = ['DBA', '工程師']
    dba_hours = 6 + 3.6 + 4 + 1  # 索引維護 + 備份 + 優化 + 建置（第1年）
    engineer_hours = 25 + 6 * 0.5  # 監控 + 問題排查（50%）
    hours_by_personnel = [dba_hours, engineer_hours]
    colors_personnel = ['#4472C4', '#ED7D31']

    bars2 = ax2.bar(personnel, hours_by_personnel, color=colors_personnel, alpha=0.8, width=0.5)
    ax2.set_ylabel('年度工時 (小時)', fontsize=10, weight='bold')
    ax2.set_title('圖 2：維運工時分配（人員別）', fontsize=11, weight='bold')
    ax2.grid(axis='y', alpha=0.3, linestyle='--')

    # 添加數值標籤
    for bar, hours in zip(bars2, hours_by_personnel):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{hours:.1f}h',
                ha='center', va='bottom', fontsize=10, weight='bold')

    # 添加百分比
    for i, (bar, hours) in enumerate(zip(bars2, hours_by_personnel)):
        percentage = (hours / total_hours) * 100
        ax2.text(bar.get_x() + bar.get_width()/2., height * 0.5,
                f'{percentage:.1f}%',
                ha='center', va='center', fontsize=9, color='white', weight='bold')

    # ===== 圖表 3：5 年累積工時 =====
    years = ['第 1 年', '第 2 年', '第 3 年', '第 4 年', '第 5 年']

    # 第 1 年包含索引建置（1小時），第 2-5 年為常態工時
    yearly_hours = [45.6, 44.6, 44.6, 44.6, 44.6]
    cumulative_hours = []
    total = 0
    for h in yearly_hours:
        total += h
        cumulative_hours.append(total)

    x = np.arange(len(years))
    width = 0.35

    bars3_yearly = ax3.bar(x - width/2, yearly_hours, width,
                          label='年度工時', color='#4472C4', alpha=0.8)
    bars3_cumulative = ax3.bar(x + width/2, cumulative_hours, width,
                              label='累積工時', color='#70AD47', alpha=0.8)

    ax3.set_ylabel('工時 (小時)', fontsize=10, weight='bold')
    ax3.set_title('圖 3：5 年工時累積', fontsize=11, weight='bold')
    ax3.set_xticks(x)
    ax3.set_xticklabels(years, fontsize=9)
    ax3.legend(fontsize=9, loc='upper left')
    ax3.grid(axis='y', alpha=0.3, linestyle='--')

    # 添加數值標籤
    for bars in [bars3_yearly, bars3_cumulative]:
        for bar in bars:
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.1f}',
                    ha='center', va='bottom', fontsize=8)

    # ===== 圖表 4：月度維運工時趨勢 =====
    months = range(1, 13)

    # 模擬月度工時波動
    monthly_hours = []
    for month in months:
        base = 2.0  # 基礎監控時間（每日 0.1h × 20工作日 = 2h）

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
    output_path = Path(r"d:\yujui\痛點需求地圖\prompt定版\maintenance_hours_chart.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"[OK] Maintenance hours chart saved")
    print(f"  File: {output_path.name}")
    print(f"  Size: {output_path.stat().st_size / 1024:.1f} KB")

    plt.close()
    return output_path, total_hours

if __name__ == "__main__":
    print("Generating maintenance hours analysis chart...")
    print("-" * 80)
    chart_path, total_hours = generate_maintenance_hours_chart()
    print("-" * 80)
    print(f"Chart saved: {chart_path}")
    print(f"Annual maintenance hours: {total_hours:.1f}")

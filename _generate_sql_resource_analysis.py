"""
生成 SQL 查詢資源需求分析圖表
"""
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from pathlib import Path
import numpy as np

# 設定中文字體
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei', 'SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

def generate_sql_resource_charts():
    """生成 SQL 資源需求分析圖表（多子圖）"""

    # 創建 2x2 子圖
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('SQL Server 查詢資源需求評估', fontsize=16, weight='bold', y=0.995)

    # ===== 圖表 1：資料傳輸量（日均/峰值/極端） =====
    scenarios = ['日均\n(685筆)', '峰值\n(1,030筆)', '極端峰值\n(1,356筆)']

    # Phase 0: 增量日報查詢（6個欄位，平均每筆 2KB）
    phase0_data = [685 * 2, 1030 * 2, 1356 * 2]  # KB

    # Phase 3: 合約資料 JOIN（假設每筆日報關聯平均 3 筆合約，每筆合約 1.5KB）
    phase3_data = [685 * 3 * 1.5, 1030 * 3 * 1.5, 1356 * 3 * 1.5]  # KB

    # 總計
    total_data = [p0 + p3 for p0, p3 in zip(phase0_data, phase3_data)]

    x = np.arange(len(scenarios))
    width = 0.25

    bars1 = ax1.bar(x - width, [d/1024 for d in phase0_data], width,
                    label='Phase 0: 日報查詢', color='#4472C4', alpha=0.8)
    bars2 = ax1.bar(x, [d/1024 for d in phase3_data], width,
                    label='Phase 3: 合約 JOIN', color='#ED7D31', alpha=0.8)
    bars3 = ax1.bar(x + width, [d/1024 for d in total_data], width,
                    label='總計', color='#70AD47', alpha=0.8)

    ax1.set_xlabel('處理情境', fontsize=10, weight='bold')
    ax1.set_ylabel('資料傳輸量 (MB)', fontsize=10, weight='bold')
    ax1.set_title('圖 1：SQL 資料傳輸量評估', fontsize=11, weight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(scenarios, fontsize=9)
    ax1.legend(fontsize=9, loc='upper left')
    ax1.grid(axis='y', alpha=0.3, linestyle='--')

    # 添加數值標籤
    for bars in [bars1, bars2, bars3]:
        for bar in bars:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.1f}',
                    ha='center', va='bottom', fontsize=8)

    # ===== 圖表 2：查詢時間估算 =====
    query_types = ['Phase 0\n增量查詢', 'Phase 3\n合約 JOIN', 'Phase 3\n續約分析\nGROUP BY']

    # 查詢時間（秒）- 基於日均 685 筆
    time_no_index = [15, 60, 90]  # 無索引
    time_with_index = [3, 12, 20]  # 有索引

    x2 = np.arange(len(query_types))
    width2 = 0.35

    bars_no = ax2.bar(x2 - width2/2, time_no_index, width2,
                      label='無索引', color='#C55A11', alpha=0.7)
    bars_yes = ax2.bar(x2 + width2/2, time_with_index, width2,
                       label='有索引（建議）', color='#70AD47', alpha=0.8)

    ax2.set_xlabel('查詢類型', fontsize=10, weight='bold')
    ax2.set_ylabel('查詢時間 (秒)', fontsize=10, weight='bold')
    ax2.set_title('圖 2：查詢效能比較（有/無索引）', fontsize=11, weight='bold')
    ax2.set_xticks(x2)
    ax2.set_xticklabels(query_types, fontsize=9)
    ax2.legend(fontsize=9)
    ax2.grid(axis='y', alpha=0.3, linestyle='--')

    # 添加改善比例標註
    for i, (no, yes) in enumerate(zip(time_no_index, time_with_index)):
        improvement = ((no - yes) / no) * 100
        ax2.text(i, max(no, yes) + 5, f'↓{improvement:.0f}%',
                ha='center', fontsize=9, color='green', weight='bold')

    # 添加數值標籤
    for bars in [bars_no, bars_yes]:
        for bar in bars:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.0f}s',
                    ha='center', va='bottom', fontsize=8)

    # ===== 圖表 3：SQL Server 資源消耗（CPU/記憶體/I/O）=====
    resources = ['CPU\n使用率', '記憶體\n佔用', '磁碟 I/O\n(IOPS)']

    # 日均情境（%）
    cpu_usage = [5, 8, 15]  # CPU 使用率 %
    memory_mb = [50, 120, 80]  # 記憶體 MB
    disk_iops = [200, 800, 500]  # 磁碟 IOPS

    # 歸一化到百分比（以最大值為 100%）
    cpu_normalized = cpu_usage
    memory_normalized = [m / 2 for m in memory_mb]  # 除以 2 轉為百分比尺度
    iops_normalized = [io / 10 for io in disk_iops]  # 除以 10 轉為百分比尺度

    x3 = np.arange(len(resources))
    width3 = 0.6

    bars_cpu = ax3.bar(0, cpu_usage[0], width3, color='#4472C4', alpha=0.7)
    bars_mem = ax3.bar(1, memory_mb[1], width3, color='#ED7D31', alpha=0.7)
    bars_io = ax3.bar(2, disk_iops[2], width3, color='#70AD47', alpha=0.7)

    ax3.set_ylabel('資源使用量', fontsize=10, weight='bold')
    ax3.set_title('圖 3：SQL Server 資源消耗（日均情境）', fontsize=11, weight='bold')
    ax3.set_xticks(x3)
    ax3.set_xticklabels(resources, fontsize=9)
    ax3.grid(axis='y', alpha=0.3, linestyle='--')

    # 雙 Y 軸
    ax3_twin = ax3.twinx()
    ax3.set_ylabel('CPU (%) / 記憶體 (MB)', fontsize=9, weight='bold', color='#4472C4')
    ax3_twin.set_ylabel('磁碟 I/O (IOPS)', fontsize=9, weight='bold', color='#70AD47')

    # 添加數值標籤
    ax3.text(0, cpu_usage[0] + 0.5, f'{cpu_usage[0]}%', ha='center', fontsize=9, weight='bold')
    ax3.text(1, memory_mb[1] + 5, f'{memory_mb[1]} MB', ha='center', fontsize=9, weight='bold')
    ax3.text(2, disk_iops[2] + 20, f'{disk_iops[2]} IOPS', ha='center', fontsize=9, weight='bold')

    # 添加安全範圍線
    ax3.axhline(y=20, color='orange', linestyle='--', linewidth=1, alpha=0.5, label='CPU 警戒線 (20%)')
    ax3.legend(fontsize=8, loc='upper left')

    # ===== 圖表 4：網路頻寬需求時間線 =====
    # 模擬一天的查詢時間分布（每日 06:00 執行，持續約 1 小時）
    hours = np.arange(0, 24, 1)
    bandwidth_mbps = np.zeros(24)

    # 06:00-07:00 期間的資料傳輸
    # 日均情境：總傳輸量 ~9.8 MB，在 45 分鐘內完成
    # 平均頻寬：9.8 MB / 45 min = 0.22 MB/min = 0.029 Mbps（峰值約 0.5 Mbps）
    bandwidth_mbps[6] = 0.4  # 06:00-07:00
    bandwidth_mbps[7] = 0.2  # 07:00-08:00（尾聲）

    # 峰值情境
    bandwidth_peak = bandwidth_mbps.copy()
    bandwidth_peak[6] = 0.7
    bandwidth_peak[7] = 0.4

    ax4.plot(hours, bandwidth_mbps, marker='o', linewidth=2,
            color='#4472C4', label='日均情境 (685筆)', markersize=5)
    ax4.plot(hours, bandwidth_peak, marker='s', linewidth=2, linestyle='--',
            color='#C55A11', label='峰值情境 (1,030筆)', markersize=5)

    ax4.set_xlabel('時間（小時）', fontsize=10, weight='bold')
    ax4.set_ylabel('網路頻寬 (Mbps)', fontsize=10, weight='bold')
    ax4.set_title('圖 4：網路頻寬需求（24小時時間線）', fontsize=11, weight='bold')
    ax4.set_xticks(range(0, 24, 2))
    ax4.set_xticklabels([f'{h:02d}:00' for h in range(0, 24, 2)], fontsize=8, rotation=45)
    ax4.legend(fontsize=9, loc='upper right')
    ax4.grid(True, alpha=0.3, linestyle='--')
    ax4.set_ylim(0, 1)

    # 標記執行時段
    ax4.axvspan(6, 7.75, alpha=0.1, color='green', label='_nolegend_')
    ax4.text(6.8, 0.85, 'Pipeline 執行時段\n(06:00-07:45)',
            fontsize=9, ha='center', bbox=dict(boxstyle='round,pad=0.5',
            facecolor='yellow', alpha=0.3))

    plt.tight_layout()

    # 保存圖表
    output_path = Path(r"d:\yujui\痛點需求地圖\prompt定版\sql_resource_analysis.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"[OK] SQL resource analysis chart saved")
    print(f"  File: {output_path.name}")
    print(f"  Size: {output_path.stat().st_size / 1024:.1f} KB")

    plt.close()
    return output_path

if __name__ == "__main__":
    print("Generating SQL resource analysis charts...")
    print("-" * 80)
    chart_path = generate_sql_resource_charts()
    print("-" * 80)
    print(f"Chart saved: {chart_path}")

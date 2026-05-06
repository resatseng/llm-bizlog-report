"""
生成五大策略視覺化圖表
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
from pathlib import Path
import numpy as np

# 設定中文字體
matplotlib.rcParams['font.sans-serif'] = ['Microsoft JhengHei', 'SimHei']
matplotlib.rcParams['axes.unicode_minus'] = False

# 路徑設定
BASE_DIR = Path(r'd:\yujui\痛點需求地圖\prompt定版')
OUTPUT_DIR = BASE_DIR / '策略分析結果'

# 讀取數據
comparison = pd.read_csv(OUTPUT_DIR / '五大策略比較表.csv')
clusters = pd.read_csv(OUTPUT_DIR / '聚類分析詳細.csv')

# 提取數值數據
strategies = comparison['策略'].values
pools = comparison['潛在池(家)'].values
conversions = comparison['預期成交(家)'].values
revenues = [float(r) for r in comparison['預期營收(億)'].values]
difficulties = comparison['執行難度'].values

# ============ 圖表 1: 策略比較雷達圖 ============
fig = plt.figure(figsize=(16, 10))

# 子圖 1: 策略潛力比較（條形圖）
ax1 = plt.subplot(2, 2, 1)
colors = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6']
bars = ax1.barh(range(5), conversions, color=colors, alpha=0.7, edgecolor='black')

# 在條形上添加數值
for i, (bar, val, rev) in enumerate(zip(bars, conversions, revenues)):
    width = bar.get_width()
    if width > 0:
        ax1.text(width + 200, bar.get_y() + bar.get_height()/2,
                f'{val:,}家\n{rev:.1f}億',
                ha='left', va='center', fontsize=10, fontweight='bold')

ax1.set_yticks(range(5))
ax1.set_yticklabels([s.replace('1. ', '').replace('2. ', '').replace('3. ', '').replace('4. ', '').replace('5. ', '')
                      for s in strategies])
ax1.set_xlabel('預期成交家數', fontsize=12, fontweight='bold')
ax1.set_title('策略 1: 預期成交家數比較', fontsize=14, fontweight='bold', pad=20)
ax1.grid(axis='x', alpha=0.3, linestyle='--')
ax1.set_xlim(0, max(conversions) * 1.15 if max(conversions) > 0 else 100)

# 子圖 2: 營收潛力比較
ax2 = plt.subplot(2, 2, 2)
bars2 = ax2.barh(range(5), revenues, color=colors, alpha=0.7, edgecolor='black')

for i, (bar, val) in enumerate(zip(bars2, revenues)):
    width = bar.get_width()
    if width > 0:
        ax2.text(width + 5, bar.get_y() + bar.get_height()/2,
                f'{val:.1f}億',
                ha='left', va='center', fontsize=10, fontweight='bold')

ax2.set_yticks(range(5))
ax2.set_yticklabels([s.replace('1. ', '').replace('2. ', '').replace('3. ', '').replace('4. ', '').replace('5. ', '')
                      for s in strategies])
ax2.set_xlabel('預期營收（億元）', fontsize=12, fontweight='bold')
ax2.set_title('策略 2: 預期營收比較', fontsize=14, fontweight='bold', pad=20)
ax2.grid(axis='x', alpha=0.3, linestyle='--')
ax2.set_xlim(0, max(revenues) * 1.15 if max(revenues) > 0 else 10)

# 子圖 3: 潛在客戶池比較
ax3 = plt.subplot(2, 2, 3)
bars3 = ax3.barh(range(5), pools, color=colors, alpha=0.7, edgecolor='black')

for i, (bar, val) in enumerate(zip(bars3, pools)):
    width = bar.get_width()
    if width > 0:
        ax3.text(width + 1000, bar.get_y() + bar.get_height()/2,
                f'{val:,}家',
                ha='left', va='center', fontsize=10, fontweight='bold')

ax3.set_yticks(range(5))
ax3.set_yticklabels([s.replace('1. ', '').replace('2. ', '').replace('3. ', '').replace('4. ', '').replace('5. ', '')
                      for s in strategies])
ax3.set_xlabel('潛在客戶池（家）', fontsize=12, fontweight='bold')
ax3.set_title('策略 3: 潛在客戶池規模', fontsize=14, fontweight='bold', pad=20)
ax3.grid(axis='x', alpha=0.3, linestyle='--')
ax3.set_xlim(0, max(pools) * 1.15 if max(pools) > 0 else 1000)

# 子圖 4: ROI 效益矩陣
ax4 = plt.subplot(2, 2, 4)

# 計算 ROI (營收/潛在池)
roi = []
for i in range(5):
    if pools[i] > 0:
        roi.append(revenues[i] / pools[i] * 1000)  # 每千家的營收
    else:
        roi.append(0)

# 難度映射
difficulty_map = {'低': 1, '中': 2, '高': 3}
difficulty_scores = [difficulty_map.get(d, 2) for d in difficulties]

# 散點圖
scatter = ax4.scatter(difficulty_scores, roi, s=[r*30 for r in revenues],
                      c=colors, alpha=0.6, edgecolors='black', linewidth=2)

# 標註策略名稱
for i, (x, y, s) in enumerate(zip(difficulty_scores, roi, strategies)):
    if y > 0:
        label = s.replace('1. ', '').replace('2. ', '').replace('3. ', '').replace('4. ', '').replace('5. ', '')
        ax4.annotate(label, (x, y), xytext=(5, 5), textcoords='offset points',
                    fontsize=9, fontweight='bold')

ax4.set_xlabel('執行難度', fontsize=12, fontweight='bold')
ax4.set_ylabel('ROI（每千家營收，億元）', fontsize=12, fontweight='bold')
ax4.set_title('策略 4: 效益-難度矩陣（圓圈大小=營收）', fontsize=14, fontweight='bold', pad=20)
ax4.set_xticks([1, 2, 3])
ax4.set_xticklabels(['低', '中', '高'])
ax4.grid(alpha=0.3, linestyle='--')
ax4.set_xlim(0.5, 3.5)

plt.tight_layout()
plt.savefig(OUTPUT_DIR / '五大策略視覺化比較.png', dpi=300, bbox_inches='tight')
print(f"圖表 1 已儲存: {OUTPUT_DIR / '五大策略視覺化比較.png'}")

# ============ 圖表 2: 聚類分析視覺化 ============
fig2, ((ax5, ax6), (ax7, ax8)) = plt.subplots(2, 2, figsize=(16, 12))

# 子圖 5: 聚類轉換率比較
cluster_names = clusters['cluster_name'].values
conversion_rates = clusters['conversion_rate'].values * 100

bars5 = ax5.bar(range(len(cluster_names)), conversion_rates,
                color=['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c', '#e67e22'],
                alpha=0.7, edgecolor='black')

for bar, val in zip(bars5, conversion_rates):
    height = bar.get_height()
    ax5.text(bar.get_x() + bar.get_width()/2, height + 0.005,
            f'{val:.3f}%',
            ha='center', va='bottom', fontsize=9)

ax5.set_xticks(range(len(cluster_names)))
ax5.set_xticklabels(cluster_names, rotation=45, ha='right')
ax5.set_ylabel('成交率 (%)', fontsize=12, fontweight='bold')
ax5.set_title('聚類 1: 各聚類成交率比較', fontsize=14, fontweight='bold', pad=20)
ax5.grid(axis='y', alpha=0.3, linestyle='--')

# 子圖 6: 平均訂單價值
avg_values = clusters['avg_order_value'].values / 10000  # 轉為萬元

bars6 = ax6.bar(range(len(cluster_names)), avg_values,
                color=['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c', '#e67e22'],
                alpha=0.7, edgecolor='black')

for bar, val in zip(bars6, avg_values):
    height = bar.get_height()
    if height > 0:
        ax6.text(bar.get_x() + bar.get_width()/2, height + 3,
                f'{val:.1f}萬',
                ha='center', va='bottom', fontsize=9)

ax6.set_xticks(range(len(cluster_names)))
ax6.set_xticklabels(cluster_names, rotation=45, ha='right')
ax6.set_ylabel('平均訂單金額（萬元）', fontsize=12, fontweight='bold')
ax6.set_title('聚類 2: 各聚類平均訂單價值', fontsize=14, fontweight='bold', pad=20)
ax6.grid(axis='y', alpha=0.3, linestyle='--')

# 子圖 7: 潛力分數排名
potential_scores = clusters['potential_score'].values

bars7 = ax7.barh(range(len(cluster_names)), potential_scores,
                 color=['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c', '#e67e22'],
                 alpha=0.7, edgecolor='black')

for bar, val in zip(bars7, potential_scores):
    width = bar.get_width()
    ax7.text(width + 0.02, bar.get_y() + bar.get_height()/2,
            f'{val:.3f}',
            ha='left', va='center', fontsize=9)

ax7.set_yticks(range(len(cluster_names)))
ax7.set_yticklabels(cluster_names)
ax7.set_xlabel('潛力分數', fontsize=12, fontweight='bold')
ax7.set_title('聚類 3: 開發潛力分數（高產值x低開發度）', fontsize=14, fontweight='bold', pad=20)
ax7.grid(axis='x', alpha=0.3, linestyle='--')

# 子圖 8: 公司數分布（餅圖）
totals = clusters['total'].values
colors_pie = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c', '#e67e22']

wedges, texts, autotexts = ax8.pie(totals, labels=cluster_names, autopct='%1.1f%%',
                                     colors=colors_pie, startangle=90,
                                     textprops={'fontsize': 10})

# 美化百分比文字
for autotext in autotexts:
    autotext.set_color('white')
    autotext.set_fontweight('bold')

ax8.set_title('聚類 4: 公司數分布比例', fontsize=14, fontweight='bold', pad=20)

plt.tight_layout()
plt.savefig(OUTPUT_DIR / '聚類分析視覺化.png', dpi=300, bbox_inches='tight')
print(f"圖表 2 已儲存: {OUTPUT_DIR / '聚類分析視覺化.png'}")

# ============ 圖表 3: 執行時間表 ============
fig3, ax9 = plt.subplots(figsize=(14, 8))

# 策略執行時間表數據
timeline_data = [
    {'策略': '再購喚醒', '開始': 0, '長度': 1, '優先': 'P0', '成交': 305, '營收': 6.41},
    {'策略': 'Output3跟進', '開始': 0, '長度': 1, '優先': 'P0', '成交': 22, '營收': 0.39},
    {'策略': '快速成交複製', '開始': 1, '長度': 2, '優先': 'P1', '成交': 115, '營收': 2.04},
    {'策略': '痛點深耕Top20', '開始': 2, '長度': 2, '優先': 'P1', '成交': 3000, '營收': 53.0},
    {'策略': 'C1藍海開發', '開始': 4, '長度': 2, '優先': 'P2', '成交': 710, '營收': 136.7},
    {'策略': '痛點深耕全面', '開始': 4, '長度': 2, '優先': 'P2', '成交': 12420, '營收': 220.17},
    {'策略': 'Look-alike', '開始': 7, '長度': 5, '優先': 'P3', '成交': 8000, '營收': 141.7},
    {'策略': 'C0微型開發', '開始': 7, '長度': 5, '優先': 'P3', '成交': 2000, '營收': 17.5},
]

priority_colors = {'P0': '#e74c3c', 'P1': '#f39c12', 'P2': '#3498db', 'P3': '#9b59b6'}

for i, data in enumerate(timeline_data):
    color = priority_colors[data['優先']]
    ax9.barh(i, data['長度'], left=data['開始'],
             color=color, alpha=0.7, edgecolor='black', linewidth=1.5)

    # 標註策略名稱和成果
    mid_point = data['開始'] + data['長度'] / 2
    ax9.text(mid_point, i, f"{data['策略']}\n{data['成交']:,}家/{data['營收']:.1f}億",
            ha='center', va='center', fontsize=9, fontweight='bold', color='white')

ax9.set_yticks(range(len(timeline_data)))
ax9.set_yticklabels([d['優先'] + ': ' + d['策略'] for d in timeline_data])
ax9.set_xlabel('執行時間（月）', fontsize=12, fontweight='bold')
ax9.set_title('12 個月執行時間表與預期成果', fontsize=16, fontweight='bold', pad=20)
ax9.set_xlim(0, 12)
ax9.set_xticks(range(13))
ax9.grid(axis='x', alpha=0.3, linestyle='--')

# 添加圖例
from matplotlib.patches import Patch
legend_elements = [
    Patch(facecolor='#e74c3c', label='P0: 立即執行（0-1月）'),
    Patch(facecolor='#f39c12', label='P1: 短期（1-3月）'),
    Patch(facecolor='#3498db', label='P2: 中期（3-6月）'),
    Patch(facecolor='#9b59b6', label='P3: 長期（6-12月）')
]
ax9.legend(handles=legend_elements, loc='upper right', fontsize=10)

plt.tight_layout()
plt.savefig(OUTPUT_DIR / '執行時間表.png', dpi=300, bbox_inches='tight')
print(f"圖表 3 已儲存: {OUTPUT_DIR / '執行時間表.png'}")

print("\n所有視覺化圖表生成完成！")
print(f"儲存位置: {OUTPUT_DIR}")

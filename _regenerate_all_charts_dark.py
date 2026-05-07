# -*- coding: utf-8 -*-
"""
重新生成所有图表 - 统一黑底样式
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import matplotlib.patheffects
matplotlib.rcParams['font.sans-serif'] = ['Microsoft JhengHei', 'Arial Unicode MS']
matplotlib.rcParams['axes.unicode_minus'] = False

# 讀取分類統計
df = pd.read_csv('痛點分類結果_Final/分類統計.csv')
df_heatmap = pd.read_csv('痛點分類結果_Final/pain_heatmap_完整分類.csv')
total = df['count'].sum()

# 計算百分比
df['percentage'] = df['count'] / total * 100
df = df.sort_values('count', ascending=False)

# 設定顏色
colors = [
    '#5DADE2', '#F9E79F', '#BB8FCE', '#F1948A', '#85C1E2', '#FAD7A0',
    '#D7BDE2', '#ABEBC6', '#D7A9E3', '#F8C471', '#AED6F1', '#A3E4D7'
]

print("=" * 60)
print("開始生成黑底版本的圖表")
print("=" * 60)

# ===== 1. 圓餅圖（黑底） =====
print("\n[1/3] 生成圓餅圖...")
fig, ax = plt.subplots(figsize=(16, 13), facecolor='#0f1117')
ax.set_facecolor('#0f1117')

wedges, texts = ax.pie(
    df['count'],
    colors=colors[:len(df)],
    startangle=90,
    wedgeprops={'linewidth': 2, 'edgecolor': '#1a1f2e'},
    radius=1.0
)

# 計算標籤位置
label_positions = []
for i, (wedge, row) in enumerate(zip(wedges, df.itertuples())):
    angle = (wedge.theta2 + wedge.theta1) / 2
    x_edge = 1.0 * np.cos(np.radians(angle))
    y_edge = 1.0 * np.sin(np.radians(angle))

    if row.percentage < 2:
        label_dist = 1.6
    elif row.percentage < 4:
        label_dist = 1.5
    else:
        label_dist = 1.35

    x_label = label_dist * np.cos(np.radians(angle))
    y_label = label_dist * np.sin(np.radians(angle))

    label_positions.append({
        'angle': angle,
        'x_edge': x_edge,
        'y_edge': y_edge,
        'x_label': x_label,
        'y_label': y_label,
        'text': f"{row.category_name}：{row.percentage:.1f}%",
        'percentage': row.percentage
    })

# 多輪調整避免重疊
min_vertical_distance = 0.18
for iteration in range(10):
    has_overlap = False
    for side in ['left', 'right']:
        side_labels = [(i, pos) for i, pos in enumerate(label_positions)
                      if (side == 'left' and pos['x_label'] < 0) or
                         (side == 'right' and pos['x_label'] >= 0)]
        side_labels.sort(key=lambda x: -x[1]['y_label'])

        for i in range(len(side_labels) - 1):
            idx1, pos1 = side_labels[i]
            idx2, pos2 = side_labels[i + 1]
            dy = pos1['y_label'] - pos2['y_label']

            if dy < min_vertical_distance:
                has_overlap = True
                shift = min_vertical_distance - dy
                label_positions[idx2]['y_label'] -= shift
                dist = np.sqrt(label_positions[idx2]['x_label']**2 +
                              label_positions[idx2]['y_label']**2)
                new_angle = np.arctan2(label_positions[idx2]['y_label'],
                                      label_positions[idx2]['x_label'])
                label_positions[idx2]['x_label'] = dist * np.cos(new_angle)

    if not has_overlap:
        break

# 繪製連接線和標籤
for i, pos in enumerate(label_positions):
    ax.plot([pos['x_edge'], pos['x_label']],
            [pos['y_edge'], pos['y_label']],
            color='#94a3b8', linewidth=0.8, alpha=0.8)

    ha = 'left' if pos['x_label'] > 0 else 'right'
    ax.text(pos['x_label'], pos['y_label'], pos['text'],
            ha=ha, va='center',
            fontsize=11.5,
            fontweight='bold',
            color='#e2e8f0')

ax.set_title(f'痛點類別分布（總計 {total:,} 筆）\n無「其他」類別',
             fontsize=18, fontweight='bold', pad=25, color='#7dd3fc')

fig.text(0.5, 0.05, '圓餅圖例',
         ha='center', fontsize=13, fontweight='bold', color='#94a3b8')

ax.axis('equal')
plt.tight_layout()

output_path = '痛點分類結果_Final/痛點類別分布_dark.png'
plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='#0f1117', pad_inches=0.4)
print(f"   [OK] 已儲存: {output_path}")
plt.close()

# ===== 2. 痛需熱圖（黑底） =====
print("\n[2/3] 生成痛需熱圖...")

# 創建 pivot 表
heatmap_pivot = df_heatmap.pivot(index='category_name', columns='cluster_name', values='heat_score')
heatmap_pivot = heatmap_pivot.fillna(0)

fig, ax = plt.subplots(figsize=(14, 10), facecolor='#0f1117')
ax.set_facecolor('#0f1117')

im = ax.imshow(heatmap_pivot.values, cmap='YlOrRd', aspect='auto')

ax.set_xticks(np.arange(len(heatmap_pivot.columns)))
ax.set_yticks(np.arange(len(heatmap_pivot.index)))
ax.set_xticklabels(heatmap_pivot.columns, color='#e2e8f0', fontsize=11)
ax.set_yticklabels(heatmap_pivot.index, color='#e2e8f0', fontsize=11)

plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

for i in range(len(heatmap_pivot.index)):
    for j in range(len(heatmap_pivot.columns)):
        value = heatmap_pivot.values[i, j]
        # 所有数字统一使用黑色
        text = ax.text(j, i, f'{value:.2f}',
                      ha="center", va="center",
                      color='black',
                      fontsize=10, fontweight='bold')

ax.set_title('痛需熱圖：法人類型 × 痛點類別（12類別）\n熱度分數（heat_score）',
             fontsize=16, fontweight='bold', pad=20, color='#7dd3fc')

ax.set_xlabel('法人聚類（C0-C6）', fontsize=12, color='#94a3b8', labelpad=10)
ax.set_ylabel('痛點類別', fontsize=12, color='#94a3b8', labelpad=10)

cbar = plt.colorbar(im, ax=ax)
cbar.set_label('熱度分數', rotation=270, labelpad=20, color='#94a3b8', fontsize=11)
cbar.ax.tick_params(colors='#e2e8f0')

ax.spines['top'].set_color('#2d4a7a')
ax.spines['bottom'].set_color('#2d4a7a')
ax.spines['left'].set_color('#2d4a7a')
ax.spines['right'].set_color('#2d4a7a')

plt.tight_layout()

output_path = '痛點分類結果_Final/最終痛需熱圖_dark.png'
plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='#0f1117')
print(f"   [OK] 已儲存: {output_path}")
plt.close()

# ===== 3. 統計圖表（黑底） =====
print("\n[3/3] 生成統計圖表...")

fig = plt.figure(figsize=(16, 10), facecolor='#0f1117')
gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)

# 子圖1: 類別數量柱狀圖
ax1 = fig.add_subplot(gs[0, 0])
ax1.set_facecolor('#1a1f2e')
bars1 = ax1.barh(df['category_name'], df['count'], color=colors[:len(df)])
ax1.set_xlabel('記錄數', fontsize=11, color='#94a3b8')
ax1.set_title('各類別記錄數', fontsize=13, fontweight='bold', color='#7dd3fc')
ax1.tick_params(colors='#e2e8f0')
for spine in ax1.spines.values():
    spine.set_color('#2d4a7a')

# 子圖2: 百分比柱狀圖
ax2 = fig.add_subplot(gs[0, 1])
ax2.set_facecolor('#1a1f2e')
bars2 = ax2.barh(df['category_name'], df['percentage'], color=colors[:len(df)])
ax2.set_xlabel('百分比 (%)', fontsize=11, color='#94a3b8')
ax2.set_title('各類別佔比', fontsize=13, fontweight='bold', color='#7dd3fc')
ax2.tick_params(colors='#e2e8f0')
for spine in ax2.spines.values():
    spine.set_color('#2d4a7a')

# 子圖3: 公司數量統計
ax3 = fig.add_subplot(gs[1, 0])
ax3.set_facecolor('#1a1f2e')
category_companies = df_heatmap.groupby('category_name')['company_count'].sum().sort_values(ascending=False)
bars3 = ax3.bar(range(len(category_companies)), category_companies.values, color=colors[:len(category_companies)])
ax3.set_xticks(range(len(category_companies)))
ax3.set_xticklabels(category_companies.index, rotation=45, ha='right', fontsize=9, color='#e2e8f0')
ax3.set_ylabel('公司數', fontsize=11, color='#94a3b8')
ax3.set_title('各類別涉及公司數', fontsize=13, fontweight='bold', color='#7dd3fc')
ax3.tick_params(colors='#e2e8f0')
for spine in ax3.spines.values():
    spine.set_color('#2d4a7a')

# 子圖4: 平均熱度分數
ax4 = fig.add_subplot(gs[1, 1])
ax4.set_facecolor('#1a1f2e')
avg_heat = df_heatmap.groupby('category_name')['heat_score'].mean().sort_values(ascending=False)
bars4 = ax4.bar(range(len(avg_heat)), avg_heat.values, color=colors[:len(avg_heat)])
ax4.set_xticks(range(len(avg_heat)))
ax4.set_xticklabels(avg_heat.index, rotation=45, ha='right', fontsize=9, color='#e2e8f0')
ax4.set_ylabel('平均熱度', fontsize=11, color='#94a3b8')
ax4.set_title('各類別平均熱度分數', fontsize=13, fontweight='bold', color='#7dd3fc')
ax4.tick_params(colors='#e2e8f0')
for spine in ax4.spines.values():
    spine.set_color('#2d4a7a')

fig.suptitle('痛點類別完整統計（4維度分析）',
             fontsize=18, fontweight='bold', color='#7dd3fc', y=0.98)

plt.tight_layout()

output_path = '痛點分類結果_Final/痛點類別完整統計_dark.png'
plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='#0f1117')
print(f"   [OK] 已儲存: {output_path}")
plt.close()

print("\n" + "=" * 60)
print("所有圖表已生成完畢（黑底版本）")
print("=" * 60)

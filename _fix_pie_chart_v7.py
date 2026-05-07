# -*- coding: utf-8 -*-
"""
重新生成痛點類別分布圓餅圖 - 优化标签位置避免重叠
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.rcParams['font.sans-serif'] = ['Microsoft JhengHei', 'Arial Unicode MS']
matplotlib.rcParams['axes.unicode_minus'] = False

# 讀取分類統計
df = pd.read_csv('痛點分類結果_Final/分類統計.csv')
total = df['count'].sum()

# 計算百分比
df['percentage'] = df['count'] / total * 100

# 按照數量排序
df = df.sort_values('count', ascending=False)

# 設定顏色
colors = [
    '#5DADE2',  # 藍色 - 溝通聯繫障礙
    '#F9E79F',  # 黃色 - 現有系統相關
    '#BB8FCE',  # 紫色 - 需求不明確/不符
    '#F1948A',  # 紅色 - 預算資源限制
    '#85C1E2',  # 淺藍 - 技術系統問題
    '#FAD7A0',  # 橙色 - 客戶態度消極
    '#D7BDE2',  # 粉紫 - 資訊不足/不透明
    '#ABEBC6',  # 綠色 - 流程效率問題
    '#D7A9E3',  # 紫紅 - 公司狀態異常
    '#F8C471',  # 金黃 - ERP系統相關
    '#AED6F1',  # 天藍 - 資安合規問題
    '#A3E4D7',  # 薄荷綠 - 服務品質問題
]

# 創建圖表
fig, ax = plt.subplots(figsize=(16, 12))

# 繪製圓餅圖 - 不帶標籤
wedges, texts = ax.pie(
    df['count'],
    colors=colors[:len(df)],
    startangle=90,
    wedgeprops={'linewidth': 2, 'edgecolor': 'white'},
    radius=1.0
)

# 手動優化標籤位置
# 計算每個楔形的角度和初始位置
label_positions = []
for i, (wedge, row) in enumerate(zip(wedges, df.itertuples())):
    angle = (wedge.theta2 + wedge.theta1) / 2

    # 楔形邊緣的點
    x_edge = 1.0 * np.cos(np.radians(angle))
    y_edge = 1.0 * np.sin(np.radians(angle))

    # 初始標籤位置
    if row.percentage < 3:  # 小片區標籤放更遠
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

# 優化標籤位置：檢測並調整重叠的標籤
min_distance = 0.15  # 最小垂直距離

# 按 y 坐標排序，從上到下調整
sorted_by_y = sorted(enumerate(label_positions), key=lambda x: -x[1]['y_label'])

for i in range(len(sorted_by_y) - 1):
    idx_current, pos_current = sorted_by_y[i]
    idx_next, pos_next = sorted_by_y[i + 1]

    # 計算距離
    dy = pos_current['y_label'] - pos_next['y_label']

    # 如果太近，調整下方的標籤
    if dy < min_distance and abs(pos_current['x_label'] - pos_next['x_label']) < 0.5:
        # 向下移動下方標籤
        shift = min_distance - dy
        label_positions[idx_next]['y_label'] -= shift

# 繪製連接線和標籤
for i, pos in enumerate(label_positions):
    # 繪製連接線
    ax.plot([pos['x_edge'], pos['x_label']],
            [pos['y_edge'], pos['y_label']],
            'k-', linewidth=0.8, alpha=0.7)

    # 根據位置決定對齊方式
    if pos['x_label'] > 0:
        ha = 'left'
    else:
        ha = 'right'

    # 添加標籤
    ax.text(pos['x_label'], pos['y_label'], pos['text'],
            ha=ha, va='center',
            fontsize=11.5,
            fontweight='bold')

# 標題
ax.set_title(f'痛點類別分布（總計 {total:,} 筆）\n無「其他」類別',
             fontsize=18, fontweight='bold', pad=25)

# 底部文字
fig.text(0.5, 0.06, '圓餅圖例',
         ha='center', fontsize=13, fontweight='bold')

# 保持圓形
ax.axis('equal')

# 調整佈局
plt.tight_layout()

# 儲存
output_path = '痛點分類結果_Final/痛點類別分布_v7.png'
plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white', pad_inches=0.3)
print(f"[OK] 圓餅圖已儲存至: {output_path}")
print(f"[INFO] 已優化標籤位置，避免重疊")
print(f"[INFO] 小片區標籤放置更遠，連接線更長")

plt.close()

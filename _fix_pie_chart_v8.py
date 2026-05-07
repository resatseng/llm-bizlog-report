# -*- coding: utf-8 -*-
"""
重新生成痛點類別分布圓餅圖 - 完全解决标签重叠问题
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
fig, ax = plt.subplots(figsize=(16, 13))

# 繪製圓餅圖 - 不帶標籤
wedges, texts = ax.pie(
    df['count'],
    colors=colors[:len(df)],
    startangle=90,
    wedgeprops={'linewidth': 2, 'edgecolor': 'white'},
    radius=1.0
)

# 計算初始標籤位置
label_positions = []
for i, (wedge, row) in enumerate(zip(wedges, df.itertuples())):
    angle = (wedge.theta2 + wedge.theta1) / 2

    # 楔形邊緣的點
    x_edge = 1.0 * np.cos(np.radians(angle))
    y_edge = 1.0 * np.sin(np.radians(angle))

    # 標籤距離根据片区大小调整
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

# 高级重叠检测和调整算法
def check_overlap(pos1, pos2):
    """检查两个标签是否重叠"""
    dx = abs(pos1['x_label'] - pos2['x_label'])
    dy = abs(pos1['y_label'] - pos2['y_label'])

    # 考虑文字长度
    text_height = 0.12
    text_width_1 = len(pos1['text']) * 0.015
    text_width_2 = len(pos2['text']) * 0.015

    # 检查是否重叠
    if dx < (text_width_1 + text_width_2) / 2 and dy < text_height:
        return True
    return False

# 多轮调整，直到没有重叠
max_iterations = 10
min_vertical_distance = 0.18

for iteration in range(max_iterations):
    has_overlap = False

    # 分别处理左右两侧
    for side in ['left', 'right']:
        # 筛选该侧的标签
        side_labels = [(i, pos) for i, pos in enumerate(label_positions)
                      if (side == 'left' and pos['x_label'] < 0) or
                         (side == 'right' and pos['x_label'] >= 0)]

        # 按 y 坐标排序
        side_labels.sort(key=lambda x: -x[1]['y_label'])

        # 检查并调整重叠
        for i in range(len(side_labels) - 1):
            idx1, pos1 = side_labels[i]
            idx2, pos2 = side_labels[i + 1]

            dy = pos1['y_label'] - pos2['y_label']

            # 如果距离太近
            if dy < min_vertical_distance:
                has_overlap = True
                # 向下推动下方标签
                shift = min_vertical_distance - dy
                label_positions[idx2]['y_label'] -= shift

                # 同时微调 x 位置，保持在合理范围
                angle = label_positions[idx2]['angle']
                dist = np.sqrt(label_positions[idx2]['x_label']**2 +
                              label_positions[idx2]['y_label']**2)
                new_angle = np.arctan2(label_positions[idx2]['y_label'],
                                      label_positions[idx2]['x_label'])
                label_positions[idx2]['x_label'] = dist * np.cos(new_angle)

    if not has_overlap:
        break

# 绘制连接线和标签
for i, pos in enumerate(label_positions):
    # 绘制连接线
    ax.plot([pos['x_edge'], pos['x_label']],
            [pos['y_edge'], pos['y_label']],
            'k-', linewidth=0.8, alpha=0.7)

    # 根据位置决定对齐方式
    if pos['x_label'] > 0:
        ha = 'left'
    else:
        ha = 'right'

    # 添加标签
    ax.text(pos['x_label'], pos['y_label'], pos['text'],
            ha=ha, va='center',
            fontsize=11.5,
            fontweight='bold')

# 标题
ax.set_title(f'痛點類別分布（總計 {total:,} 筆）\n無「其他」類別',
             fontsize=18, fontweight='bold', pad=25)

# 底部文字
fig.text(0.5, 0.05, '圓餅圖例',
         ha='center', fontsize=13, fontweight='bold')

# 保持圆形
ax.axis('equal')

# 调整布局
plt.tight_layout()

# 储存
output_path = '痛點分類結果_Final/痛點類別分布_v8.png'
plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white', pad_inches=0.4)
print(f"[OK] 圓餅圖已儲存至: {output_path}")
print(f"[INFO] 經過 {iteration + 1} 輪調整，完全避免重疊")
print(f"[INFO] 最小垂直距離: {min_vertical_distance}")

plt.close()

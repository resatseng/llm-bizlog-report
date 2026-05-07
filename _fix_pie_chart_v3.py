# -*- coding: utf-8 -*-
"""
重新生成痛點類別分布圓餅圖 - 外部标签样式
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

# 為小片區設定 explode
explode = []
for pct in df['percentage']:
    if pct < 3:
        explode.append(0.1)
    else:
        explode.append(0)

# 準備標籤（類別名 + 百分比）
labels = []
for idx, row in df.iterrows():
    labels.append(f"{row['category_name']}\n{row['percentage']:.1f}%")

# 創建圖表
fig, ax = plt.subplots(figsize=(14, 10))

# 繪製圓餅圖，使用外部標籤
wedges, texts, autotexts = ax.pie(
    df['count'],
    labels=labels,
    autopct='',  # 不在饼图内显示百分比
    colors=colors[:len(df)],
    explode=explode,
    startangle=90,
    textprops={'fontsize': 11, 'fontweight': 'bold'},
    pctdistance=0.85,
    labeldistance=1.15  # 标签距离圆心的距离
)

# 调整标签连接线样式
for text in texts:
    text.set_fontsize(11)
    text.set_fontweight('bold')

# 在每个楔形上添加数量信息（仅大片区）
for i, (wedge, row) in enumerate(zip(wedges, df.itertuples())):
    pct = row.percentage
    if pct >= 5:  # 只在大片区显示数量
        angle = (wedge.theta2 - wedge.theta1) / 2. + wedge.theta1
        x = wedge.r * 0.6 * np.cos(np.radians(angle))
        y = wedge.r * 0.6 * np.sin(np.radians(angle))
        ax.text(x, y, f'{row.count:,}筆',
                ha='center', va='center',
                fontsize=10,
                color='white' if pct > 15 else 'black',
                bbox=dict(boxstyle='round,pad=0.3',
                         facecolor='black' if pct > 15 else 'white',
                         alpha=0.3,
                         edgecolor='none'))

# 標題
plt.title(f'痛點類別分布（總計 {total:,} 筆）\n無「其他」類別',
          fontsize=18, fontweight='bold', pad=20)

# 保持圓形
ax.axis('equal')

# 調整佈局
plt.tight_layout()

# 儲存
output_path = '痛點分類結果_Final/痛點類別分布_v3.png'
plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
print(f"[OK] 圓餅圖已儲存至: {output_path}")
print(f"[INFO] 採用外部標籤樣式（類別名 + 百分比）")
print(f"[INFO] 大片區內顯示數量資訊")

plt.close()

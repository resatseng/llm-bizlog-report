# -*- coding: utf-8 -*-
"""
重新生成痛點類別分布圓餅圖，修正文字重疊問題
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

# 為小片區設定 explode（稍微分離）以避免重疊
explode = []
for pct in df['percentage']:
    if pct < 3:
        explode.append(0.1)  # 小於3%的片區稍微分離
    else:
        explode.append(0)

# 創建大圖
fig, ax = plt.subplots(figsize=(16, 12))

# 繪製圓餅圖
wedges, texts, autotexts = ax.pie(
    df['count'],
    labels=None,  # 不在餅圖上直接標註
    autopct='',  # 先不顯示百分比
    colors=colors[:len(df)],
    explode=explode,
    startangle=90,
    pctdistance=0.85
)

# 手動添加標籤，避免重疊
# 使用 legend 顯示類別名稱、百分比和詳細資訊
legend_labels = []
for idx, row in df.iterrows():
    label = f"{row['category_name']} ({row['percentage']:.1f}%)\n{row['count']:,}筆"
    legend_labels.append(label)

# 在每個片區上只顯示百分比（僅顯示 >= 3% 的）
for i, (wedge, autotext, row) in enumerate(zip(wedges, autotexts, df.itertuples())):
    pct = row.percentage
    if pct >= 3:  # 只顯示 >= 3% 的百分比，避免小片區擁擠
        angle = (wedge.theta2 - wedge.theta1) / 2. + wedge.theta1
        x = wedge.r * 0.7 * np.cos(np.radians(angle))
        y = wedge.r * 0.7 * np.sin(np.radians(angle))
        ax.text(x, y, f'{pct:.1f}%',
                ha='center', va='center',
                fontsize=14, fontweight='bold',
                color='white' if pct > 15 else 'black')

# 添加圖例（放在右側）
ax.legend(wedges, legend_labels,
          title="痛點類別",
          loc="center left",
          bbox_to_anchor=(1, 0, 0.5, 1),
          fontsize=11,
          title_fontsize=13)

# 標題
plt.title(f'痛點類別分布（總計 {total:,} 筆）\n無「其他」類別',
          fontsize=18, fontweight='bold', pad=20)

# 保持圓形
ax.axis('equal')

# 調整佈局
plt.tight_layout()

# 儲存
output_path = '痛點分類結果_Final/痛點類別分布圓餅圖.png'
plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
print(f"[OK] 圓餅圖已儲存至: {output_path}")

plt.close()

# -*- coding: utf-8 -*-
"""
重新生成痛點類別分布圓餅圖 - 完全按照參考圖樣式
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import ConnectionPatch
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
fig, ax = plt.subplots(figsize=(14, 11))

# 繪製圓餅圖 - 不帶標籤
wedges, texts = ax.pie(
    df['count'],
    colors=colors[:len(df)],
    startangle=90,
    wedgeprops={'linewidth': 1.5, 'edgecolor': 'white'},
    radius=1.0
)

# 手動添加標籤和連接線
# 為每個楔形計算角度和位置
for i, (wedge, row) in enumerate(zip(wedges, df.itertuples())):
    # 計算楔形中點角度
    angle = (wedge.theta2 + wedge.theta1) / 2

    # 楔形邊緣的點（連接線起點）
    x1 = 1.0 * np.cos(np.radians(angle))
    y1 = 1.0 * np.sin(np.radians(angle))

    # 標籤位置（連接線終點）
    # 根據角度決定標籤距離
    label_distance = 1.35
    x2 = label_distance * np.cos(np.radians(angle))
    y2 = label_distance * np.sin(np.radians(angle))

    # 繪製連接線
    ax.plot([x1, x2], [y1, y2], 'k-', linewidth=0.8, alpha=0.6)

    # 添加標籤文字
    # 根據位置決定對齊方式
    if x2 > 0:
        ha = 'left'
    else:
        ha = 'right'

    label_text = f"{row.category_name}：{row.percentage:.1f}%"

    ax.text(x2, y2, label_text,
            ha=ha, va='center',
            fontsize=11,
            fontweight='bold')

# 標題
ax.set_title(f'痛點類別分布（總計 {total:,} 筆）\n無「其他」類別',
             fontsize=16, fontweight='bold', pad=20)

# 底部文字
fig.text(0.5, 0.05, '圓餅圖例',
         ha='center', fontsize=12, fontweight='bold')

# 保持圓形
ax.axis('equal')

# 設置軸範圍以確保所有標籤可見
ax.set_xlim(-1.8, 1.8)
ax.set_ylim(-1.8, 1.8)

# 調整佈局
plt.tight_layout()

# 儲存
output_path = '痛點分類結果_Final/痛點類別分布_v6.png'
plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
print(f"[OK] 圓餅圖已儲存至: {output_path}")
print(f"[INFO] 採用參考圖樣式：手動繪製連接線和標籤")

plt.close()

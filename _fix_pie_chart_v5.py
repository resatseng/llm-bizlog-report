# -*- coding: utf-8 -*-
"""
重新生成痛點類別分布圓餅圖 - 参考样式，避免文字重叠
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
        explode.append(0.05)  # 减小 explode，让饼图更紧凑
    else:
        explode.append(0)

# 準備標籤（類別名：百分比）
labels = []
for idx, row in df.iterrows():
    labels.append(f"{row['category_name']}：{row['percentage']:.1f}%")

# 創建圖表 - 增大图表尺寸以容纳标签
fig, ax = plt.subplots(figsize=(16, 16))

# 繪製圓餅圖
wedges, texts = ax.pie(
    df['count'],
    labels=labels,
    colors=colors[:len(df)],
    explode=explode,
    startangle=90,
    labeldistance=1.2,  # 标签距离
    textprops={
        'fontsize': 13,
        'fontweight': 'bold'
    },
    wedgeprops={'linewidth': 1, 'edgecolor': 'white'}  # 添加白色边框
)

# 手动调整部分标签位置以避免重叠
# matplotlib 会自动尝试避免重叠，但我们可以进一步优化
for i, text in enumerate(texts):
    # 获取当前位置
    x, y = text.get_position()

    # 对于y坐标接近的标签，进行微调
    if abs(y) < 0.3:  # 接近水平中线的标签
        # 稍微向外移动
        angle = np.arctan2(y, x)
        r = 1.25
        text.set_position((r * np.cos(angle), r * np.sin(angle)))

# 標題
ax.set_title(f'痛點類別分布（總計 {total:,} 筆）\n無「其他」類別',
             fontsize=18, fontweight='bold', pad=30)

# 在底部添加"圓餅圖例"文字
fig.text(0.5, 0.08, '圓餅圖例',
         ha='center', fontsize=14, fontweight='bold')

# 保持圓形
ax.axis('equal')

# 調整佈局，留出更多空白
plt.tight_layout(pad=3.0)

# 儲存
output_path = '痛點分類結果_Final/痛點類別分布_v5.png'
plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white', pad_inches=0.5)
print(f"[OK] 圓餅圖已儲存至: {output_path}")
print(f"[INFO] 採用外部標籤樣式，自動避免重疊")
print(f"[INFO] 標籤格式：類別名：百分比")

plt.close()

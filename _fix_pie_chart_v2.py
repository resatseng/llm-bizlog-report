# -*- coding: utf-8 -*-
"""
重新生成痛點類別分布圓餅圖 - 完全解決文字重疊
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

# 為小片區設定 explode（稍微分離）
explode = []
for pct in df['percentage']:
    if pct < 3:
        explode.append(0.15)  # 小於3%的片區分離
    else:
        explode.append(0)

# 創建圖表
fig, ax = plt.subplots(figsize=(18, 12))

# 自定義百分比顯示函數 - 只顯示大於3%的
def autopct_format(pct):
    return f'{pct:.1f}%' if pct >= 3 else ''

# 繪製圓餅圖 - 關鍵：不使用 labels 參數
wedges, texts, autotexts = ax.pie(
    df['count'],
    autopct=autopct_format,
    colors=colors[:len(df)],
    explode=explode,
    startangle=90,
    pctdistance=0.75,
    textprops={'fontsize': 15, 'fontweight': 'bold', 'color': 'black'}
)

# 設定百分比文字顏色（大片區用白色）
for i, (autotext, row) in enumerate(zip(autotexts, df.itertuples())):
    if row.percentage > 15:
        autotext.set_color('white')

# 準備圖例標籤
legend_labels = []
for idx, row in df.iterrows():
    label = f"{row['category_name']} ({row['percentage']:.1f}%) - {row['count']:,}筆"
    legend_labels.append(label)

# 添加圖例（放在右側，垂直排列）
ax.legend(wedges, legend_labels,
          title="痛點類別詳細資訊",
          loc="center left",
          bbox_to_anchor=(1.05, 0.5),
          fontsize=12,
          title_fontsize=14,
          frameon=True,
          fancybox=True,
          shadow=True)

# 標題
plt.title(f'痛點類別分布（總計 {total:,} 筆）\n無「其他」類別',
          fontsize=20, fontweight='bold', pad=25)

# 保持圓形
ax.axis('equal')

# 調整佈局
plt.tight_layout()

# 儲存
output_path = '痛點分類結果_Final/痛點類別分布圓餅圖.png'
plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
print(f"[OK] 圓餅圖已儲存至: {output_path}")
print(f"[INFO] 圖表尺寸: 18x12, DPI: 150")
print(f"[INFO] 餅圖上僅顯示 >= 3% 的百分比")
print(f"[INFO] 所有類別詳細資訊顯示在右側圖例")

plt.close()

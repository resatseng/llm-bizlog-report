# -*- coding: utf-8 -*-
"""
重新生成痛點類別分布圓餅圖 - 附带详细信息表格
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

# 創建圖表 - 使用子图布局
fig = plt.figure(figsize=(18, 10))
gs = fig.add_gridspec(1, 2, width_ratios=[2, 1], wspace=0.3)

# 左側：圓餅圖
ax_pie = fig.add_subplot(gs[0])

wedges, texts, autotexts = ax_pie.pie(
    df['count'],
    labels=labels,
    autopct='',
    colors=colors[:len(df)],
    explode=explode,
    startangle=90,
    textprops={'fontsize': 11, 'fontweight': 'bold'},
    pctdistance=0.85,
    labeldistance=1.15
)

ax_pie.set_title(f'痛點類別分布（總計 {total:,} 筆）\n無「其他」類別',
                 fontsize=18, fontweight='bold', pad=20)

# 右側：詳細信息表格
ax_table = fig.add_subplot(gs[1])
ax_table.axis('off')

# 準備表格數據
table_data = []
table_data.append(['排名', '類別', '百分比', '筆數'])  # 表頭

for i, row in enumerate(df.itertuples(), 1):
    table_data.append([
        f'{i}',
        row.category_name,
        f'{row.percentage:.1f}%',
        f'{row.count:,}'
    ])

# 創建表格
table = ax_table.table(
    cellText=table_data,
    cellLoc='left',
    loc='center',
    bbox=[0, 0, 1, 1]
)

# 設定表格樣式
table.auto_set_font_size(False)
table.set_fontsize(11)

# 設定表頭樣式
for i in range(4):
    cell = table[(0, i)]
    cell.set_facecolor('#4A90E2')
    cell.set_text_props(weight='bold', color='white', fontsize=12)
    cell.set_height(0.06)

# 設定數據行樣式
for i in range(1, len(table_data)):
    # 顏色標記
    color_cell = table[(i, 0)]
    color_cell.set_facecolor(colors[i-1])
    color_cell.set_alpha(0.7)

    # 其他單元格
    for j in range(4):
        cell = table[(i, j)]
        if i % 2 == 0:
            cell.set_facecolor('#F5F5F5')
        cell.set_height(0.055)

        # 設定對齊方式
        if j == 1:  # 類別名稱左對齊
            cell.set_text_props(ha='left')
        else:  # 其他居中
            cell.set_text_props(ha='center')

# 設定列寬
table.auto_set_column_width([0, 1, 2, 3])
for i in range(len(table_data)):
    table[(i, 0)].set_width(0.12)  # 排名
    table[(i, 1)].set_width(0.50)  # 類別
    table[(i, 2)].set_width(0.18)  # 百分比
    table[(i, 3)].set_width(0.20)  # 筆數

# 添加表格標題
ax_table.text(0.5, 0.98, '詳細統計資訊',
              ha='center', va='top',
              fontsize=14, fontweight='bold',
              transform=ax_table.transAxes)

# 調整佈局
plt.tight_layout()

# 儲存
output_path = '痛點分類結果_Final/痛點類別分布_v4.png'
plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
print(f"[OK] 圓餅圖已儲存至: {output_path}")
print(f"[INFO] 左側：圓餅圖（外部標籤）")
print(f"[INFO] 右側：詳細統計表格")

plt.close()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重新生成全螢幕尺寸的 Sunburst 圖表
"""

import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

# 路徑
OUT = Path("results_timeseries")

print("讀取資料...")
# 讀取現有的 Sunburst 資料（從 CSV 如果有的話）
# 或者直接讀取原始資料重新計算

# 由於完整的 Sunburst 生成邏輯很複雜，我們採用簡化版本
# 讀取 matched_orders.csv
matched_orders = pd.read_csv(OUT / "matched_orders.csv")

# 簡化版：只按 stage 統計
stage_stats = matched_orders.groupby('stage').agg({
    'company_id': 'count'
}).reset_index()
stage_stats.columns = ['stage', 'count']

# 創建簡化的 Sunburst 資料
ids = ['總訂單'] + stage_stats['stage'].tolist()
labels = ['總訂單'] + stage_stats['stage'].tolist()
parents = [''] + ['總訂單'] * len(stage_stats)
values = [stage_stats['count'].sum()] + stage_stats['count'].tolist()

# 顏色
colors = {
    'A': '#e74c3c',  # 紅色
    'B': '#3498db',  # 藍色
    'C1': '#f39c12', # 橙色
    'C2': '#f39c12',
    'D': '#9b59b6',  # 紫色
    'E': '#2ecc71'   # 綠色
}
marker_colors = ['#f0f0f0'] + [colors.get(s, '#95a5a6') for s in stage_stats['stage']]

# 生成 hover text
hover_text = ['總訂單: ' + str(stage_stats['count'].sum())]
for _, row in stage_stats.iterrows():
    hover_text.append(f"{row['stage']}<br>訂單: {row['count']:,}")

# 創建 Sunburst 圖
fig = go.Figure(go.Sunburst(
    ids=ids,
    labels=labels,
    parents=parents,
    values=values,
    hovertext=hover_text,
    hoverinfo='text',
    marker=dict(
        colors=marker_colors,
        line=dict(color='white', width=2)
    ),
    branchvalues='total'
))

# 重點：layout 不設定固定尺寸
fig.update_layout(
    title=dict(
        text="成交路徑樹狀圖（Sunburst）- 前100大路徑",
        font=dict(size=16, family="Microsoft JhengHei"),
        x=0.5,
        xanchor='center'
    ),
    font=dict(size=12, family="Microsoft JhengHei"),
    # 不設定 width 和 height
    autosize=True,  # 重點！
    margin=dict(l=0, r=0, t=60, b=0)
)

# 儲存為 HTML，使用 full_html=False 會產生更乾淨的輸出
output_path = OUT / "Tree_Path_Sunburst_NEW.html"

# 使用 write_html 的 config 參數
config = {
    'responsive': True,
    'displayModeBar': True,
    'displaylogo': False
}

fig.write_html(
    output_path,
    config=config,
    include_plotlyjs='cdn',  # 使用 CDN 版本的 Plotly，檔案更小
    full_html=True
)

print(f"\n[OK] 已生成新的 Sunburst 圖表")
print(f"   檔案: {output_path}")
print(f"\n說明:")
print("   - 使用 autosize=True")
print("   - 不設定固定 width/height")
print("   - 使用 CDN Plotly (檔案更小)")
print("\n請開啟此檔案測試是否全螢幕顯示")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成互動式 Chart 2: 訂單數與平均週期趨勢
使用 Plotly 讓用戶可以懸停查看具體數據
"""

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path

# 資料路徑
DATA_DIR = Path("results_timeseries")
OUTPUT_DIR = Path("results_timeseries/individual_charts")
OUTPUT_DIR.mkdir(exist_ok=True)

# 讀取資料
matched_orders = pd.read_csv(DATA_DIR / "matched_orders.csv")

# 確保日期欄位格式正確
if 'order_date' in matched_orders.columns:
    matched_orders['order_date'] = pd.to_datetime(matched_orders['order_date'])
    matched_orders['order_month'] = matched_orders['order_date'].dt.to_period('M').astype(str)

if 'order_month' not in matched_orders.columns:
    print("錯誤: 缺少 order_month 欄位")
    exit(1)

# 計算月度統計
monthly = matched_orders.groupby('order_month').agg({
    'company_id': 'count',
    'days_before_order': 'mean'
}).rename(columns={'company_id': 'order_count'})

monthly['days_before_order'] = monthly['days_before_order'].round(1)

# 創建雙軸圖表
fig = make_subplots(specs=[[{"secondary_y": True}]])

# 添加柱狀圖（訂單數）
fig.add_trace(
    go.Bar(
        x=monthly.index,
        y=monthly['order_count'],
        name='訂單數',
        marker_color='#2196F3',
        opacity=0.7,
        hovertemplate='<b>%{x}</b><br>訂單數: %{y}<extra></extra>',
        hoverlabel=dict(
            bgcolor='#2196F3',
            font_size=14,
            font_family='Microsoft JhengHei'
        )
    ),
    secondary_y=False
)

# 添加折線圖（平均週期）- 帶數據點標記
fig.add_trace(
    go.Scatter(
        x=monthly.index,
        y=monthly['days_before_order'],
        name='平均週期',
        mode='lines+markers',
        line=dict(color='#FF5722', width=3),
        marker=dict(
            size=12,
            color='#FF5722',
            line=dict(color='white', width=2),
            symbol='circle'
        ),
        hovertemplate='<b>%{x}</b><br>平均成交週期: %{y:.1f} 天<extra></extra>',
        hoverlabel=dict(
            bgcolor='#FF5722',
            font_size=14,
            font_family='Microsoft JhengHei'
        )
    ),
    secondary_y=True
)

# 更新軸標籤
fig.update_xaxes(
    title_text="月份",
    tickangle=-45,
    showgrid=True,
    gridcolor='rgba(128,128,128,0.2)'
)

fig.update_yaxes(
    title_text="訂單數",
    secondary_y=False,
    showgrid=True,
    gridcolor='rgba(128,128,128,0.2)'
)

fig.update_yaxes(
    title_text="平均成交週期（天）",
    secondary_y=True
)

# 更新佈局
fig.update_layout(
    title={
        'text': '訂單數與平均週期趨勢（按月）',
        'x': 0.5,
        'xanchor': 'center',
        'font': {'size': 18, 'family': 'Microsoft JhengHei'}
    },
    hovermode='x unified',
    template='plotly_white',
    height=600,
    showlegend=True,
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    ),
    font=dict(family='Microsoft JhengHei', size=12),
    hoverdistance=100,  # 增加 hover 觸發距離
    spikedistance=1000  # 增加 spike 線顯示範圍
)

# 儲存互動式 HTML
output_html = OUTPUT_DIR / "chart2_monthly_trend_interactive.html"
fig.write_html(output_html)

print("=" * 60)
print("OK - 互動式 Chart 2 生成完成！")
print(f"OK - 輸出檔案: {output_html.absolute()}")
print("\n功能說明：")
print("- 滑鼠移到紅點上會顯示具體數據")
print("- 可以放大/縮小圖表")
print("- 點擊圖例可以顯示/隱藏數據系列")
print("=" * 60)

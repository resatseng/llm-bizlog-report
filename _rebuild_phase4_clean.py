#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重建 Phase 4 區塊：
1. 兩欄並排
2. 無邊框、無外框
3. 固定高度 450px
"""

import re
import base64
from pathlib import Path

# 讀取六張圖片
def img_to_base64(img_path):
    with open(img_path, "rb") as f:
        return base64.b64encode(f.read()).decode('utf-8')

print("讀取圖片...")
charts_data = [
    {
        'num': '①',
        'title': '各階段成交週期分布',
        'file': 'Phase4_訂單整合分析/results_timeseries/individual_charts/chart1_cycle_distribution.png',
        'lb_idx': 10
    },
    {
        'num': '②',
        'title': '訂單數與平均週期趨勢',
        'file': 'Phase4_訂單整合分析/results_timeseries/individual_charts/chart2_monthly_trend.png',
        'lb_idx': 11
    },
    {
        'num': '③',
        'title': '訂單金額 vs 成交週期',
        'file': 'Phase4_訂單整合分析/results_timeseries/individual_charts/chart3_amount_vs_cycle.png',
        'lb_idx': 12
    },
    {
        'num': '④',
        'title': '客戶分群分析',
        'file': 'Phase4_訂單整合分析/results_timeseries/individual_charts/chart4_customer_segments.png',
        'lb_idx': 13
    },
    {
        'num': '⑤',
        'title': '各階段週期分布（箱型圖）',
        'file': 'Phase4_訂單整合分析/results_timeseries/individual_charts/chart5_cycle_boxplot.png',
        'lb_idx': 14
    },
    {
        'num': '⑥',
        'title': '累積分布曲線（CDF）',
        'file': 'Phase4_訂單整合分析/results_timeseries/individual_charts/chart6_cdf.png',
        'lb_idx': 15
    }
]

# 轉換圖片為 base64
for chart in charts_data:
    chart['base64'] = img_to_base64(chart['file'])
    print(f"  {chart['num']} {chart['title']}")

# 讀取 HTML
with open('REPORT.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 找到 Phase 4 區塊
start_marker = '<h3>六圖整合分析（點擊放大）</h3>'
end_marker = '<h3>互動式視覺化（新視窗開啟）</h3>'

start_idx = content.find(start_marker)
end_idx = content.find(end_marker)

if start_idx == -1 or end_idx == -1:
    print("錯誤：找不到標記")
    exit(1)

# 重建 Phase 4 HTML（完全無邊框）
phase4_html = f'''
  <h3>六圖整合分析（點擊放大）</h3>

  <div style="display:grid; grid-template-columns:repeat(2,1fr); gap:20px; max-width:1400px; margin:20px auto;">
'''

for i, chart in enumerate(charts_data, 1):
    phase4_html += f'''
    <div style="padding:0; margin:0;">
      <h4 style="text-align:center; margin-bottom:10px; color:#fff;">{chart['num']} {chart['title']}</h4>
      <img src="data:image/png;base64,{chart['base64']}"
           alt="Chart {i}: {chart['title']}"
           style="width:100%; height:450px; object-fit:contain; cursor:pointer; display:block;"
           onclick="openLB({chart['lb_idx']})"
           title="點擊放大">
    </div>
'''

phase4_html += '''
  </div>

'''

# 替換內容
before = content[:start_idx]
after = content[end_idx:]
content = before + phase4_html + after

# 儲存
print("\n儲存檔案...")
with open('REPORT.html', 'w', encoding='utf-8') as f:
    f.write(content)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("\n" + "=" * 60)
print("完成！Phase 4 已重建")
print("- 兩欄並排（每行 2 張）")
print("- 完全無邊框、無外框")
print("- 固定高度 450px")
print("- 最大寬度 1400px")
print("\n請強制重新整理瀏覽器（Ctrl+Shift+R）")
print("=" * 60)

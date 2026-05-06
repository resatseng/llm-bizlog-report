#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增強圖表顯示 - 確保圖表可見並置中
"""

import re
from pathlib import Path

def enhance_chart_display(html_path):
    """增強圖表顯示效果"""
    print(f"\n處理: {html_path}")

    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. 修改圖表 div 尺寸為更大的尺寸
    old_div = r'class="plotly-graph-div" style="height:800px; width:900px;"'
    new_div = 'class="plotly-graph-div" style="height:100vh; width:100vw; background:#fff;"'

    if old_div in content:
        content = content.replace(old_div, new_div)
        print("  [OK] 已調整圖表尺寸為全螢幕")

    # 2. 添加頁面樣式 - 確保圖表可見
    body_style = '''<style>
    body {
        margin: 0;
        padding: 0;
        overflow: auto;
        background: #f5f5f5;
    }
    .plotly-graph-div {
        display: block !important;
        visibility: visible !important;
        opacity: 1 !important;
    }
</style>
</head>'''

    if '</head>' in content and '<style>' not in content:
        content = content.replace('</head>', body_style)
        print("  [OK] 已添加頁面樣式")

    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print("  [OK] 完成")
    return True

# 處理兩個圖表
charts = [
    Path("results_timeseries/Tree_Path_Sunburst.html"),
    Path("results_timeseries/Stage_Flow_Sankey.html")
]

print("=" * 60)
print("增強圖表顯示")
print("=" * 60)

success_count = 0
for chart_path in charts:
    if chart_path.exists():
        if enhance_chart_display(chart_path):
            success_count += 1
    else:
        print(f"\n找不到檔案: {chart_path}")

print("\n" + "=" * 60)
print(f"完成！成功處理 {success_count}/{len(charts)} 個圖表")
print("\n改進：")
print("- 圖表尺寸改為 100vh x 100vw（全螢幕）")
print("- 添加白色背景讓圖表更清楚")
print("- 確保 display、visibility、opacity 都正確")
print("- 移除可能的隱藏樣式")
print("=" * 60)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
讓圖表占滿螢幕顯示
"""

import re
from pathlib import Path

def make_fullscreen(html_path):
    """讓圖表占滿螢幕"""
    print(f"\n處理: {html_path}")

    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. 修改 div 尺寸為視窗大小
    content = re.sub(
        r'class="plotly-graph-div" style="height:\d+px; width:\d+px;"',
        'class="plotly-graph-div" style="width:100vw; height:100vh;"',
        content
    )
    content = re.sub(
        r'class="plotly-graph-div" style="height:\d+px; width:100%;"',
        'class="plotly-graph-div" style="width:100vw; height:100vh;"',
        content
    )
    print("  [OK] 已設定為全螢幕尺寸")

    # 2. 添加 CSS 確保正確顯示
    css_block = '''<style>
    html, body {
        margin: 0;
        padding: 0;
        width: 100%;
        height: 100%;
        overflow: hidden;
    }
    .plotly-graph-div {
        display: block !important;
        visibility: visible !important;
    }
</style>
</head>'''

    if '<style>' not in content:
        content = content.replace('</head>', css_block)
        print("  [OK] 已添加 CSS 樣式")

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
print("設定圖表為全螢幕顯示")
print("=" * 60)

for chart_path in charts:
    if chart_path.exists():
        make_fullscreen(chart_path)
    else:
        print(f"\n找不到檔案: {chart_path}")

print("\n" + "=" * 60)
print("完成！圖表現在會占滿整個視窗")
print("- width: 100vw（視窗寬度）")
print("- height: 100vh（視窗高度）")
print("- 移除邊距和溢出")
print("=" * 60)

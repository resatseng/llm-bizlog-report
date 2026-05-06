#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修正 Sankey 圖表顯示問題
"""

import re

html_path = "results_timeseries/Stage_Flow_Sankey.html"

with open(html_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 在 layout 中添加尺寸設定
if '"layout":' in content:
    content = re.sub(
        r'("layout":\s*\{)',
        r'\1"width":1200,"height":800,',
        content,
        count=1
    )
    print("已添加 width 和 height 到 layout")

# 確保容器有正確的樣式
if '<body>' in content:
    content = content.replace(
        '<body>',
        '<body style="margin:0; padding:20px; display:flex; justify-content:center; align-items:center; min-height:100vh;">'
    )
    print("已添加 body 樣式")

# 確保 plotly div 有正確的大小
content = re.sub(
    r'<div id="([^"]*plotly[^"]*)"([^>]*)>',
    r'<div id="\1" style="width:100%; max-width:1200px; height:800px;"\2>',
    content,
    flags=re.IGNORECASE
)

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"\n已修正 {html_path}")
print("- 設定圖表尺寸: 1200 × 800")
print("- 調整容器樣式: 置中顯示")
print("- 確保完整可見")

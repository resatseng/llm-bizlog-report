#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修正圖表置中顯示問題
"""

import re
from pathlib import Path

html_path = Path("results_timeseries/Tree_Path_Sunburst.html")

print("修正圖表置中顯示...")

with open(html_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 移除舊的 CSS
content = re.sub(
    r'<style>.*?</style>',
    '',
    content,
    flags=re.DOTALL
)

# 新的 CSS - 確保置中並可見工具列
new_css = '''<style>
html, body {
    margin: 0;
    padding: 0;
    width: 100%;
    height: 100%;
    overflow: auto;
    background: #f5f5f5;
    display: flex;
    justify-content: center;
    align-items: center;
}
.plotly-graph-div {
    width: 95vw !important;
    height: 95vh !important;
    max-width: 95vw;
    max-height: 95vh;
    background: white;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}
</style>
</head>'''

content = content.replace('</head>', new_css)

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("[OK] 已修正置中顯示")
print("- 使用 flexbox 置中")
print("- 圖表大小改為 95vw x 95vh（留邊距）")
print("- 淺灰色背景對比")
print("- 白色圖表背景 + 陰影")
print("- overflow: auto 確保可捲動")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
移除 Plotly layout 中的固定尺寸限制
"""

import re
import json
from pathlib import Path

def remove_layout_size(html_path):
    """移除 layout 中的 width 和 height 限制"""
    print(f"\n處理: {html_path}")

    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 找到 layout 物件並移除 width 和 height
    # layout 格式通常是: {"width":900,"height":800,...}
    # 我們要把這兩個屬性刪除

    # 方法：使用正則替換
    # 移除 "width":數字,
    content = re.sub(r'"width":\d+,?', '', content)
    # 移除 "height":數字,
    content = re.sub(r'"height":\d+,?', '', content)

    print("  [OK] 已移除 width 和 height 限制")

    # 修改 div 樣式為 100vw x 100vh（已在之前的腳本完成）
    # 確保有這個設定
    if '100vw' not in content or '100vh' not in content:
        print("  [WARNING] div 尺寸不是全螢幕")

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
print("移除 Plotly layout 尺寸限制")
print("=" * 60)

for chart_path in charts:
    if chart_path.exists():
        remove_layout_size(chart_path)
    else:
        print(f"\n找不到檔案: {chart_path}")

print("\n" + "=" * 60)
print("完成！")
print("- 已移除 layout 的 width 和 height 屬性")
print("- 圖表現在會自適應容器大小")
print("- 配合 div 的 100vw × 100vh，圖表會占滿螢幕")
print("=" * 60)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增大互動式圖表尺寸，讓用戶可以看到更多細節
Sunburst 圖表不支援 scrollZoom，因此直接增大圖表尺寸
"""

import re
from pathlib import Path

def increase_chart_size(html_path, width=2000, height=2000):
    """增大圖表的顯示尺寸"""
    print(f"\n處理: {html_path}")

    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 修改 div 的樣式
    # 從 style="height:800px; width:900px;" 改為更大的尺寸
    old_div_pattern = r'class="plotly-graph-div" style="height:\d+px; width:\d+px;"'
    new_div = f'class="plotly-graph-div" style="height:{height}px; width:{width}px;"'

    if re.search(old_div_pattern, content):
        content = re.sub(old_div_pattern, new_div, content)
        print(f"  [OK] 已設定圖表尺寸為 {width}x{height}")

        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("  [OK] 已儲存檔案")
        return True
    else:
        print("  [ERROR] 找不到圖表 div")
        return False

# 處理兩個圖表
charts = [
    ("results_timeseries/Tree_Path_Sunburst.html", 2000, 2000),  # Sunburst 用正方形
    ("results_timeseries/Stage_Flow_Sankey.html", 2400, 1600)    # Sankey 保持寬高比
]

print("=" * 60)
print("增大互動式圖表尺寸")
print("=" * 60)

success_count = 0
for chart_info in charts:
    chart_path = Path(chart_info[0])
    width = chart_info[1]
    height = chart_info[2]

    if chart_path.exists():
        if increase_chart_size(chart_path, width, height):
            success_count += 1
    else:
        print(f"\n找不到檔案: {chart_path}")

print("\n" + "=" * 60)
print(f"完成！成功處理 {success_count}/{len(charts)} 個圖表")
print("\n說明：")
print("- Sunburst 圖表：2000x2000 (正方形，更容易看清層級)")
print("- Sankey 圖表：2400x1600 (橫向，適合流程)")
print("- 圖表會顯示捲軸，可以捲動查看完整內容")
print("=" * 60)

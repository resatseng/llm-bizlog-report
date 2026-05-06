#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增大圖表初始尺寸
"""

from pathlib import Path

def increase_chart_size(html_path, width, height, old_pattern=None):
    """增大圖表初始顯示尺寸"""
    print(f"\n處理: {html_path}")
    print(f"  目標尺寸: {width} x {height}")

    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 替換圖表 div 尺寸
    if old_pattern is None:
        old_pattern = 'class="plotly-graph-div" style="height:800px; width:900px;"'

    new_pattern = f'class="plotly-graph-div" style="height:{height}px; width:{width}px;"'

    if old_pattern in content:
        content = content.replace(old_pattern, new_pattern)
        print("  [OK] 已更新尺寸")

        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    else:
        print(f"  [ERROR] 找不到原始尺寸設定: {old_pattern}")
        return False

# 處理兩個圖表
charts = [
    ("results_timeseries/Tree_Path_Sunburst.html", 1400, 1400, 'class="plotly-graph-div" style="height:800px; width:900px;"'),
    ("results_timeseries/Stage_Flow_Sankey.html", 1600, 1000, 'class="plotly-graph-div" style="height:700px; width:100%;"')
]

print("=" * 60)
print("增大圖表初始尺寸")
print("=" * 60)

success_count = 0
for chart_file, width, height, old_pattern in charts:
    chart_path = Path(chart_file)
    if chart_path.exists():
        if increase_chart_size(chart_path, width, height, old_pattern):
            success_count += 1
    else:
        print(f"\n找不到檔案: {chart_path}")

print("\n" + "=" * 60)
print(f"完成！成功處理 {success_count}/{len(charts)} 個圖表")
print("\n改進：")
print("- Sunburst: 1400 x 1400 (更大的圓形)")
print("- Sankey: 1600 x 1000 (寬扁流程圖)")
print("- 點開後直接看到較大圖表")
print("- 然後可以用滾輪繼續縮放")
print("=" * 60)

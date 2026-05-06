#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
在 Sunburst 和 Sankey 圖表中啟用滾輪縮放
"""

import re
from pathlib import Path

def enable_scroll_zoom(html_path):
    """啟用 Plotly 圖表的滾輪縮放功能"""
    print(f"\n處理: {html_path}")

    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 找到並替換配置對象
    # 將 {"responsive": true} 替換為包含 scrollZoom 的完整配置
    old_config = '{"responsive": true}'
    new_config = '''{
        "responsive": true,
        "scrollZoom": true,
        "displayModeBar": true,
        "displaylogo": false,
        "modeBarButtonsToRemove": [],
        "toImageButtonOptions": {
            "format": "png",
            "filename": "chart"
        }
    }'''

    if old_config in content:
        content = content.replace(old_config, new_config)
        print("  [OK] 已添加 scrollZoom 配置")

        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("  [OK] 已儲存檔案")
        return True
    else:
        print("  [ERROR] 找不到配置對象")
        return False

# 處理兩個圖表
charts = [
    Path("results_timeseries/Tree_Path_Sunburst.html"),
    Path("results_timeseries/Stage_Flow_Sankey.html")
]

print("=" * 60)
print("啟用滾輪縮放功能")
print("=" * 60)

success_count = 0
for chart_path in charts:
    if chart_path.exists():
        if enable_scroll_zoom(chart_path):
            success_count += 1
    else:
        print(f"\n找不到檔案: {chart_path}")

print("\n" + "=" * 60)
print(f"完成！成功處理 {success_count}/{len(charts)} 個圖表")
print("\n功能說明：")
print("- 現在可以使用滑鼠滾輪來縮放圖表")
print("- 向上滾動：放大")
print("- 向下滾動：縮小")
print("- 雙擊可重置視圖")
print("=" * 60)

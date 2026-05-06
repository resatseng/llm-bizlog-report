#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修正 Plotly 圖表尺寸 - 移除固定尺寸限制
"""

import re
from pathlib import Path

def fix_plotly_size(html_path):
    """修正 Plotly 圖表尺寸配置"""
    print(f"\n處理: {html_path}")

    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 找到並修改 config 物件，確保 responsive: true
    # Plotly.newPlot 的格式: Plotly.newPlot(id, data, layout, config)
    # 我們需要確保 config 包含 responsive: true

    # 替換 {"responsive": true} 為包含 autosize 的版本
    old_config = '{"responsive": true}'
    new_config = '{"responsive": true, "autosizable": true, "displayModeBar": true}'

    if old_config in content:
        content = content.replace(old_config, new_config)
        print("  [OK] 已更新 config")

    # 在 </body> 前添加腳本強制調整大小
    resize_script = '''
<script id="force-resize">
window.addEventListener('load', function() {
    setTimeout(function() {
        // 找到 Plotly div
        const plotDiv = document.querySelector('.plotly-graph-div');
        if (plotDiv && window.Plotly) {
            console.log('[調整] 強制調整 Plotly 圖表大小');

            // 使用 Plotly.relayout 強制更新尺寸
            Plotly.relayout(plotDiv, {
                'width': window.innerWidth,
                'height': window.innerHeight,
                'autosize': true
            });

            // 監聽視窗大小變化
            window.addEventListener('resize', function() {
                Plotly.relayout(plotDiv, {
                    'width': window.innerWidth,
                    'height': window.innerHeight
                });
            });

            console.log('[調整] ✓ 完成');
        } else {
            console.error('[調整] 找不到圖表或 Plotly');
        }
    }, 1000);
});
</script>
'''

    if 'force-resize' not in content:
        # 在滾輪縮放腳本之前插入
        if 'wheel-zoom-handler' in content:
            content = content.replace(
                '<script id="wheel-zoom-handler">',
                resize_script + '\n<script id="wheel-zoom-handler">'
            )
            print("  [OK] 已添加尺寸調整腳本")
        else:
            content = content.replace('</body>', resize_script + '\n</body>')
            print("  [OK] 已添加尺寸調整腳本")

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
print("修正 Plotly 圖表尺寸")
print("=" * 60)

for chart_path in charts:
    if chart_path.exists():
        fix_plotly_size(chart_path)
    else:
        print(f"\n找不到檔案: {chart_path}")

print("\n" + "=" * 60)
print("完成！")
print("- 啟用 responsive 模式")
print("- 強制調整為視窗大小")
print("- 監聽視窗大小變化自動調整")
print("=" * 60)

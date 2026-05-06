#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
為 Sunburst 和 Sankey 圖表添加滾輪縮放功能
使用自定義 JavaScript 實現 CSS transform scale
"""

import re
from pathlib import Path

def add_wheel_zoom_script(html_path):
    """添加滾輪縮放的 JavaScript 代碼"""
    print(f"\n處理: {html_path}")

    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 檢查是否已經添加過
    if 'wheel-zoom-handler' in content:
        print("  [SKIP] 已經有滾輪縮放功能")
        return False

    # 添加縮放腳本在 </body> 之前
    zoom_script = '''
<script id="wheel-zoom-handler">
// 滾輪縮放功能
(function() {
    const plotDiv = document.querySelector('.plotly-graph-div');
    if (!plotDiv) return;

    let scale = 1;
    const MIN_SCALE = 0.5;
    const MAX_SCALE = 5;
    const SCALE_STEP = 0.1;

    // 創建包裝容器
    const wrapper = document.createElement('div');
    wrapper.style.cssText = 'overflow: auto; width: 100%; height: 100vh; display: flex; justify-content: center; align-items: center;';
    plotDiv.parentNode.insertBefore(wrapper, plotDiv);
    wrapper.appendChild(plotDiv);

    // 滾輪事件
    wrapper.addEventListener('wheel', function(e) {
        e.preventDefault();

        // 計算新的縮放比例
        const delta = e.deltaY > 0 ? -SCALE_STEP : SCALE_STEP;
        scale = Math.min(Math.max(scale + delta, MIN_SCALE), MAX_SCALE);

        // 應用縮放
        plotDiv.style.transform = `scale(${scale})`;
        plotDiv.style.transformOrigin = 'center center';

        // 顯示當前縮放比例
        showZoomLevel(scale);
    }, { passive: false });

    // 顯示縮放比例提示
    function showZoomLevel(scale) {
        let indicator = document.getElementById('zoom-indicator');
        if (!indicator) {
            indicator = document.createElement('div');
            indicator.id = 'zoom-indicator';
            indicator.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                background: rgba(0,0,0,0.7);
                color: white;
                padding: 10px 15px;
                border-radius: 5px;
                font-family: Arial, sans-serif;
                font-size: 14px;
                z-index: 10000;
                transition: opacity 0.3s;
            `;
            document.body.appendChild(indicator);
        }

        indicator.textContent = `縮放: ${Math.round(scale * 100)}%`;
        indicator.style.opacity = '1';

        // 2秒後淡出
        clearTimeout(indicator.timeout);
        indicator.timeout = setTimeout(() => {
            indicator.style.opacity = '0';
        }, 2000);
    }

    // 雙擊重置
    wrapper.addEventListener('dblclick', function() {
        scale = 1;
        plotDiv.style.transform = 'scale(1)';
        showZoomLevel(scale);
    });

    console.log('滾輪縮放已啟用 - 向上滾動放大，向下滾動縮小，雙擊重置');
})();
</script>
'''

    # 在 </body> 前插入
    content = content.replace('</body>', zoom_script + '\n</body>')

    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print("  [OK] 已添加滾輪縮放功能")
    return True

# 處理兩個圖表
charts = [
    Path("results_timeseries/Tree_Path_Sunburst.html"),
    Path("results_timeseries/Stage_Flow_Sankey.html")
]

print("=" * 60)
print("添加自定義滾輪縮放功能")
print("=" * 60)

success_count = 0
for chart_path in charts:
    if chart_path.exists():
        if add_wheel_zoom_script(chart_path):
            success_count += 1
    else:
        print(f"\n找不到檔案: {chart_path}")

print("\n" + "=" * 60)
print(f"完成！成功處理 {success_count}/{len(charts)} 個圖表")
print("\n功能說明：")
print("- 滑鼠滾輪：縮放圖表 (50% - 500%)")
print("- 向上滾動：放大")
print("- 向下滾動：縮小")
print("- 雙擊：重置為 100%")
print("- 右上角會顯示當前縮放比例")
print("=" * 60)

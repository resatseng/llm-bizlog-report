#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修正滾輪縮放功能 - 確保在 Plotly 渲染完成後執行
"""

import re
from pathlib import Path

def fix_wheel_zoom_script(html_path):
    """修正滾輪縮放腳本"""
    print(f"\n處理: {html_path}")

    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 移除舊的腳本
    content = re.sub(
        r'<script id="wheel-zoom-handler">.*?</script>',
        '',
        content,
        flags=re.DOTALL
    )

    # 新的改進版腳本
    zoom_script = '''
<script id="wheel-zoom-handler">
// 滾輪縮放功能 - 等待 Plotly 渲染完成
window.addEventListener('load', function() {
    setTimeout(function() {
        const plotDiv = document.querySelector('.plotly-graph-div');

        if (!plotDiv) {
            console.error('找不到 Plotly 圖表元素');
            return;
        }

        console.log('找到圖表元素:', plotDiv);

        let scale = 1;
        const MIN_SCALE = 0.3;
        const MAX_SCALE = 8;
        const SCALE_STEP = 0.15;

        // 直接在圖表 div 上監聽滾輪事件
        plotDiv.addEventListener('wheel', function(e) {
            e.preventDefault();
            e.stopPropagation();

            // 計算新的縮放比例
            const delta = e.deltaY > 0 ? -SCALE_STEP : SCALE_STEP;
            scale = Math.min(Math.max(scale + delta, MIN_SCALE), MAX_SCALE);

            // 應用縮放
            plotDiv.style.transform = `scale(${scale})`;
            plotDiv.style.transformOrigin = 'center center';
            plotDiv.style.transition = 'transform 0.1s ease-out';

            // 顯示縮放比例
            showZoomLevel(scale);

            console.log('當前縮放:', Math.round(scale * 100) + '%');
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
                    background: rgba(76, 175, 80, 0.9);
                    color: white;
                    padding: 12px 20px;
                    border-radius: 8px;
                    font-family: 'Microsoft JhengHei', Arial, sans-serif;
                    font-size: 16px;
                    font-weight: bold;
                    z-index: 99999;
                    transition: opacity 0.3s;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
                `;
                document.body.appendChild(indicator);
            }

            indicator.textContent = `🔍 縮放: ${Math.round(scale * 100)}%`;
            indicator.style.opacity = '1';

            clearTimeout(indicator.timeout);
            indicator.timeout = setTimeout(() => {
                indicator.style.opacity = '0';
            }, 1500);
        }

        // 雙擊重置
        plotDiv.addEventListener('dblclick', function(e) {
            e.preventDefault();
            scale = 1;
            plotDiv.style.transform = 'scale(1)';
            showZoomLevel(scale);
            console.log('已重置縮放');
        });

        console.log('✓ 滾輪縮放已啟用！');
        console.log('- 在圖表上滾動滑鼠滾輪即可縮放');
        console.log('- 雙擊圖表重置');

        // 顯示初始提示
        showZoomLevel(scale);
    }, 500);  // 等待 500ms 確保 Plotly 完全渲染
});
</script>
'''

    # 在 </body> 前插入
    content = content.replace('</body>', zoom_script + '\n</body>')

    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print("  [OK] 已修正滾輪縮放功能")
    return True

# 處理兩個圖表
charts = [
    Path("results_timeseries/Tree_Path_Sunburst.html"),
    Path("results_timeseries/Stage_Flow_Sankey.html")
]

print("=" * 60)
print("修正滾輪縮放功能")
print("=" * 60)

success_count = 0
for chart_path in charts:
    if chart_path.exists():
        if fix_wheel_zoom_script(chart_path):
            success_count += 1
    else:
        print(f"\n找不到檔案: {chart_path}")

print("\n" + "=" * 60)
print(f"完成！成功處理 {success_count}/{len(charts)} 個圖表")
print("\n改進：")
print("- 等待頁面完全載入後才初始化")
print("- 直接在圖表元素上監聽滾輪事件")
print("- 增加調試訊息到瀏覽器控制台")
print("- 改善視覺提示（綠色、更大字體）")
print("- 縮放範圍擴大到 30%-800%")
print("=" * 60)

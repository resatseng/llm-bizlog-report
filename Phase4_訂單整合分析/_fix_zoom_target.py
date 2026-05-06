#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修正縮放目標元素 - 對整個頁面 body 進行縮放
"""

import re
from pathlib import Path

def fix_zoom_target(html_path):
    """修正縮放目標元素"""
    print(f"\n處理: {html_path}")

    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 移除舊腳本
    content = re.sub(
        r'<script id="wheel-zoom-handler">.*?</script>',
        '',
        content,
        flags=re.DOTALL
    )

    # 新腳本 - 直接縮放整個 body
    zoom_script = '''
<script id="wheel-zoom-handler">
// 滾輪縮放 - 縮放整個頁面
(function() {
    let scale = 1;
    const MIN_SCALE = 0.5;
    const MAX_SCALE = 8;
    const SCALE_STEP = 0.15;

    console.log('[縮放] 初始化中...');

    // 等待載入完成
    window.addEventListener('load', function() {
        setTimeout(function() {
            console.log('[縮放] 頁面已載入');

            // 監聽滾輪事件
            document.addEventListener('wheel', function(e) {
                e.preventDefault();

                // 計算縮放
                const delta = e.deltaY > 0 ? -SCALE_STEP : SCALE_STEP;
                scale = Math.min(Math.max(scale + delta, MIN_SCALE), MAX_SCALE);

                // 對 body 應用縮放
                document.body.style.transform = `scale(${scale})`;
                document.body.style.transformOrigin = 'top center';
                document.body.style.transition = 'transform 0.05s ease-out';

                // 顯示提示
                showZoom(Math.round(scale * 100));

                console.log('[縮放]', Math.round(scale * 100) + '%');
            }, { passive: false });

            // 雙擊重置
            document.addEventListener('dblclick', function(e) {
                scale = 1;
                document.body.style.transform = 'scale(1)';
                showZoom(100);
                console.log('[縮放] 已重置');
            });

            console.log('[縮放] ✓ 已啟用 - 滾動滑鼠滾輪即可縮放');

            // 顯示初始提示
            showZoom(100);

        }, 500);
    });

    // 顯示縮放提示
    function showZoom(percent) {
        let indicator = document.getElementById('zoom-indicator');
        if (!indicator) {
            indicator = document.createElement('div');
            indicator.id = 'zoom-indicator';
            indicator.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 15px 30px;
                border-radius: 12px;
                font-family: 'Microsoft JhengHei', 'Arial', sans-serif;
                font-size: 20px;
                font-weight: bold;
                z-index: 999999;
                opacity: 0;
                transition: opacity 0.3s ease;
                box-shadow: 0 8px 20px rgba(0,0,0,0.3);
                pointer-events: none;
            `;
            document.body.appendChild(indicator);
        }

        indicator.textContent = `🔍 ${percent}%`;
        indicator.style.opacity = '1';

        clearTimeout(indicator.timeout);
        indicator.timeout = setTimeout(() => {
            indicator.style.opacity = '0';
        }, 1200);
    }
})();
</script>
'''

    # 在 </body> 前插入
    content = content.replace('</body>', zoom_script + '\n</body>')

    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print("  [OK] 已修正縮放目標")
    return True

# 處理兩個圖表
charts = [
    Path("results_timeseries/Tree_Path_Sunburst.html"),
    Path("results_timeseries/Stage_Flow_Sankey.html")
]

print("=" * 60)
print("修正縮放目標元素")
print("=" * 60)

success_count = 0
for chart_path in charts:
    if chart_path.exists():
        if fix_zoom_target(chart_path):
            success_count += 1
    else:
        print(f"\n找不到檔案: {chart_path}")

print("\n" + "=" * 60)
print(f"完成！成功處理 {success_count}/{len(charts)} 個圖表")
print("\n改進：")
print("- 直接縮放整個 body 元素（包含圖表）")
print("- 簡化事件處理邏輯")
print("- 使用漸層色提示（紫藍漸層）")
print("- 縮放範圍：50% - 800%")
print("=" * 60)

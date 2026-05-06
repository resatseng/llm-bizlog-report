#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
應用增強版滾輪縮放 - 捕獲所有滾輪事件
"""

import re
from pathlib import Path

def apply_advanced_zoom(html_path):
    """應用增強版縮放腳本"""
    print(f"\n處理: {html_path}")

    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 移除所有舊的滾輪縮放腳本
    content = re.sub(
        r'<script id="wheel-zoom-handler">.*?</script>',
        '',
        content,
        flags=re.DOTALL
    )

    # 新的增強版腳本 - 在 document 層級捕獲事件
    zoom_script = '''
<script id="wheel-zoom-handler">
// 增強版滾輪縮放 - 在 document 層級捕獲
(function() {
    let scale = 1;
    const MIN_SCALE = 0.5;
    const MAX_SCALE = 5;
    const SCALE_STEP = 0.1;
    let plotDiv = null;
    let zoomIndicator = null;

    // 初始化
    function init() {
        plotDiv = document.querySelector('.plotly-graph-div');
        if (!plotDiv) {
            console.error('[縮放] 找不到圖表元素');
            return;
        }

        console.log('[縮放] 圖表元素已找到');

        // 創建縮放提示
        zoomIndicator = document.createElement('div');
        zoomIndicator.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: rgba(76, 175, 80, 0.95);
            color: white;
            padding: 15px 25px;
            border-radius: 10px;
            font-family: 'Microsoft JhengHei', Arial, sans-serif;
            font-size: 18px;
            font-weight: bold;
            z-index: 999999;
            opacity: 0;
            transition: opacity 0.3s;
            box-shadow: 0 4px 12px rgba(0,0,0,0.4);
            pointer-events: none;
        `;
        document.body.appendChild(zoomIndicator);

        // 在 document 層級監聽滾輪
        document.addEventListener('wheel', handleWheel, { passive: false });

        // 雙擊重置
        plotDiv.addEventListener('dblclick', resetZoom);

        console.log('[縮放] ✓ 滾輪縮放已啟用');
        showZoom(100);
    }

    // 處理滾輪事件
    function handleWheel(e) {
        if (!plotDiv) return;

        // 檢查鼠標是否在圖表上
        const rect = plotDiv.getBoundingClientRect();
        const mouseX = e.clientX;
        const mouseY = e.clientY;

        if (mouseX >= rect.left && mouseX <= rect.right &&
            mouseY >= rect.top && mouseY <= rect.bottom) {

            e.preventDefault();
            e.stopPropagation();

            // 計算縮放
            const delta = e.deltaY > 0 ? -SCALE_STEP : SCALE_STEP;
            scale = Math.min(Math.max(scale + delta, MIN_SCALE), MAX_SCALE);

            // 應用縮放
            plotDiv.style.transform = `scale(${scale})`;
            plotDiv.style.transformOrigin = '50% 50%';

            showZoom(Math.round(scale * 100));

            console.log('[縮放] 當前:', Math.round(scale * 100) + '%');

            return false;
        }
    }

    // 重置縮放
    function resetZoom(e) {
        e.preventDefault();
        scale = 1;
        plotDiv.style.transform = 'scale(1)';
        showZoom(100);
        console.log('[縮放] 已重置');
    }

    // 顯示縮放提示
    function showZoom(percent) {
        if (!zoomIndicator) return;

        zoomIndicator.textContent = `🔍 ${percent}%`;
        zoomIndicator.style.opacity = '1';

        clearTimeout(zoomIndicator.timeout);
        zoomIndicator.timeout = setTimeout(() => {
            zoomIndicator.style.opacity = '0';
        }, 1500);
    }

    // 等待頁面完全載入
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            setTimeout(init, 800);
        });
    } else {
        setTimeout(init, 800);
    }
})();
</script>
'''

    # 在 </body> 前插入
    content = content.replace('</body>', zoom_script + '\n</body>')

    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print("  [OK] 已應用增強版縮放")
    return True

# 處理兩個圖表
charts = [
    Path("results_timeseries/Tree_Path_Sunburst.html"),
    Path("results_timeseries/Stage_Flow_Sankey.html")
]

print("=" * 60)
print("應用增強版滾輪縮放")
print("=" * 60)

success_count = 0
for chart_path in charts:
    if chart_path.exists():
        if apply_advanced_zoom(chart_path):
            success_count += 1
    else:
        print(f"\n找不到檔案: {chart_path}")

print("\n" + "=" * 60)
print(f"完成！成功處理 {success_count}/{len(charts)} 個圖表")
print("\n改進：")
print("- 在 document 層級捕獲滾輪事件（更可靠）")
print("- 檢查鼠標位置是否在圖表上")
print("- 防止事件冒泡和默認行為")
print("- 增加初始化延遲到 800ms")
print("- 添加詳細的控制台日誌")
print("=" * 60)

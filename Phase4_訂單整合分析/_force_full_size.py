#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
強制設定圖表為全尺寸 - 最激進的方法
"""

import re
from pathlib import Path

def force_full_size(html_path):
    """用 JavaScript 強制設定 SVG 尺寸"""
    print(f"\n處理: {html_path}")

    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 移除所有現有的 resize 和 zoom 腳本
    content = re.sub(r'<script id="force-resize">.*?</script>', '', content, flags=re.DOTALL)
    content = re.sub(r'<script id="wheel-zoom-handler">.*?</script>', '', content, flags=re.DOTALL)

    # 新的強制尺寸腳本
    force_script = '''
<script>
// 強制全螢幕顯示
window.addEventListener('load', function() {
    setTimeout(function() {
        console.log('[全螢幕] 開始強制設定');

        // 找到所有 SVG 元素
        const svgs = document.querySelectorAll('svg.main-svg');
        svgs.forEach(function(svg) {
            svg.setAttribute('width', '100%');
            svg.setAttribute('height', '100%');
            svg.style.width = '100vw';
            svg.style.height = '100vh';
            console.log('[全螢幕] 已設定 SVG 尺寸');
        });

        // 找到 Plotly 容器
        const plotDiv = document.querySelector('.plotly-graph-div');
        if (plotDiv) {
            plotDiv.style.width = '100vw';
            plotDiv.style.height = '100vh';
            plotDiv.style.position = 'fixed';
            plotDiv.style.top = '0';
            plotDiv.style.left = '0';
            console.log('[全螢幕] 已設定容器尺寸');

            // 強制 Plotly 重新計算
            if (window.Plotly) {
                Plotly.Plots.resize(plotDiv);
                console.log('[全螢幕] 已觸發 Plotly 重新計算');
            }
        }

        console.log('[全螢幕] ✓ 完成');
    }, 1500);
});
</script>

<script>
// 滾輪縮放
window.addEventListener('load', function() {
    setTimeout(function() {
        let scale = 1;

        document.addEventListener('wheel', function(e) {
            e.preventDefault();

            const delta = e.deltaY > 0 ? -0.1 : 0.1;
            scale = Math.max(0.5, Math.min(8, scale + delta));

            document.body.style.transform = 'scale(' + scale + ')';
            document.body.style.transformOrigin = 'top left';

            let tip = document.getElementById('zoom-tip');
            if (!tip) {
                tip = document.createElement('div');
                tip.id = 'zoom-tip';
                tip.style.cssText = 'position:fixed; top:10px; right:10px; background:#4CAF50; color:white; padding:10px 20px; border-radius:8px; font-size:16px; z-index:999999; font-family:Arial;';
                document.body.appendChild(tip);
            }
            tip.textContent = Math.round(scale * 100) + '%';
            tip.style.opacity = '1';

            clearTimeout(tip.timer);
            tip.timer = setTimeout(function() { tip.style.opacity = '0'; }, 1000);
        }, {passive: false});
    }, 2000);
});
</script>
'''

    # 在 </body> 前插入
    content = content.replace('</body>', force_script + '\n</body>')

    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print("  [OK] 已強制設定全螢幕")
    return True

# 處理兩個圖表
charts = [
    Path("results_timeseries/Tree_Path_Sunburst.html"),
    Path("results_timeseries/Stage_Flow_Sankey.html")
]

print("=" * 60)
print("強制設定圖表為全螢幕")
print("=" * 60)

for chart_path in charts:
    if chart_path.exists():
        force_full_size(chart_path)
    else:
        print(f"\n找不到檔案: {chart_path}")

print("\n" + "=" * 60)
print("完成！使用最激進的方法：")
print("- 直接設定 SVG width/height = 100vw/100vh")
print("- 容器 position: fixed 占滿視窗")
print("- 強制觸發 Plotly.Plots.resize()")
print("=" * 60)

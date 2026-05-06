#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
添加最簡單的滾輪縮放 - 不修改任何原有結構
"""

import re
from pathlib import Path

def add_simple_zoom(html_path):
    """只添加縮放功能，不修改原有結構"""
    print(f"\n處理: {html_path}")

    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 檢查是否已經有縮放腳本
    if 'wheel-zoom-handler' in content:
        print("  [SKIP] 已有縮放功能")
        return False

    # 極簡縮放腳本
    zoom_script = '''
<script id="wheel-zoom-handler">
// 極簡滾輪縮放
window.addEventListener('load', function() {
    setTimeout(function() {
        let scale = 1;

        document.addEventListener('wheel', function(e) {
            e.preventDefault();

            const delta = e.deltaY > 0 ? -0.1 : 0.1;
            scale = Math.max(0.5, Math.min(8, scale + delta));

            document.body.style.transform = `scale(${scale})`;
            document.body.style.transformOrigin = 'top left';

            // 顯示提示
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
            tip.timer = setTimeout(() => tip.style.opacity = '0', 1000);
        }, {passive: false});

        console.log('縮放已啟用');
    }, 500);
});
</script>
'''

    # 在 </body> 前插入
    if '</body>' in content:
        content = content.replace('</body>', zoom_script + '\n</body>')
        print("  [OK] 已添加縮放功能")
    else:
        print("  [ERROR] 找不到 </body>")
        return False

    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(content)

    return True

# 處理兩個圖表
charts = [
    Path("results_timeseries/Tree_Path_Sunburst.html"),
    Path("results_timeseries/Stage_Flow_Sankey.html")
]

print("=" * 60)
print("添加極簡滾輪縮放")
print("=" * 60)

for chart_path in charts:
    if chart_path.exists():
        # 先恢復原始版本
        original = chart_path.parent / (chart_path.stem + "_original.html")
        if original.exists():
            print(f"\n從原始版本恢復: {chart_path.name}")
            import shutil
            shutil.copy(original, chart_path)

        add_simple_zoom(chart_path)
    else:
        print(f"\n找不到檔案: {chart_path}")

print("\n" + "=" * 60)
print("完成！")
print("- 保留原始圖表結構")
print("- 只添加滾輪縮放功能")
print("- 縮放範圍：50% - 800%")
print("=" * 60)

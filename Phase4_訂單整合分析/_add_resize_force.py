#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
添加強制調整 Plotly 圖表大小的 JavaScript
"""

import re
from pathlib import Path

html_path = Path("results_timeseries/Tree_Path_Sunburst.html")

print("添加強制調整大小腳本...")

with open(html_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 移除舊的滾輪縮放腳本
content = re.sub(
    r'<script>\s*//\s*滾輪縮放.*?</script>',
    '',
    content,
    flags=re.DOTALL
)

# 新的腳本：強制調整 + 滾輪縮放
new_script = '''
<script>
// 強制調整 Plotly 圖表大小
window.addEventListener('load', function() {
    setTimeout(function() {
        const plotDiv = document.querySelector('.plotly-graph-div');
        if (plotDiv && window.Plotly) {
            console.log('[調整] 開始強制調整圖表大小');

            // 方法1: 使用 Plotly.relayout 強制設定尺寸
            Plotly.relayout(plotDiv, {
                width: window.innerWidth,
                height: window.innerHeight,
                autosize: true
            }).then(function() {
                console.log('[調整] ✓ 完成 - 尺寸:', window.innerWidth, 'x', window.innerHeight);
            }).catch(function(err) {
                console.error('[調整] 錯誤:', err);
            });

            // 監聽視窗大小變化
            window.addEventListener('resize', function() {
                Plotly.relayout(plotDiv, {
                    width: window.innerWidth,
                    height: window.innerHeight
                });
            });
        } else {
            console.error('[調整] 找不到圖表或 Plotly');
        }
    }, 1000);
});

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
    }, 1500);
});
</script>
</body>
</html>'''

# 替換 </body></html>
content = re.sub(r'</body>\s*</html>', new_script, content)

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("[OK] 已添加強制調整大小腳本")
print("- 使用 Plotly.relayout() 強制設定 width/height")
print("- 延遲 1 秒執行確保 Plotly 完全載入")
print("- 監聽視窗大小變化自動調整")
print("- 保留滾輪縮放功能")

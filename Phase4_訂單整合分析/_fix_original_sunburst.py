#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修改原始完整版 Sunburst 的尺寸設定
"""

import re
from pathlib import Path

def fix_original(input_path, output_path):
    """修改原始檔案的尺寸設定"""
    print(f"\n處理: {input_path}")

    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. 移除 layout 中的固定尺寸
    # 找到 "width":900, 和 "height":800,
    content = re.sub(r'"width":900,', '', content)
    content = re.sub(r'"height":800,', '', content)
    print("  [OK] 已移除固定 width/height")

    # 2. 在 layout 中添加 autosize
    # 找到 "margin":{ 並在前面插入 "autosize":true,
    content = re.sub(
        r'("margin":\{)',
        r'"autosize":true,\1',
        content
    )
    print("  [OK] 已添加 autosize:true")

    # 3. 修改 div 尺寸為 100vw x 100vh
    content = re.sub(
        r'class="plotly-graph-div" style="height:\d+px; width:\d+px;"',
        'class="plotly-graph-div" style="width:100%; height:100%;"',
        content
    )
    print("  [OK] 已修改 div 尺寸")

    # 4. 添加 CSS
    css_style = '''<style>
html, body {
    margin: 0;
    padding: 0;
    width: 100%;
    height: 100%;
    overflow: hidden;
}
.plotly-graph-div {
    width: 100vw !important;
    height: 100vh !important;
}
</style>
</head>'''

    if '<style>' not in content:
        content = content.replace('</head>', css_style)
        print("  [OK] 已添加 CSS")

    # 5. 添加滾輪縮放
    zoom_script = '''
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
    }, 500);
});
</script>
</body>
</html>'''

    content = re.sub(r'</body>\s*</html>', zoom_script, content)
    print("  [OK] 已添加滾輪縮放")

    # 儲存
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"  [OK] 已儲存: {output_path}")
    return True

# 處理
input_file = Path("results_timeseries/Tree_Path_Sunburst_ORIGINAL.html")
output_file = Path("results_timeseries/Tree_Path_Sunburst.html")

print("=" * 60)
print("修改原始完整版 Sunburst")
print("=" * 60)

if input_file.exists():
    fix_original(input_file, output_file)
    print("\n" + "=" * 60)
    print("完成！")
    print("- 保留原始完整路徑樹結構")
    print("- 移除固定尺寸限制")
    print("- 添加 autosize: true")
    print("- 設定全螢幕 CSS")
    print("- 添加滾輪縮放功能")
    print("=" * 60)
else:
    print(f"\n找不到檔案: {input_file}")

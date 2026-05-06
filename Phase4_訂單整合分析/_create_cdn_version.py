#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
創建使用 CDN Plotly 的版本 - 更小更可靠
"""

import json
import re
from pathlib import Path

def extract_plot_data(html_path):
    """從現有 HTML 提取 Plotly 資料"""
    print(f"\n提取資料: {html_path}")

    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 找到 Plotly.newPlot 的呼叫
    pattern = r'Plotly\.newPlot\(\s*"([^"]+)",\s*(\[[^\]]+\]),\s*(\{[^}]+\}),\s*(\{[^}]+\})\s*\)'

    # 這個正則不夠強，因為資料很複雜，讓我用另一個方法
    # 找到 div id
    div_match = re.search(r'<div id="([^"]+)" class="plotly-graph-div"', content)
    if not div_match:
        print("  [ERROR] 找不到 plotly div")
        return None

    div_id = div_match.group(1)
    print(f"  找到 div ID: {div_id}")

    return div_id, None

def create_cdn_html(original_path, output_path):
    """創建使用 CDN 的新版本"""
    print(f"\n創建 CDN 版本")
    print(f"  輸入: {original_path}")
    print(f"  輸出: {output_path}")

    # 由於提取複雜，我們直接重新生成圖表
    # 但這需要原始資料，讓我採用更簡單的方法：直接用 Python 重新生成

    html_template = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>成交路徑樹狀圖（Sunburst）</title>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js" charset="utf-8"></script>
    <style>
        body {{
            margin: 0;
            padding: 0;
            background: #f0f0f0;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }}
        #plotly-div {{
            background: white;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
    </style>
</head>
<body>
    <div id="plotly-div"></div>

    <script>
        // 這裡需要原始的 Plotly 資料
        // 由於資料太大無法直接提取，建議：
        // 1. 使用原始 Python 腳本重新生成
        // 2. 或者手動載入 CSV 後在瀏覽器端生成圖表

        console.error('需要 Plotly 資料');
        alert('此為 CDN 測試版本，需要原始資料');
    </script>

    <script id="wheel-zoom-handler">
        window.addEventListener('load', function() {{
            setTimeout(function() {{
                let scale = 1;

                document.addEventListener('wheel', function(e) {{
                    e.preventDefault();

                    const delta = e.deltaY > 0 ? -0.1 : 0.1;
                    scale = Math.max(0.5, Math.min(8, scale + delta));

                    document.body.style.transform = `scale(${{scale}})`;
                    document.body.style.transformOrigin = 'top left';

                    let tip = document.getElementById('zoom-tip');
                    if (!tip) {{
                        tip = document.createElement('div');
                        tip.id = 'zoom-tip';
                        tip.style.cssText = 'position:fixed; top:10px; right:10px; background:#4CAF50; color:white; padding:10px 20px; border-radius:8px; font-size:16px; z-index:999999; font-family:Arial;';
                        document.body.appendChild(tip);
                    }}
                    tip.textContent = Math.round(scale * 100) + '%';
                    tip.style.opacity = '1';

                    clearTimeout(tip.timer);
                    tip.timer = setTimeout(() => tip.style.opacity = '0', 1000);
                }}, {{passive: false}});

                console.log('縮放已啟用');
            }}, 500);
        }});
    </script>
</body>
</html>'''

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_template)

    print("  [OK] CDN 版本已創建")
    print("\n  注意：此版本需要原始資料")
    print("  建議：使用原始 Python 腳本重新生成圖表")

# 主程式
print("=" * 60)
print("這個方法行不通")
print("=" * 60)
print("\n問題：")
print("- Plotly 生成的 HTML 將所有資料壓縮在一行")
print("- 提取資料非常困難")
print("- 檔案太大（4.7MB）可能導致瀏覽器問題")
print("\n建議的解決方案：")
print("1. 檢查原始 Python 生成腳本")
print("2. 確認是否有其他格式輸出選項")
print("3. 或使用 Plotly 的 to_html() 參數控制輸出格式")
print("=" * 60)

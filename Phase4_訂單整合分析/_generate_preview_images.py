#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成互動式圖表的靜態預覽圖
使用 selenium 或 playwright 截圖
"""

import os
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright

    def capture_screenshot(html_path, output_path, width=1200, height=800):
        """使用 Playwright 截圖"""
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={'width': width, 'height': height})

            # 載入本地 HTML 檔案
            file_url = f'file:///{os.path.abspath(html_path)}'
            page.goto(file_url)

            # 等待圖表載入
            page.wait_for_timeout(3000)

            # 截圖
            page.screenshot(path=output_path)
            browser.close()
            print(f'已生成截圖: {output_path}')

    # 生成兩個預覽圖
    base_path = Path('results_timeseries')

    print('開始生成預覽圖...')

    # Sankey 預覽圖
    capture_screenshot(
        base_path / 'Stage_Flow_Sankey.html',
        base_path / 'Stage_Flow_Sankey_preview.png',
        width=1200,
        height=800
    )

    # Sunburst 預覽圖
    capture_screenshot(
        base_path / 'Tree_Path_Sunburst.html',
        base_path / 'Tree_Path_Sunburst_preview.png',
        width=1200,
        height=800
    )

    print('\n' + '=' * 60)
    print('完成！已生成兩個預覽圖')
    print('- Stage_Flow_Sankey_preview.png')
    print('- Tree_Path_Sunburst_preview.png')
    print('=' * 60)

except ImportError:
    print('錯誤：需要安裝 playwright')
    print('請執行：')
    print('  pip install playwright')
    print('  playwright install chromium')
    print('\n或者手動截圖：')
    print('1. 開啟 Stage_Flow_Sankey.html')
    print('2. 截圖並儲存為 Stage_Flow_Sankey_preview.png')
    print('3. 開啟 Tree_Path_Sunburst.html')
    print('4. 截圖並儲存為 Tree_Path_Sunburst_preview.png')

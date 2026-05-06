#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修正 Phase 4 圖片排列：移除限制寬度的 flex 容器
"""

import re

with open("REPORT.html", "r", encoding="utf-8") as f:
    content = f.read()

# 1. 移除或修改限制寬度的 flex 容器
# 將 display:flex; flex-direction:column; align-items:center 改為簡單的 block
content = re.sub(
    r'<div style="display:flex; flex-direction:column; align-items:center;">',
    '<div>',
    content
)

# 2. 確保 grid 容器設定正確
content = re.sub(
    r'<div style="display:grid; grid-template-columns: repeat\(2, 1fr\); gap:[^;]+; margin:[^;]+; max-width:[^;]+;">',
    '<div style="display:grid; grid-template-columns: repeat(2, 1fr); gap:25px; margin:20px auto; max-width:1400px;">',
    content
)

# 3. 統一所有 Phase 4 圖片的樣式
for i in range(1, 7):
    old_pattern = rf'(<img src="data:image/png;base64,[^"]+"\s+alt="Chart {i}:[^"]+"\s+style=")([^"]+)(")'
    # 固定高度 450px，寬度 100%
    new_style = r'\1width:100%; height:450px; object-fit:contain; cursor:pointer; border:1px solid #444; display:block;\3'
    content = re.sub(old_pattern, new_style, content)

print("儲存修改...")
with open("REPORT.html", "w", encoding="utf-8") as f:
    f.write(content)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(content)

print("\n" + "=" * 60)
print("完成！已移除限制寬度的 flex 容器")
print("- 圖片現在會填滿整個 grid 欄位")
print("- 兩欄並排，最大寬度 1400px")
print("- 固定高度 450px 保持整齊")
print("\n請清除瀏覽器快取並重新載入（Ctrl+Shift+Delete）")
print("=" * 60)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修正 Phase 4 HTML 結構問題：統一所有圖片的容器層級
"""

import re

with open("REPORT.html", "r", encoding="utf-8") as f:
    content = f.read()

# 找到 Phase 4 的六圖區塊
start_marker = '<h3>六圖整合分析（點擊放大）</h3>'
end_marker = '<h3>互動式視覺化'

start_idx = content.find(start_marker)
end_idx = content.find(end_marker, start_idx)

if start_idx == -1 or end_idx == -1:
    print("找不到 Phase 4 區塊！")
    exit(1)

# 提取 Phase 4 區塊
before = content[:start_idx + len(start_marker)]
phase4_block = content[start_idx + len(start_marker):end_idx]
after = content[end_idx:]

# 重建整個區塊（簡化結構）
# 移除所有現有的 div 結構，重新建立一致的結構

# 提取六個圖片區塊（標題 + img 標籤）
charts = []
for i in range(1, 7):
    # 找到每個圖片的標題和 img 標籤
    h4_pattern = rf'<h4[^>]*>([①②③④⑤⑥]) ([^<]+)</h4>'
    img_pattern = rf'<img src="(data:image/png;base64,[^"]+)"\s+alt="Chart {i}:[^"]+"\s+style="[^"]+"\s+onclick="openLB\((\d+)\)"\s+title="[^"]+">'

    h4_match = re.search(h4_pattern, phase4_block)
    img_match = re.search(img_pattern, phase4_block)

    if h4_match and img_match:
        number = h4_match.group(1)
        title = h4_match.group(2)
        img_src = img_match.group(1)
        lb_index = img_match.group(2)

        charts.append({
            'number': number,
            'title': title,
            'src': img_src,
            'index': i,
            'lb_index': lb_index
        })

# 重建 HTML
new_phase4 = f'''

  <div style="display:grid; grid-template-columns: repeat(2, 1fr); gap:25px; margin:20px auto; max-width:1400px;">
'''

for chart in charts:
    new_phase4 += f'''
    <div>
      <h4 style="text-align:center; margin-bottom:10px;">{chart['number']} {chart['title']}</h4>
      <img src="{chart['src']}"
           alt="Chart {chart['index']}: {chart['title']}"
           style="width:100%; height:450px; object-fit:contain; cursor:pointer; border:1px solid #444; display:block;"
           onclick="openLB({chart['lb_index']})"
           title="點擊放大">
    </div>
'''

new_phase4 += '''
  </div>

'''

# 組合回去
content = before + new_phase4 + after

print("儲存修正後的 HTML...")
with open("REPORT.html", "w", encoding="utf-8") as f:
    f.write(content)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(content)

print("\n" + "=" * 60)
print(f"完成！已重建 Phase 4 區塊（找到 {len(charts)} 張圖）")
print("- 統一所有圖片的 HTML 結構")
print("- 每張圖片一層 div 包裹")
print("- Grid 兩欄佈局，寬度 1400px")
print("- 固定高度 450px")
print("\n請重新開啟網頁查看")
print("=" * 60)

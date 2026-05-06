#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修正 Phase 4 HTML 結構 v2：正確提取每張圖片的標題
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

before = content[:start_idx + len(start_marker)]
phase4_block = content[start_idx + len(start_marker):end_idx]
after = content[end_idx:]

# 定義六張圖的標題（手動指定，確保正確）
chart_titles = [
    "各階段成交週期分布",
    "訂單數與平均週期趨勢",
    "訂單金額 vs 成交週期",
    "客戶分群分析",
    "各階段週期分布（箱型圖）",
    "累積分布曲線（CDF）"
]

chart_numbers = ["①", "②", "③", "④", "⑤", "⑥"]

# 提取所有圖片的 base64 資料
img_pattern = r'<img src="(data:image/png;base64,[^"]+)"[^>]+alt="Chart (\d+):'
img_matches = list(re.finditer(img_pattern, phase4_block))

if len(img_matches) != 6:
    print(f"警告：找到 {len(img_matches)} 張圖片（預期 6 張）")

# 提取 lightbox 索引
lb_indices = []
for match in img_matches:
    lb_match = re.search(r'onclick="openLB\((\d+)\)"', phase4_block[match.start():match.end()+200])
    if lb_match:
        lb_indices.append(lb_match.group(1))
    else:
        # 預設從 10 開始
        lb_indices.append(str(10 + len(lb_indices)))

# 建立圖表資料
charts = []
for i in range(min(6, len(img_matches))):
    charts.append({
        'number': chart_numbers[i],
        'title': chart_titles[i],
        'src': img_matches[i].group(1),
        'index': i + 1,
        'lb_index': lb_indices[i] if i < len(lb_indices) else str(10 + i)
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
print(f"完成！已重建 Phase 4 區塊")
print("圖表清單：")
for chart in charts:
    print(f"  {chart['number']} {chart['title']}")
print("\n排版設定：")
print("- Grid 兩欄佈局")
print("- 最大寬度 1400px（置中）")
print("- 固定高度 450px")
print("- 所有圖片結構一致")
print("\n請關閉並重新開啟網頁")
print("=" * 60)

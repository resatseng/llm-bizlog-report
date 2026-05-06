#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新 REPORT.html：
1. 新增 Phase 3 章節及熱圖
2. 將 Phase 4 的 6 張獨立圖表加入 (取代合併圖)
3. 將所有圖片整合至 lightbox 系統
"""

import base64
import re
from pathlib import Path

# 讀取所有圖片並轉換為 base64
def img_to_base64(img_path):
    with open(img_path, "rb") as f:
        return base64.b64encode(f.read()).decode('utf-8')

print("讀取圖片...")

# Phase 3 圖片
phase3_heatmap = img_to_base64("Phase3_痛需熱圖/results/pain_heatmap.png")

# Phase 4 獨立圖表
p4_chart1 = img_to_base64("Phase4_訂單整合分析/results_timeseries/individual_charts/chart1_cycle_distribution.png")
p4_chart2 = img_to_base64("Phase4_訂單整合分析/results_timeseries/individual_charts/chart2_monthly_trend.png")
p4_chart3 = img_to_base64("Phase4_訂單整合分析/results_timeseries/individual_charts/chart3_amount_vs_cycle.png")
p4_chart4 = img_to_base64("Phase4_訂單整合分析/results_timeseries/individual_charts/chart4_customer_segments.png")
p4_chart5 = img_to_base64("Phase4_訂單整合分析/results_timeseries/individual_charts/chart5_cycle_boxplot.png")
p4_chart6 = img_to_base64("Phase4_訂單整合分析/results_timeseries/individual_charts/chart6_cdf.png")

print("讀取 REPORT.html...")
with open("REPORT.html", "r", encoding="utf-8") as f:
    content = f.read()

# 刪除舊的 Phase 4 章節
content = re.sub(
    r'<h2>Phase 4 — 訂單整合分析.*?(?=<h2>結果一覽</h2>)',
    '',
    content,
    flags=re.DOTALL
)

print("建立新的 Phase 3 章節...")
phase3_section = f'''
  <h2>Phase 3 — 痛需熱圖（229+257+310 三輸出）</h2>
  <p>
    整合 Phase 1、Phase 2、Phase M 及商機等級四路資料，生成 <strong>cluster × pain_type</strong> 痛需熱圖，
    並產出三類業務應用輸出。
  </p>

  <h3>痛需熱圖視覺化</h3>
  <p>
    橫軸為 7 種法人聚類（C0-C6），縱軸為不同痛點類型，顏色深淺代表該組合的熱度（出現頻率）。
  </p>
  <div style="text-align:center; margin:20px 0;">
    <img src="data:image/png;base64,{phase3_heatmap}"
         alt="Phase 3 痛需熱圖"
         style="max-width:100%; height:auto; cursor:pointer; border:1px solid #444;"
         onclick="openLB(7)"
         title="點擊放大查看痛需熱圖">
  </div>

  <h3>三類輸出</h3>
  <ul>
    <li><strong>Output 1：推薦業務問項（229 家）</strong> — 基於痛點標籤，為業務人員提供精準提問腳本</li>
    <li><strong>Output 2：開發方案卡（257 組合）</strong> — 高熱痛點組合（heat_score ≥ 0.5），建議對應解決方案</li>
    <li><strong>Output 3：機會卡 B+A 標的（310 家）</strong> — 商機等級 B/A 且有明確痛點的高價值目標客戶</li>
  </ul>

  <h3>關鍵統計</h3>
  <ul>
    <li>整合公司數：206,817 家</li>
    <li>有效痛點標籤：123,893 家（L1 覆蓋率 73.3%）</li>
    <li>痛點組合數：89,710 個</li>
    <li>高熱組合（≥0.5）：257 個</li>
  </ul>
'''

print("建立新的 Phase 4 章節...")
phase4_section = f'''
  <h2>Phase 4 — 訂單整合分析（73,934 筆 / 167.6 億）</h2>
  <p>
    整合 2024-2026 年訂單資料（CRMHC 表），追蹤 14,842 家公司的商機階段演進與成交路徑。
    包含<strong>階段轉換分析</strong>（3,186 次轉換）、<strong>成交路徑追蹤</strong>（73,934 條旅程）、
    <strong>樹狀路徑分析</strong>（1,276 種獨特路徑）。
  </p>

  <h3>六圖整合分析（點擊放大）</h3>

  <div style="display:grid; grid-template-columns: repeat(2, 1fr); gap:20px; margin:20px 0;">
    <div>
      <h4 style="text-align:center; margin-bottom:10px;">① 各階段成交週期分布</h4>
      <img src="data:image/png;base64,{p4_chart1}"
           alt="Chart 1: 各階段成交週期分布"
           style="width:100%; cursor:pointer; border:1px solid #444;"
           onclick="openLB(8)"
           title="點擊放大">
    </div>

    <div>
      <h4 style="text-align:center; margin-bottom:10px;">② 訂單數與平均週期趨勢</h4>
      <img src="data:image/png;base64,{p4_chart2}"
           alt="Chart 2: 訂單數與平均週期"
           style="width:100%; cursor:pointer; border:1px solid #444;"
           onclick="openLB(9)"
           title="點擊放大">
    </div>

    <div>
      <h4 style="text-align:center; margin-bottom:10px;">③ 訂單金額 vs 成交週期</h4>
      <img src="data:image/png;base64,{p4_chart3}"
           alt="Chart 3: 訂單金額 vs 成交週期"
           style="width:100%; cursor:pointer; border:1px solid #444;"
           onclick="openLB(10)"
           title="點擊放大">
    </div>

    <div>
      <h4 style="text-align:center; margin-bottom:10px;">④ 客戶分群分析</h4>
      <img src="data:image/png;base64,{p4_chart4}"
           alt="Chart 4: 客戶分群分析"
           style="width:100%; cursor:pointer; border:1px solid #444;"
           onclick="openLB(11)"
           title="點擊放大">
    </div>

    <div>
      <h4 style="text-align:center; margin-bottom:10px;">⑤ 各階段週期分布（箱型圖）</h4>
      <img src="data:image/png;base64,{p4_chart5}"
           alt="Chart 5: 週期分布箱型圖"
           style="width:100%; cursor:pointer; border:1px solid #444;"
           onclick="openLB(12)"
           title="點擊放大">
    </div>

    <div>
      <h4 style="text-align:center; margin-bottom:10px;">⑥ 累積分布曲線（CDF）</h4>
      <img src="data:image/png;base64,{p4_chart6}"
           alt="Chart 6: 累積分布曲線"
           style="width:100%; cursor:pointer; border:1px solid #444;"
           onclick="openLB(13)"
           title="點擊放大">
    </div>
  </div>

  <h3>互動式視覺化（新視窗開啟）</h3>
  <ul>
    <li><strong>Sankey 階段流向圖：</strong>
      <a href="Phase4_訂單整合分析/results_timeseries/Stage_Flow_Sankey.html" target="_blank" style="color:#4CAF50; text-decoration:underline;">
        Stage_Flow_Sankey.html
      </a> — 追蹤商機階段 E→D→C2→C1→B→A 的流向關係
    </li>
    <li><strong>Sunburst 樹狀路徑圖：</strong>
      <a href="Phase4_訂單整合分析/results_timeseries/Tree_Path_Sunburst.html" target="_blank" style="color:#4CAF50; text-decoration:underline;">
        Tree_Path_Sunburst.html
      </a> — 展示 Top 100 成交路徑的階層結構（可互動縮放）
    </li>
  </ul>

  <h3>關鍵發現</h3>
  <ul>
    <li><strong>高再購路徑：</strong>63 條路徑的老客戶比例 ≥70%（標示 🔴）</li>
    <li><strong>新客路徑：</strong>128 條路徑的新客戶比例 ≥70%（標示 🔵）</li>
    <li><strong>反向流動：</strong>A→C1、B→C2 等反向降級，時間差 >90 天視為再購行為</li>
    <li><strong>單階段成交：</strong>部分公司僅在單一階段（如 B 階段）即完成成交</li>
  </ul>
'''

# 在「結果一覽」之前插入 Phase 3 和 Phase 4 章節
insert_pattern = r'(<h2>結果一覽</h2>)'
combined_sections = phase3_section + '\n' + phase4_section + '\n  '
content = re.sub(insert_pattern, combined_sections + r'\1', content)

print("更新 LB_ITEMS 陣列...")
# 找到 LB_ITEMS 結尾並添加新圖片
new_lb_items = f''',
  {{src:"data:image/png;base64,{phase3_heatmap}", caption:"Phase 3 痛需熱圖"}},
  {{src:"data:image/png;base64,{p4_chart1}", caption:"Phase 4 - Chart 1: 各階段成交週期分布"}},
  {{src:"data:image/png;base64,{p4_chart2}", caption:"Phase 4 - Chart 2: 訂單數與平均週期趨勢"}},
  {{src:"data:image/png;base64,{p4_chart3}", caption:"Phase 4 - Chart 3: 訂單金額 vs 成交週期"}},
  {{src:"data:image/png;base64,{p4_chart4}", caption:"Phase 4 - Chart 4: 客戶分群分析"}},
  {{src:"data:image/png;base64,{p4_chart5}", caption:"Phase 4 - Chart 5: 各階段週期分布（箱型圖）"}},
  {{src:"data:image/png;base64,{p4_chart6}", caption:"Phase 4 - Chart 6: 累積分布曲線（CDF）"}}'''

# 在 LB_ITEMS 陣列結尾添加（在 ]; 之前）
content = re.sub(
    r'(var LB_ITEMS = \[.*?)\];',
    r'\1' + new_lb_items + '\n];',
    content,
    count=1,
    flags=re.DOTALL
)

print("儲存更新後的 REPORT.html...")
with open("REPORT.html", "w", encoding="utf-8") as f:
    f.write(content)

print("同步至 index.html...")
with open("index.html", "w", encoding="utf-8") as f:
    f.write(content)

print("\n" + "=" * 60)
print("完成！已更新：")
print("- Phase 3 章節（含痛需熱圖）")
print("- Phase 4 章節（6 張獨立圖表 + 互動式連結）")
print("- Lightbox 系統（所有圖片可點擊放大）")
print("=" * 60)

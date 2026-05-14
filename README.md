# 痛點需求地圖 - 階段式分析流程

## 資料夾結構

```
prompt定版/
├── Phase1_法人屬性/         # 階段 1：法人基礎屬性萃取
│   ├── results/
│   │   └── company_labels_flat.csv
│   └── README.md
│
├── Phase2_深度標籤/         # 階段 2：L1-L7 深度標籤萃取
│   ├── L-Phase2深度標籤.ipynb
│   ├── results/
│   │   ├── phase2_deep_labels.jsonl (86MB, 173,376 家)
│   │   └── phase2_labels_flat.csv
│   └── README.md
│
├── Phase3_痛需熱圖/         # 階段 3：四路資料整合 + 熱圖生成
│   ├── L-Phase3痛需熱圖.ipynb
│   ├── results/
│   │   ├── company_dim.csv
│   │   ├── pain_heatmap.csv
│   │   ├── pain_heatmap.png
│   │   ├── output1_recommended_questions.csv
│   │   ├── output2_development_cards.csv
│   │   └── output3_opportunity_cards.csv
│   └── README.md
│
├── Phase4_訂單整合分析/     # 階段 4：訂單驗證 + 時間序列路徑分析（v3）
│   ├── L-Phase4訂單整合分析.ipynb
│   ├── results_timeseries/
│   │   ├── C1_stage_conversion_timeseries.csv
│   │   ├── C2_cycle_distribution.csv
│   │   ├── matched_orders.csv
│   │   ├── stage_transitions.csv
│   │   ├── company_stage_paths.csv
│   │   ├── hot_stage_paths.csv
│   │   ├── reverse_transitions.csv
│   │   ├── single_vs_multi_stage.csv
│   │   ├── order_conversion_paths.csv
│   │   ├── hot_conversion_paths.csv
│   │   ├── tree_path_analysis.csv
│   │   ├── conversion_leaf_paths.csv
│   │   ├── repurchase_dominated_paths.csv
│   │   ├── new_customer_dominated_paths.csv
│   │   ├── Phase4_Complete_Visualization_v3.png
│   │   ├── Stage_Flow_Sankey.html
│   │   └── Tree_Path_Sunburst.html
│   └── README.md
│
└── PhaseM_聚類分析/         # 階段 M：法人分層聚類（C0-C6）
    ├── L-PhaseM分層聚類.ipynb
    ├── results/
    │   ├── company_clusters.csv (18MB, 206,797 家)
    │   ├── cluster_pca_map.png
    │   ├── cluster_radar.png
    │   └── radar_c0~c6.png
    └── README.md
```

## 執行順序

### 1️⃣ Phase 1：法人屬性標籤
- **目的**：從業務日誌萃取 8 大基礎屬性
- **輸出**：`company_labels_flat.csv` (178,790 家公司)

### 2️⃣ Phase M：聚類分析
- **目的**：基於 Phase 1 屬性，聚類為 7 種法人類型
- **輸入**：Phase 1 結果
- **輸出**：`company_clusters.csv` (206,797 家公司)
- **聚類**：C0 微型內銷、C1 標準內銷、C2 大型外商、C3 多面型強者、C4 品牌驅動、C5 家族外銷、C6 外資貿易

### 3️⃣ Phase 2：深度標籤萃取
- **目的**：使用 LLM 萃取 L1-L7 七層銷售情報
- **輸入**：業務日誌（SQL Server）
- **輸出**：`phase2_deep_labels.jsonl` (173,376 家公司)
- **處理**：Gemini 2.5 Flash，28 小時批次處理
- **覆蓋率**：L1 痛點 73.3%，123,893 家有效

### 4️⃣ Phase 3：痛需熱圖
- **目的**：四路資料整合，生成痛需熱圖與業務應用輸出
- **輸入**：Phase 1 + Phase 2 + Phase M + 商機等級
- **輸出**：
  - 痛需熱圖（cluster × pain_type）
  - Output 1：推薦業務問項（229 家）
  - Output 2：開發方案卡（257 組合）
  - Output 3：機會卡 B+A 標的（310 家）

### 5️⃣ Phase 4：訂單整合分析 v3 ⭐ NEW
- **目的**：時間序列路徑分析，追蹤商機階段演進與成交路徑
- **輸入**：Phase 1-3 + 訂單資料（CRMHC 表）+ 業務日誌時間序列
- **訂單規模**：73,934 筆（2024-2026）/ 14,842 家公司 / 總金額 167.6 億
- **三大核心分析**：
  - **階段轉換分析**：3,186 次轉換，識別正向晉升 vs 反向降級（A→C1 為再購）
  - **成交路徑分析**：73,934 條完整旅程，標記單階段 vs 多階段轉換
  - **樹狀路徑分析**：1,276 種獨特路徑，識別高再購路徑（≥70%）vs 新客路徑（≤30%）
- **視覺化輸出**：
  - 6 張整合圖表（週期分布、客戶分群、時間趨勢）
  - Sankey 階段流向圖（互動式）
  - Sunburst 樹狀路徑圖（互動式）

## 資料流向

```
業務日誌 (SQL Server CRMGY)
    ↓
Phase 1 → 8 大屬性 ────────────┐
    ↓                         ↓
Phase M → 7 種聚類 ──┐    Phase 3 四路合流
                     ↓         ↑
Phase 2 → L1-L7 標籤 ─┴────────┤
                               ↑
商機等級 (lead_stage_results) ─┘
                ↓
    痛需熱圖 + 三輸出
                ↓
                │
    ┌───────────┴──────────┐
    ↓                      ↓
Phase 4 五路整合     訂單資料 (CRMHC)
    ↓
階段轉換分析 + 成交路徑追蹤 + 樹狀路徑分群 + 互動式視覺化
```

## 關鍵指標

| 指標 | 數值 |
|------|------|
| 總公司數 | 206,817 家 |
| Phase 2 處理成功 | 173,376 家 (84%) |
| L1 痛點覆蓋 | 123,893 家 (73.3%) |
| 商機等級覆蓋 | 2,085 家 |
| B+A 高溫標的 | 310 家 |
| 痛點組合數 | 89,710 個 |
| 高熱組合 (≥0.5) | 257 個 |
| **訂單筆數（2024-2026）** | **73,934 筆** |
| **成交公司數** | **14,842 家** |
| **總訂單金額** | **167.6 億元** |
| **整體成交率** | **7.2%** |
| **階段轉換次數** | **3,186 次** |
| **獨特路徑數** | **1,276 條** |
| **高再購路徑（≥70%）** | **63 條** |
| **新客路徑（≤30%）** | **128 條** |
| **Phase 4 輸出檔案** | **15 CSV + 3 圖表** |

## 技術棧

- **LLM**: Google Gemini 2.5 Flash (Vertex AI)
- **資料庫**: SQL Server (CRMGY 業務日誌表 + CRMHC 訂單表)
- **分析**: Python, Pandas, NumPy, Scikit-learn
- **視覺化**: Matplotlib, Plotly (Sankey, Sunburst)
- **平行處理**: ThreadPoolExecutor, RateLimiter

## 🌐 線上展示（GitHub Pages）

### 📄 技術文件
**URL**: https://resatseng.github.io/llm-bizlog-report/

完整的業務日誌 LLM 智慧萃取系統技術文件，包含系統架構、實作細節、效能分析等。

### 🏗️ 系統架構圖集
**URL**: https://resatseng.github.io/llm-bizlog-report/architecture.html

痛點需求地圖系統的完整架構視覺化，包含：
- 總體系統架構圖
- 資料流程與四路整合
- Phase 1-4 執行流程
- 技術架構與資料庫設計
- 互動式 Mermaid.js 圖表

---

## 更新日誌

- 2026-05-14：新增系統架構圖集頁面（architecture.html）
- 2026-05-13：修正 Phase 4 圖表黑底配色
- 2026-05-05：
  - Phase 4 v3 時間序列路徑分析完成（階段轉換、成交路徑、樹狀路徑分析）
  - 新增互動式視覺化（Sankey 階段流向圖、Sunburst 樹狀路徑圖）
  - 識別 1,276 條獨特路徑，標記高再購路徑（63 條）與新客路徑（128 條）
  - 完整輸出：15 CSV 檔案 + 3 圖表（靜態 + 互動式）
  - 整合 CRMHC 訂單資料（73,934 筆 / 167.6 億元）
- 2026-05-04：Phase 2 完成（173,376 家）
- 2026-04-30：修正商機等級 ID 格式對齊
- 2026-04-23：Phase M 聚類完成（7 clusters）

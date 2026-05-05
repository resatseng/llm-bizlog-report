# Phase 3：痛需熱圖 + 三輸出

## 目的
整合多路資料，生成痛需熱圖並產出三種業務應用輸出。

## 程式
- `L-Phase3痛需熱圖.ipynb` - 資料整合與熱圖生成

## 輸入資料（四路合流）

| 來源 | 檔案 | 說明 |
|------|------|------|
| Phase 2 | `phase2_deep_labels.jsonl` | L1–L7 深度標籤 |
| 商機等級 | `lead_stage_results.csv` | E/D/C2/C1/B/A 銷售階段 |
| Phase M | `company_clusters.csv` | 法人聚類 C0–C6 |
| Phase 1 | `company_labels_flat.csv` | 法人 8 大屬性 |

## 輸出檔案

### 核心資料表
1. `company_dim.csv` - 公司維度表（206,817 家）
2. `layer_coverage.csv` - L1-L7 層覆蓋旗標
3. `pain_records.csv` - L1 痛點明細（123,893 筆）
4. `pain_heatmap.csv` - 痛需熱圖核心表（cluster × pain_type 組合）

### 三輸出
1. **`output1_recommended_questions.csv`** - 推薦業務問項
   - 有 L1 痛點但 L4/L5 空白 且商機溫度 ≥ C2 的公司
   - 業務應補問「議題驅動力」、「評估方案」
   
2. **`output2_development_cards.csv`** - 推薦開發方案卡
   - heat_score ≥ 0.5 的痛點組合
   - 需求明確 + 商機熱 + 規模夠 → 值得開發產品/功能

3. **`output3_opportunity_cards.csv`** - 機會卡（B+A 高溫標的）
   - best_stage 為 B 或 A 的公司（約 309 家）
   - 商機最熱、最近成交可能最高

### 視覺化
- `pain_heatmap.png` - 法人類型 × L1 痛點類型熱圖

## 熱度公式
```
heat_score = ba_ratio × 0.5 + urgency_high_pct × 0.3 + scale_score × 0.2
```

其中：
- `ba_ratio`: B+A 階段公司比例
- `urgency_high_pct`: 高緊迫度比例
- `scale_score`: 規模分數（log 標準化）

## 法人聚類名稱
- C0 微型內銷
- C1 標準內銷
- C2 大型外商
- C3 多面型強者
- C4 品牌驅動
- C5 家族外銷
- C6 外資貿易

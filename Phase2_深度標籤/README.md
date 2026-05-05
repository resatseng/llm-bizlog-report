# Phase 2：深度標籤萃取

## 目的
對每家公司的業務日誌進行深度結構化標籤萃取，萃取 L1-L7 七層銷售情報。

## 程式
- `L-Phase2深度標籤.ipynb` - 使用 Gemini 2.5 Flash 批次萃取深度標籤

## 輸入資料
- `phase_l_final.csv` - L 層分類結果（1,802,590 筆日報、178,790 家公司）
- SQL Server 業務日誌（每家公司每層取最近 3 篇）

## 處理統計
- 已處理：173,376 家公司
- L1 痛點覆蓋率：73.3% (127,126 家)
- 錯誤率：0.7% (1,154 筆)

## 輸出
- `results/phase2_deep_labels.jsonl` - JSONL 格式深度標籤（86MB）
- `results/phase2_labels_flat.csv` - 扁平化 CSV（57MB，172,222 行）

## 七層標籤結構

| L 層 | 萃取欄位 |
|------|---------|
| L1 起因/阻礙 | pain_type, impact, urgency |
| L2 角色壓力 | role, pressure_source, kpi |
| L3 戰略目標 | goal_type, timeline, core_kpi |
| L4 產業議題 | issue_name, driver, stance |
| L5 問項精煉 | eval_items, competitors, decision_criteria |
| L6 動態屬性 | direction, trigger, current_temp |
| L7 實戰對策 | outcome_type, key_factor, next_step |

## LLM 設定
- Model: gemini-2.5-flash (Vertex AI)
- RPM Limit: 100
- Workers: 15
- Temperature: 0.1
- 預估耗時：28 小時（實際完成：~6 小時，使用斷點續跑）

## 後續使用
- Phase 3 使用 L1 痛點資料生成痛需熱圖

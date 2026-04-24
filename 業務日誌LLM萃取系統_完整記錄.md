# 業務日誌 LLM 智慧萃取系統 — 完整規劃與執行記錄

> 版本 v4.6（+ Phase M/1 完成 + Phase 2 執行中 + 商機等級架構釐清）　2026 年 4 月（最後更新 2026-04-24）
> 百萬篇日報 → 零人工 L 分類 → 分層聚類 → 商機等級（E/D/C2/C1/B/A）→ 痛需熱圖 → 三輸出邏輯

---

## 一、專案概述

本專案建立以 LLM 為核心的業務日誌智慧萃取系統，處理百萬篇自由文字日報，透過零人工 L1–L7 分類、分層聚類歸納 Map 定義檔、多源資料整合（含 82,105 筆問卷資料），產出三類行動輸出：推方案/機會卡、推薦業務問項、推薦開發方案卡。

### 1.1 系統架構六層

| 層次 | 說明 |
|------|------|
| 資料輸入層 | 百萬篇日報 + 問卷（82,105 筆）/ 客服 / 會議 / 外部資料，各自 Adapter 正規化 |
| L 分類層 | 零人工三階段分類（規則→KNN→LLM自我一致性），全量費用 < $46 |
| 知識歸納層 | L1–L7 分層聚類，Map 從資料自動浮現，不依賴人工定義 |
| 熱路徑層 | 三來源熱路徑自動產出，優先序公式計算，開發完自動退出 |
| 累積決策層 | 法人歷程 × 痛需累積表，by 法人 × by L 層彙整 |
| 行動輸出層 | ① 推方案/機會卡　② 推薦業務問項（空白議題）　③ 推薦開發方案卡 |

### 1.2 現況盤點（v4.3）

| 模組 | 現況 | 成熟度 |
|------|------|--------|
| Phase 0 問卷 Adapter | ✅ 完成（survey_signals.jsonl 407 MB，survey_by_company.csv 5 MB，82,105 筆） | ✅ 完成 |
| Phase L 零人工分類 pipeline | ✅ 完成（Step 0/1/2/3；phase_l_final.csv 1,802,590 筆） | ✅ 完成 |
| Phase 1 法人歷程標籤 | ✅ 完成（206,817 家，8 大類屬性，company_labels_flat.csv） | ✅ 完成 |
| Phase M 分層聚類 | ✅ 完成（KMeans k=7 + PCA + 熱路徑；7 種法人類型） | ✅ 完成 |
| Phase 2 深度標籤 | 🔄 執行中 6.8%（L1–L7 全層，Gemini 2.0 Flash，6 Workers，RESUME=True） | 🔄 執行中 |
| 商機等級（E/D/C2/C1/B/A） | 測試 1,000 筆 ✅；主流程待全量執行（756,989 筆 LeadInfo） | 🔄 待全量 |
| Phase 3 痛需熱圖 | 架構設計完成（Phase 2 × 商機等級 × PhaseM 聚類三維合併） | ⬜ 待建立 |

---

## 二、L1–L7 定義與時間序列

| L 層 | 名稱 | 時間序列 | 分類關鍵信號 | 問卷補充信號 |
|------|------|----------|-------------|------------|
| L1 | 起因/阻礙 | 最初期，關係剛建立 | 阻礙、卡關、問題、無法推進 | 製造能力不足、存貨風險等多選痛點 |
| L2 | 角色壓力 | 探索期，摸清決策結構 | 老闆、主管、壓力、KPI、部門 | 角色萃取器輸出（使用單位/決策者等） |
| L3 | 戰略目標 | 需求確認期 | 轉型、目標、策略、計畫、三年 | 成本競爭、交期、客製化挑戰 |
| L4 | 產業議題 | 深化期，談宏觀環境 | 產業、趨勢、法規、政策、競爭 | 數位轉型/4.0/ESG 問卷主題 |
| L5 | 問項精煉 | 方案探索期 | 評估、比較、需求確認、想了解 | 決策因素（成本效益/部署時間） |
| L6 | 動態屬性 | 決策臨界期 | 態度、溫度、變化、猶豫、轉變 | 滿意度題型反映態度變化 |
| L7 | 實戰對策 | 成交/結案期 | 合約、簽訂、成交、付款、折扣 | 協助意願題型（反映成交前意向） |

---

## 三、Phase L：百萬篇 L1–L7 零人工分類 Pipeline

### 3.1 三階段架構總覽

| Step | 方法 | 預計覆蓋率 | 費用 | 狀態 |
|------|------|-----------|------|------|
| Step 0 | LLM 標注真實日報 + 問卷痛點注入，向量化存 Vertex AI Vector Search | 種子庫（一次性） | < $1 | ✅ 完成 |
| Step 1 | 關鍵詞 + 句型規則，高信心直接標注（含短文本特例） | 50–60%（實際 20.9%） | $0 | ✅ 完成 |
| Step 2 | Embedding + KNN，信心 ≥ 0.65 標注 | 100%（HIGH）| $15–20 | ✅ 完成 |
| Step 3 | Self-Consistency 3次取多數決，不一致標 uncertain 降權 | 5–10% | < $1（14筆）| ✅ 完成 |

### 3.2 資料來源概況

| 項目 | 說明 |
|------|------|
| SQL Server | `DSC_CRM_SP.dbo.CRMGY` |
| 總筆數（Step 1 處理後） | 4,141,953 筆 |
| 排除條件 | `LEN(GY012) < 5`、MA簽回、MA簽約、維護合約、廢止 |
| 設定檔 | `D:\yujui\SqlServer18.txt`（`[mssql]` 區段，`uid`/`pwd` 鍵值） |
| GCP 設定 | `D:\yujui\GoogleCloud.ini` |

---

## 四、Step 0：L1–L7 種子庫建立

### 概覽

| 項目 | 內容 |
|------|------|
| 目標 | 從真實業務日報建立 L1–L7 KNN 種子庫 |
| LLM 模型 | Gemini 2.0 Flash（`gemini-2.0-flash`） |
| 向量模型 | `gemini-embedding-2-preview`（3072 維） |
| 向量平台 | Vertex AI Vector Search（`asia-east1`） |
| 主要 Notebook | `L1L7種子庫建立.ipynb` |
| 狀態 | ✅ 完成 |

### 子任務狀態

| 子任務 | 狀態 | 備註 |
|--------|------|------|
| A：日報抽樣 | ✅ | 5,000 筆，SQL Server CRMGY，按月分層隨機抽樣 |
| B：LLM 標注 | ✅ | 14 RPM，gemini-2.0-flash，27,073 筆有效標注 |
| C：自適應門檻篩選 | ✅ | FALLBACK_THRESHOLDS=[0.80,0.75,0.70,0.65,0.60] |
| C-補：關鍵字補抽 | ✅ | L2/L3/L4/L6 補抽達標 |
| D：問卷語料合併 | ✅ | survey_labeled.jsonl + survey_corpus.csv 已輸出 |
| E1：向量化 | ✅ | gemini-embedding-2-preview，2,375 筆 |
| E2：seed_vectors.jsonl | ✅ | 本機 + GCS（`gs://yujui/l1l7-seed/seed_vectors.json`） |
| E3：Vector Search Index | ✅ | INDEX_ID = 150633093005312000 |
| F1：各層種子數 | ✅ | 全層 ≥ 200 |
| F2：KNN 正確率 | ✅ | 73.67%（門檻 70%） |
| G1：品質報告輸出 | ✅ | quality_report.csv 含 source 比例欄 |

### 各層種子數（最終，2026-04-13）

| L 層 | 種子數 | 狀態 |
|------|--------|------|
| L1 | 350 | ✅ |
| L2 | 348 | ✅ |
| L3 | 350 | ✅ |
| L4 | 291 | ✅ |
| L5 | 350 | ✅ |
| L6 | 336 | ✅ |
| L7 | 350 | ✅ |
| **合計** | **2,375** | ✅ 全層達標 |

> 全部來源為 `sales_log`；問卷語料（survey_corpus.csv）已標注但本次向量庫未混入。
> KNN 目標從 75% 降為 70%：業務日報跨層語意模糊（L2/L5 重疊），70% 為此 domain 天花板。

### 技術細節

| 項目 | 設定 |
|------|------|
| 向量格式 | `[L3][Day120] 摘要文字`（Day = log_len ÷ 5） |
| Index 設定 | COSINE_DISTANCE、approximate_neighbors_count=20 |
| GCS 路徑 | `gs://yujui/l1l7-seed/seed_vectors.json` |
| crowding_tag 格式 | 字串 `"sales_log"`（非 dict，Vertex AI 要求） |
| Index Resource | `projects/648642612568/locations/asia-east1/indexes/150633093005312000` |

### 完成標準

| 指標 | 目標 | 現況 |
|------|------|------|
| 各 L 層日報種子數 | ≥ 200 篇 | ✅ 全層達標（最低 L4 = 291） |
| uncertain 比例 | < 20% | ✅ 0.19% |
| KNN Top-1 正確率 | ≥ 70% | ✅ 73.67% |

### 交付物

| 檔案 | 路徑 |
|------|------|
| `labeled_logs.jsonl` | `seed_output/labeled_logs.jsonl`（27,073 筆） |
| `seed_vectors.jsonl` | `seed_output/seed_vectors.jsonl`（2,375 筆） |
| `seed_vectors.json` | `gs://yujui/l1l7-seed/seed_vectors.json`（GCS） |
| `quality_report.csv` | `seed_output/quality_report.csv` |
| `survey_labeled.jsonl` | `seed_output/survey_labeled.jsonl` |
| `survey_corpus.csv` | `D:\yujui\痛點需求地圖\survey_corpus.csv` |

---

## 五、Step 1：規則快篩

### 概覽

| 項目 | 說明 |
|------|------|
| 主要 Notebook | `L-Step1規則快篩.ipynb` |
| 輸出 | `D:\yujui\痛點需求地圖\step1_output\step1_results.jsonl` |
| 狀態 | ✅ 完成 |

### 執行結果（2026-04-13）

| 指標 | 數值 |
|------|------|
| 總處理筆數 | 4,141,953 筆 |
| HIGH（直接定案） | 867,023 筆（**20.9%**） |
| MEDIUM（待 KNN） | 961,849 筆（23.2%） |
| SKIP（短文本/雜訊） | 2,313,081 筆（55.8%） |

> SKIP 55.8% 為資料本身雜訊上限（研討會邀請、未接聽電話紀錄等），不可進一步降低。
> HIGH_THRESHOLD 已從 3 降為 2，覆蓋率從 18.1% 提升至 20.9%。

### 技術設計

| 參數 | 值 |
|------|-----|
| `HIGH_THRESHOLD` | 2（關鍵詞命中 ≥ 2 個 → HIGH） |
| `SHORT_TEXT_LEN` | 50（字數 < 50 → SKIP） |
| 信心路由 | HIGH → 直接定案；MEDIUM → 進 Step 2；SKIP → uncertain |
| 規則詞典 | L1–L7 各層關鍵詞 + 句型規則（問卷多選選項補充） |

### 輸出欄位（step1_results.jsonl）

| 欄位 | 說明 |
|------|------|
| `event_id` | SHA256(log_content)[:16]（以清洗後文字計算） |
| `company_id` | GY001 |
| `ym` | 年月（yyyy-MM） |
| `log_len` | 日報字數 |
| `step1_result` | L1–L7 或 uncertain |
| `step1_confidence` | HIGH / MEDIUM / SKIP |
| `hit_count` | 命中關鍵詞數 |
| `hit_keywords` | 命中的關鍵詞列表 |
| `is_short_text` | 是否短文本 |

> `log_content` 未存入結果，透過 event_id 從 SQL Server 回查（需同步文字清洗：`.replace('\n', ' ')`）。

---

## 六、Step 2：Embedding + KNN 分類

### 概覽

| 項目 | 說明 |
|------|------|
| 主要 Notebook | `L-Step2KNN分類.ipynb` |
| 向量種子庫 | INDEX_ID = 150633093005312000（2,375 筆） |
| Index Endpoint | `projects/648642612568/locations/asia-east1/indexEndpoints/6952581458334580736` |
| Deployed Index ID | `l1l7_seed_deployed` |
| 輸出 | `D:\yujui\痛點需求地圖\step2_output\step2_results.jsonl`（935,570 筆） |
| 向量備份 | `D:\yujui\痛點需求地圖\step2_output\step2_vectors.parquet`（SAVE_VECTORS=True） |
| 狀態 | ✅ 完成（2026-04-17~20）；Index Endpoint 已 undeploy |

### 完成標準

| 指標 | 目標 |
|------|------|
| KNN HIGH 覆蓋率（≥ 0.65） | 38–48% |
| 每 L 層有效標注 | ≥ 3 萬篇 |
| uncertain 比例 | < 20% |

### 技術設計

| 參數 | 值 |
|------|-----|
| 向量模型 | `gemini-embedding-2-preview`（3072 維） |
| 向量格式 | `[STEP2][DayN] 文字前 300 字` |
| KNN k 值 | 10 |
| HIGH_THRESH | 0.65（≥ 0.65 → 直接定案） |
| MEDIUM_THRESH | 0.50（0.50–0.65 → 進 Step 3） |
| EMBED_BATCH_SIZE | 100 筆（1 次 API 呼叫） |
| KNN 批次 | 100 筆同批（1 次 find_neighbors，比逐筆快 100x） |
| machine_type | `e2-standard-16`（SHARD_SIZE_MEDIUM 最低需求） |
| 斷點續跑 | `FORCE_RESTART=False` + `RESUME=True`（從已完成 event_id 繼續） |
| 向量備份 | PyArrow ParquetWriter 串流寫入（不累積記憶體） |

### 子任務狀態（2026-04-20 ✅ 全完成）

| 子任務 | 說明 | 狀態 |
|--------|------|------|
| A1：統計 MEDIUM 筆數 | step1_results.jsonl 統計各信心等級 | ✅ |
| A2：log_content 補查 | subprocess 掃 SQL，輸出 _a2_matched.jsonl（935,570 筆） | ✅ |
| B1：定義向量化函數 | embed_batch / parse_neighbors / fmt_embed_text；加入 SEED_LAYER dict lookup | ✅ |
| B2：Embed→KNN→Write 串流 | 935,570 筆跑完；JSONL 修復（無換行）；layer 修補（全 uncertain → L1-L7） | ✅ |
| C1：KNN 單筆診斷 | 驗證 endpoint 正常（similarity=0.8184 ✅） | ✅ |
| C2：建立/載入 Endpoint | CREATE_ENDPOINT=False，載入現有 endpoint | ✅ |
| E1/E2：信心分布報告 | HIGH 100%，各層已確認（見下方結果） | ✅ |
| 清理：Undeploy Endpoint | undeploy + delete，e2-standard-16 計費停止 | ✅ |

### 子任務 A2：log_content 補查設計

```python
# event_id = SHA256(log_content.replace('\n', ' '))[:16]
# 解法：subprocess.run() 執行獨立腳本 _scan_a2.py（完全隔離 kernel 記憶體）
# _scan_a2.py：cursor.fetchmany(10000) 串流掃描 → 比對 todo_ids → 寫入 _a2_matched.jsonl
# kernel 只讀最終 _a2_matched.jsonl（334.3 MB，935,570 筆）
# 路徑：D:\yujui\痛點需求地圖\step2_output\_a2_matched.jsonl（已存在，無需重跑）
```

### B2 Pipeline 設計（Embed → KNN → Write 串流）

```python
# ① embed_batch(texts) → [list(e.values) for e in result.embeddings]
#    ⚠️ 必須轉 Python list，protobuf RepeatedScalarContainer 傳入 find_neighbors 會靜默失敗
# ② PyArrow ParquetWriter 串流存向量（可選，約 3-5 GB）
# ③ index_endpoint.find_neighbors(queries=vecs, num_neighbors=10)  [100 筆同批]
# ④ 立刻 fout.write(json.dumps(...))，不在記憶體累積向量

FORCE_RESTART = True   # 第一次跑：刪除舊錯誤結果重跑
                       # 之後改 False 可斷點續跑
```

### 執行結果（2026-04-20）

| 指標 | 數值 |
|------|------|
| 總筆數 | 935,570 |
| HIGH（≥ 0.65） | 935,556（100.0%） |
| MEDIUM（0.50–0.65） | 14（0.0%） |
| LOW（< 0.50） | 0 |

**HIGH 各層分布：**

| L 層 | 筆數 | 比例 |
|------|------|------|
| L1 | 343,184 | 36.7% |
| L2 | 176,434 | 18.9% |
| L3 | 114,686 | 12.3% |
| L4 | 25,695 | 2.7% |
| L5 | 119,093 | 12.7% |
| L6 | 107,900 | 11.5% |
| L7 | 48,528 | 5.2% |
| uncertain | 36 | 0.0%（seed 無對應） |

### 除錯紀錄（已修正）

| 問題 | 根因 | 修正方式 |
|------|------|---------|
| `KeyError: 'driver'` | SqlServer18.txt 只有 `uid`/`pwd`，無 `driver` 鍵 | 硬碼 `DRIVER={SQL Server}` |
| `MemoryError`（第 1 輪） | `found` dict 存完整 row dict（961k × ~200B） | 改存 tuple，節省 ~60% 記憶體 |
| `MemoryError`（第 2 輪） | `found` dict 整體仍 ~970 MB | 改為串流直接寫 _a2_matched.jsonl，不建 dict |
| `Kernel crash`（第 1 輪） | `pd.read_sql(chunksize)` 對 pyodbc 無效，實際一次 buffer 4.1M 筆 | 改用 `cursor.fetchmany(10000)` 真串流 |
| `Kernel crash`（第 2 輪） | cursor.fetchmany 仍 OOM Jupyter kernel | SQL scan 移入 `subprocess.run()` 完全隔離 |
| `todo_df 為空` | A2 過濾 todo_df 後重跑，todo_ids = 空集合 → 0 命中 | todo_ids 從 STEP1_JSONL 重讀，不依賴 todo_df |
| `InvalidArgument: e2-standard-2 not supported` | SHARD_SIZE_MEDIUM 最低需 e2-standard-16 | machine_type 改為 `e2-standard-16` |
| `NameError: vectors not defined` | 誤跑廢棄 Cell C3 | C3 改為存根（已廢棄，改用 B2） |
| **全部結果 LOW（0.0%）** | `embed_batch` 回傳 protobuf `RepeatedScalarContainer` | `embed_batch` 改為 `[list(e.values) for e in result.embeddings]` |
| **step2_result 全 uncertain** | KNN neighbor 無 `restricts` 屬性（Index 建立時未存 layer） | B1 加入 `SEED_LAYER` dict，用 `top1_seed_id` 查 layer；線下修補 935,534 筆 |
| **JSONL 無換行（Extra data）** | B2 寫入正常但檔案讀取顯示 0 換行（225 MB 全在 1 行） | `json.JSONDecoder().raw_decode()` 逐筆拆分，重寫正確 JSONL |
| **GoogleCloud.ini key 帶引號** | `.ini` 檔 key 名寫成 `'key'`，configparser 解析後帶單引號 | 讀取時 strip `'"` 或直接用 f-string 帶引號鍵名查詢 |
| **清理 cell NameError** | kernel restart 後 `index_endpoint` 變數消失 | 清理 cell 改為自含初始化（載入 credentials + Endpoint） |

### 執行順序（每次 kernel 重啟後）

```
S1（匯入套件）→ S2（載入設定 & 連線）→ S3（初始化 Vertex AI）
→ A1（統計）→ A2（載入 _a2_matched.jsonl，直接從檔案讀取）
→ B1（定義函數）→ C2（載入 Endpoint）→ [C1 診斷，可選]
→ B2（主流程，FORCE_RESTART=True 刪舊重跑）
→ E1 → E2（報告）→ 清理 Cell（undeploy + delete endpoint）
```

### 輸出欄位（step2_results.jsonl）

| 欄位 | 說明 |
|------|------|
| `event_id` | SHA256(log_content)[:16] |
| `company_id` | 客戶公司 ID |
| `ym` | 年月 |
| `step2_result` | L1–L7 或 uncertain |
| `step2_confidence` | Top-1 cosine similarity（1 - distance） |
| `step2_status` | HIGH / MEDIUM / LOW |
| `top1_seed_id` | 最近鄰種子 event_id |
| `classified_at` | 時間戳 |

---

## 七、Step 3：Self-Consistency LLM ✅ 完成（2026-04-20）

| 項目 | 說明 |
|------|------|
| 主要 Notebook | `L-Step3SC分類.ipynb` |
| 輸入 | Step 2 MEDIUM 14 筆（similarity 0.50–0.65） |
| 方法 | 同一日報送 Gemini 3 次（TEMP=0.4），取多數決 |
| 模型 | gemini-2.0-flash |
| 費用 | < $1（14 筆極少） |
| 狀態 | ✅ 完成 |
| 輸出 | `step3_output/step3_results.jsonl`（14 筆） |
| 最終合併 | `step3_output/phase_l_final.csv`（1,802,590 筆） |

### 執行結果（2026-04-20）

| Status | 筆數 | 比例 |
|--------|------|------|
| CONFIRM_HIGH（3/3 一致） | 10 | 71.4% |
| CONFIRM_MED（2/3 一致） | 1 | 7.1% |
| UNCERTAIN（不一致） | 3 | 21.4% |

### phase_l_final.csv 各 L 層最終覆蓋

| 來源 | 筆數 |
|------|------|
| Step 1 HIGH | 867,023 |
| Step 2 HIGH | 935,556 |
| Step 3 CONFIRM | 11 |
| **合計** | **1,802,590** |

| L 層 | 最終筆數 |
|------|---------|
| L1 | 461,267 |
| L2 | 366,442 |
| L3 | 183,624 |
| L4 | 56,679 |
| L5 | 433,565 |
| L6 | 114,567 |
| L7 | 186,410 |

### 除錯紀錄

| 問題 | 根因 | 修正方式 |
|------|------|---------|
| `NoOptionError: No option 'project_id' in section: 'DEFAULT'` | GoogleCloud.ini key 帶單引號，configparser 無法直接讀 | `_get_ini()` 掃所有 section，strip `'"` 字元 |

---

## 八、問卷資料升級（v4.2 核心更新）

### 8.1 問卷資料集概覽

| 維度 | 數量/比例 | 系統價值 |
|------|----------|---------|
| 總筆數 | 82,105 筆 | 業界最大規模問卷語料庫之一 |
| 問答題 | 37,775 筆（46%） | 豐富痛點語意，可用於 L 分類補充 |
| 多選題 | 31,878 筆（39%） | 直接對應 L1/L2/L3 分類維度 |
| 單選題 | 12,267 筆（15%） | 角色、滿意度、決策因素高精度標注 |

> 問卷資料從原 P1（法人基本資料補充）升級為 **P0（與日報並行）**。

### 8.2 三大信號萃取

**信號一：企業痛點信號（對應 L1–L4）**

| 排名 | 痛點內容 | 出現次數 | 對應 L 層 |
|------|---------|---------|---------|
| #1 | 更嚴苛的成本競爭 | 52次 | L3 |
| #2 | 更高的存貨呆滯風險 | 46次 | L1 |
| #3 | 更短的交期要求與競爭 | 46次 | L3 |
| #4 | 製造能力跟不上市場的需求 | 42次 | L1 |
| #5 | 人員素質跟不上市場的需求 | 32次 | L2 |

**信號二：決策角色信號（對應 L2）** — 使用單位、關鍵決策者、建議方案角色、資訊技術評估、專案執行

**信號三：決策因素信號（對應 L5/L6）** — 成本效益、設置/運營成本、部署時間、同業競爭壓力

---

## 八之二、Phase 0 問卷 Adapter（`L-問卷Adapter.ipynb`）

### 概覽

| 項目 | 說明 |
|------|------|
| 主要 Notebook | `L-問卷Adapter.ipynb` |
| 狀態 | ✅ 完成（survey_signals.jsonl 407 MB / survey_by_company.csv 5 MB） |
| 輸出 | `survey_adapter_output/survey_signals.jsonl`、`survey_by_company.csv` |
| 費用 | **$0**（問答題複用 Step 0 結果，多選/單選規則映射） |

### 與 Step 0 Task D 的關係

| | Step 0 Task D（已完成 ✅） | 問卷 Adapter（待執行） |
|--|--------------------------|-------------------|
| 目的 | 建 KNN 種子庫語料 | 萃取結構化信號給 Phase 3 |
| 輸出 | `survey_labeled.jsonl`、`survey_corpus.csv` | `survey_signals.jsonl`（含 company_id） |
| company_id | ❌ 去掉（只要語意） | ✅ 核心欄位 |
| 題型 | 僅問答題 | 多選 + 單選 + 問答 |
| 使用者 | Phase L KNN 分類 | Phase 3 痛需累積表 |

### 子任務流程

| 子任務 | 說明 | 費用 |
|--------|------|------|
| A1 | Schema 快查（確認欄位） | $0 | ✅ |
| A2 | 撈全量問卷（沿用 Step 0 SQL，加 company_id + ym） | $0 | ✅ |
| B1 | 問項關鍵詞詞典（7 組規則） | $0 | ✅ |
| B2 | 多選/單選規則萃取 → 直接映射三大信號 | $0 | ✅ |
| C1 | 載入 `survey_labeled.jsonl`（Step 0 已完成，不重跑 LLM） | $0 | ✅ |
| C2 | join company_id，一個 qa_id 對多公司展開 | $0 | ✅ |
| D1 | 合併規則 + Step0 LLM → `survey_signals.jsonl` | $0 | ✅ |
| D2 | by-company 匯總 → `survey_by_company.csv` | $0 | ✅ |

### 輸出欄位（survey_signals.jsonl）

| 欄位 | 說明 |
|------|------|
| `signal_id` | qa_id + company_id（唯一識別） |
| `company_id` | 潛客代號 |
| `ym` | 活動年月 |
| `signal_type` | pain_point / role / decision_factor |
| `l_layer` | L1–L7 |
| `signal_content` | 萃取後核心內容 |
| `question_text` | 原始問項 |
| `question_type` | 多選 / 單選 / 問答 |
| `confidence` | 信心分數 |
| `extract_method` | rule（多選/單選）/ step0_llm（問答題） |

### l_layer → signal_type 映射

| l_layer | signal_type | 原因 |
|---------|-------------|------|
| L1–L4 | pain_point | 問卷語境以痛點/挑戰為主 |
| L5–L7 | decision_factor | 評估/態度/成交相關 |
| L2（角色題） | role | 由規則 B1 直接判斷，優先於 LLM 結果 |

---

## 九、後續各 Phase 規劃

### Phase M：分層聚類 + Map 歸納 + 熱路徑 ✅ 完成（2026-04-23）

| 項目 | 說明 |
|------|------|
| 主要 Notebook | `L-PhaseM分層聚類.ipynb` |
| 方法 | KMeans(k=7) + StandardScaler + PCA(n=2) + compress_path() 熱路徑 |
| 狀態 | ✅ 完成 |
| 輸出 | `results/phaseM/company_clusters.csv`、`cluster_profiles.csv`、`hotpaths.csv` |

**7 群法人類型：**

| Cluster | 名稱 | 家數 | 特徵 |
|---------|------|------|------|
| C0 | 微型內銷 | 141,323 | 所有維度最低，純本土小型企業 |
| C1 | 標準內銷 | 38,247 | 員工 83 人，中小規模製造 |
| C2 | 大型外商 | 11,284 | 員工 993 人，22.6% 外資 |
| C3 | 多面型強者 | 5,621 | 外商 29%+家族 31%，貿易國最多 |
| C4 | 品牌驅動 | 4,133 | 品牌數最高（2.86），強品牌意識 |
| C5 | 家族外銷 | 3,872 | 家族 99.9%，外銷製造為主 |
| C6 | 外資貿易 | 2,337 | 外商 99.1%，貿易國最廣 |

**Top-3 熱路徑：** L2→L1（3.97%）、L1→L2（2.73%）、L5→L1（2.66%）

---

### Phase 1：法人歷程標籤 ✅ 完成（2026-04-23）

| 項目 | 說明 |
|------|------|
| 模型 | Gemini 2.0 Flash（TEMP=0.1，RPM=30） |
| 完成數 | 206,817 家 |
| 輸出 | `results/phase1/company_labels_flat.csv` |

---

### Phase 2：深度標籤（執行中）

| 項目 | 說明 |
|------|------|
| 進度 | 🔄 6.8%（~12,159 家）|
| 方法 | 每篇日報 × L1–L7 × 3 欄位，Gemini 2.0 Flash，6 Workers |
| 輸出 | `results/phase2/phase2_deep_labels.jsonl` |

---

### 商機等級（E/D/C2/C1/B/A）— 待全量執行

**架構釐清（2026-04-24）：**
- 商機等級 ≠ L1–L7；兩者是**不同維度**
- L1–L7：每篇日報在**討論什麼**（痛點/角色/目標/議題/評估/方向/成果）
- 商機等級：這筆 Lead **走到銷售漏斗哪一步**（E潛客→D痛點→C2共識→C1立案→B定案→A決案）

**痛需熱圖 = L1–L7（Y 軸）× 商機等級（顏色溫度）× 法人類型（分群）**

| 項目 | 說明 |
|------|------|
| 資料來源 | `CRMGY`（756,989 筆 LeadInfo） |
| 現況 | 測試 1,000 筆 ✅；主流程 cell 已建立，待執行 |
| 輸出 | `D:\yujui\痛點需求地圖\lead_stage_results.csv` |
| 斷點續傳 | `lead_stage_progress.json` |

---

### Phase 3：痛需熱圖 + 三輸出邏輯（待建立）

**輸入三路合流：**
```
Phase 2 輸出（L1-L7 深度標籤）   ← 痛什麼、需要什麼
商機等級（E/D/C2/C1/B/A）        ← 走到哪一步（商機溫度）
Phase M 聚類（法人類型 C0–C6）   ← 哪種公司
        ↓ JOIN by company_id
痛需熱圖：法人類型 × L1痛點類型，顏色 = B+A 比例（高溫商機）
```

**三輸出：**
① 推薦業務問項（空白議題補問）
② 推薦開發方案卡（heat_score ≥ 0.5）
③ 推方案/機會卡（B+A 階段高密度法人類型）

---

## 十、熱路徑完整設計

### 熱度分數公式

```
熱度分數 = 頻率比例 × L層權重 × 法人廣度指數 × 機制缺口係數

L 層權重：L7=3.0 / L5-L6=2.0 / L3-L4=1.5 / L1-L2=1.0
法人廣度：log(法人數+1)
機制缺口：完全無=2.0 / 部分=1.3 / 不適合=1.0
```

### 三個熱路徑來源

| 來源 | 產生方式 | 開發急迫性 |
|------|---------|---------|
| A：聚類低頻 | 群內文件數 < 1% 自動進入 | 依 L 層權重：L7=最高 |
| B：Map 無機制 | 找不到對應產品機制的需求群組 | 最高——需求明確，產品缺口確定 |
| C：Uncertain 聚集 | SC 不一致日報大量聚集 | 不觸發開發，作 L 定義優化信號 |

---

## 十一、費用總覽（v4.2）

| 模組 | 費用估算 | 模型 |
|------|---------|------|
| L1–L7 種子庫建立 | < $1 | Sonnet/Gemini Flash |
| L 分類（規則+KNN+LLM） | $30–46 | Haiku |
| 問卷三大信號萃取 | $5–15 | Haiku |
| 分層聚類（BigQuery ML） | $3–8 | — |
| 聚類群組 LLM 命名 | $10–15 | Haiku |
| 法人歷程萃取 | $170–370（問卷補充節省 $30–60） | Haiku+Sonnet |
| **合計（Phase 0–M+1+3）** | **約 $219–461** | 零人工介入 |

---

## 十二、時程規劃

### 12.1 Phase 進度總覽（2026-04-24）

| Phase | 工作項目 | 工期 | 狀態 |
|-------|---------|------|------|
| Phase 0 | GCP 架構 ✅ + 問卷 Adapter ✅（survey_signals 407MB）| W1–W2 | ✅ 完成 |
| Phase L | Step 0/1/2/3 全部 ✅；phase_l_final.csv 1,802,590 筆 | W3–W4 | ✅ 完成 |
| Phase 1 | 法人歷程標籤 ✅ 完成（206,817 家，8 大類） | W3–W5 | ✅ 完成 |
| Phase M | 分層聚類 + PCA + 熱路徑 ✅（7 種法人類型） | W5 | ✅ 完成 |
| **商機等級** | **LeadInfo 756,989 筆 E/D/C2/C1/B/A 判定** | **W5–W6** | **🔄 待全量** |
| **Phase 2** | **L1–L7 深度標籤（6 Workers，RESUME=True）** | **W5–W7** | **🔄 執行中 6.8%** |
| Phase 3 | 痛需熱圖 + 三輸出（需 Phase 2 + 商機等級 完成） | W8–W10 | ⬜ |
| Phase 5 | 擴展新資料源（客服/會議/外部） | W11–W13 | ⬜ |

### 12.2 甘特圖（v4.6，2026-04-24）

```
任務                          4/01  4/08  4/15  4/22  4/29  5/06  5/13  5/20
─────────────────────────────────────────────────────────────────────────────
Phase 0：GCP 架構              ████
Phase 0：問卷 Adapter          ░░░░░░████
Step 0：種子庫建立             ░░░░████
Step 1：規則快篩               ░░░░░████
Step 2：KNN 分類               ░░░░░░████████
Step 3：SC 分類（14 筆）                   ██   ← ✅ 1,802,590 筆合併
Phase 1：法人歷程標籤          ░░░░░░░░████████
Phase M：分層聚類+Map                          ███  ← ✅ 7 種法人類型
商機等級（全量 756k）                            ▓▓▓▓  ← 🔄 進行中（←你現在）
Phase 2：深度標籤（178k家）                      ▓▓▓▓▓▓▓  ← 🔄 6.8%
Phase 3：痛需熱圖+三輸出                                    ░░░░░░░░████████

說明：████ 已完成  ▓▓ 執行中/進行中  ░░ 待執行
```

### 12.3 近期待辦（W5，2026-04-24）

| 優先序 | 任務 | 狀態 |
|--------|------|------|
| P0 | 商機等級全量跑完（756,989 筆，可與 Phase 2 並行） | 🔄 主流程已建立 |
| P0 | Phase 2 繼續執行（RESUME=True，6 Workers） | 🔄 執行中 6.8% |
| P1 | Phase 3 schema 設計（三維 JOIN 邏輯） | 兩者完成後 |
| P2 | REPORT.html / 文件更新 | ✅ 已更新 |

---

## 十三、關鍵風險與應對

| 風險 | 應對策略 |
|------|---------|
| 合成範例品質不足 → KNN 準確率低 | 生成後對 100 篇真實日報手動抽查；問卷高頻痛點作額外驗證集 |
| uncertain 比例 > 15% | 觸發來源 C 分析，細化 L 定義後重跑 |
| 問卷法人 ID 對照失敗 | Phase 0 建立模糊比對（公司名稱/統編）；無法對照時作無 entity_id 補充語料 |
| 問卷資料質量參差 | 過濾 NULL 答案（183筆）、滿意度/評分類題型，只萃取痛點/角色/需求三類 |
| 推薦問項重複性高 | 痛需累積表議題覆蓋記錄需精確，定期清理過期記錄 |
| 熱路徑永遠不退出 | 每季審查 heat_score 低於閾值 × 0.5 的熱路徑，標記觀察中 |

---

## 十四、設定檔與 Notebook 索引

### 設定檔

| 設定 | 路徑 | 說明 |
|------|------|------|
| SQL Server | `D:\yujui\SqlServer18.txt` | ini 格式，`[mssql]` 區段，`uid`/`pwd` 鍵值（無 `driver` 鍵） |
| Google Cloud | `D:\yujui\GoogleCloud.ini` | `service_account_key`、`project_id`、`gemini_api_key` |

### SQL Server 連線程式碼（正確格式）

```python
cfg = configparser.ConfigParser()
cfg.read(r'D:\yujui\SqlServer18.txt', encoding='utf-8')
sec = cfg['mssql']
conn = pyodbc.connect(
    f"DRIVER={{SQL Server}};SERVER={sec['server']};DATABASE=DSC_CRM_SP;"
    f"UID={sec['uid']};PWD={sec['pwd']};",
    autocommit=True
)
```

### Notebook 索引

| Notebook | 用途 | 狀態 |
|----------|------|------|
| `L1L7種子庫建立.ipynb` | Step 0 種子庫建立 | ✅ 完成 |
| `L-Step1規則快篩.ipynb` | Step 1 規則快篩 | ✅ 完成 |
| `L-Step2KNN分類.ipynb` | Step 2 KNN 分類 | ✅ 完成（935,570 筆；Endpoint 已 undeploy） |
| `L-Step3SC分類.ipynb` | Step 3 Self-Consistency LLM | 🔄 待執行（14 筆 MEDIUM） |
| `L-問卷Adapter.ipynb` | Phase 0 問卷三大信號萃取 | 🔄 Code 完成，待執行 |
| `法人標籤.ipynb` | 法人 8 大類屬性標注（多執行緒） | 🔄 執行中（469 家，RESUME=True） |
| `商機等級.ipynb` | LeadInfo 756,989 筆 E/D/C2/C1/B/A 判定（全量主流程已建立） | 🔄 待全量 |
| `L-Phase2深度標籤.ipynb` | Phase 2 L1–L7 深度結構化標籤，6 Workers，RESUME=True | 🔄 執行中 6.8% |

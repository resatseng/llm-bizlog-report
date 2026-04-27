# 業務日誌 LLM 智慧萃取系統

百萬篇業務日報 → 零人工 L1–L7 分類 → 法人標籤 → 深度標籤 → 痛需地圖

## 系統架構

```
業務日報（SQL）
    │
    ├─ Phase 0：GCP 地基 + 問卷 Adapter
    │       └─ survey_signals.jsonl（82,105 筆問卷三大信號）
    │
    ├─ Phase L：L1–L7 零人工分類（1,802,590 筆）
    │       ├─ Step 0：LLM 標注種子庫（2,375 筆，KNN 正確率 73.67%）
    │       ├─ Step 1：關鍵詞規則快篩（HIGH 867,023 筆）
    │       ├─ Step 2：Embedding + KNN 分類（935,570 筆）
    │       └─ Step 3：Self-Consistency LLM（14 筆模糊案例）
    │
    ├─ Phase 1：法人標籤（8 大類，206,817 家）
    │       └─ company_labels.jsonl
    │
    ├─ Phase M：分層聚類 + Map + 熱路徑
    │       └─ KMeans(k=7) × PCA × Top-30 熱路徑
    │       └─ REPORT.html（互動式 PCA + 雷達圖，公開於 GitHub Pages）
    │
    ├─ 商機等級：LeadInfo E/D/C2/C1/B/A 銷售漏斗（執行中）
    │       └─ 三層 pipeline：關鍵詞快篩 → TF-IDF KNN → Batch LLM
    │
    ├─ Phase 2：日報深度標籤（L1–L7 結構化，執行中）
    │       └─ phase2_deep_labels.jsonl
    │
    └─ Phase 3：痛需累積表 + 三輸出（待建立）
```

## L 層定義

| 層 | 名稱 | 萃取內容 |
|----|------|----------|
| L1 | 痛點層 | 痛點類型 / 衝擊程度 / 緊迫度 |
| L2 | 角色層 | 決策角色 / 壓力來源 / 負責 KPI |
| L3 | 目標層 | 目標類型 / 時程 / 核心 KPI |
| L4 | 議題層 | 議題名稱 / 驅動因素 / 客戶立場 |
| L5 | 評估層 | 評估項目 / 競爭者 / 決策標準 |
| L6 | 方向層 | 策略方向 / 觸發事件 / 當前溫度 |
| L7 | 成果層 | 結果類型 / 關鍵因素 / 下一步 |

## Notebooks 說明

| 檔案 | 說明 |
|------|------|
| `L1L7種子庫建立.ipynb` | Phase L Step 0：LLM 標注 + KNN 種子庫 |
| `L-Step1規則快篩.ipynb` | Phase L Step 1：關鍵詞規則快篩 |
| `L-Step2KNN分類.ipynb` | Phase L Step 2：Embedding + KNN 分類 |
| `L-Step3SC分類.ipynb` | Phase L Step 3：Self-Consistency LLM |
| `L-問卷Adapter.ipynb` | Phase 0：問卷三大信號萃取 |
| `法人標籤.ipynb` | Phase 1：法人歷程標籤（8 大類） |
| `L-PhaseM分層聚類.ipynb` | Phase M：KMeans + PCA + 熱路徑 |
| `L-Phase2深度標籤.ipynb` | Phase 2：L1–L7 深度結構化標籤 |
| `商機等級.ipynb` | 商機等級三層 pipeline（關鍵詞→TF-IDF KNN→Batch LLM） |

## 生成腳本

| 檔案 | 說明 |
|------|------|
| `_gen_pptx.py` | 生成進度簡報 PPT |
| `_gen_charts.py` | 生成 PCA 散點圖 + 雷達圖（PNG） |
| `_gen_report3.py` | 生成互動式 REPORT.html（Plotly PCA + 雷達圖 Lightbox，PCA 群組篩選） |
| `_gen_corp_label.py` | 生成法人標籤 Notebook |
| `_gen_phaseM.py` | 生成 Phase M Notebook |
| `_gen_phase2.py` | 生成 Phase 2 Notebook |

## 環境需求

```bash
pip install google-genai pyodbc pandas tqdm scikit-learn numpy
```

- Python 3.10+
- Gemini API Key（`D:\yujui\GoogleCloud.ini`）
- SQL Server 連線（`D:\yujui\SqlServer18.txt`）

## 設定檔格式

**GoogleCloud.ini**
```ini
[gcp]
gemini_api_key = YOUR_API_KEY
```

**SqlServer18.txt**
```ini
[mssql]
server = YOUR_SERVER_IP
uid = YOUR_USERNAME
pwd = YOUR_PASSWORD
```

## 進度

| Phase | 狀態 | 數量 | 說明 |
|-------|------|------|------|
| Phase 0 | ✅ 完成 | 82,105 筆問卷 | 三大信號（Pain/Need/Insight） |
| Phase L | ✅ 完成 | 1,802,590 筆日報 | Step 0/1/2/3 零人工分類 |
| Phase 1 | ✅ 完成 | 206,817 家法人 | 8 大類屬性標籤 |
| Phase M | ✅ 完成 | 7 clusters | KMeans+PCA+熱路徑；REPORT.html 公開於 GitHub Pages |
| 商機等級 | 🔄 執行中 2.0% | 756,989 筆 LeadInfo | 三層 pipeline：關鍵詞→TF-IDF KNN→Batch LLM（零 API 呼叫） |
| Phase 2 | 🔄 執行中 40.5% | ~178,790 行 | L1–L7 全層深度標籤（72,420 行已完成） |
| Phase 3 | ⬜ 待建立 | — | 痛需熱圖（Phase 2 × 商機等級 × PhaseM） |

## 架構關鍵釐清

痛需熱圖由**兩個獨立維度**合成：

| 維度 | 工具 | 回答的問題 |
|------|------|-----------|
| L1–L7 | Phase 2 深度標籤 | 客戶在**討論什麼**（痛點/角色/目標…） |
| 商機等級 | 商機等級.ipynb | 這筆 Lead **走到哪一步**（E→D→C2→C1→B→A） |

熱圖 = L1-L7（Y 軸）× 法人類型（X 軸），顏色深淺 = B+A 高階商機比例

## 互動式儀表板

REPORT.html 已公開於 GitHub Pages：https://resatseng.github.io/llm-bizlog-report/

- PCA 散點圖：可依法人類型群組（C0–C6）篩選，支援全選 / 全消
- 雷達圖：各群組 7 維特徵值，含單位（%、人、國、個）
- Lightbox：點擊雷達縮圖可放大顯示

---
*最後更新：2026-04-27*

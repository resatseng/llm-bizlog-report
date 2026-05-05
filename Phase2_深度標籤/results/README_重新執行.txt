=================================================================
Phase 2 深度標籤 - 重新執行指南
=================================================================

修正完成時間：2026-04-30 16:36
修正內容：SQL 查詢欄位錯誤（GY002 → GY003）

-----------------------------------------------------------------
執行步驟：
-----------------------------------------------------------------

1. 開啟 Jupyter Notebook
   檔案：D:\yujui\痛點需求地圖\prompt定版\L-Phase2深度標籤.ipynb

2. 依序執行以下 Cells：

   [ ] Cell 1 - 匯入套件 & 全域設定
       → 檢查輸出：MODEL=gemini-2.5-flash  RPM=100  WORKERS=15

   [ ] Cell 2 - 載入設定 & 連線
       → 檢查輸出：Vertex AI 連線成功、SQL 連線成功

   [ ] Cell A1 - 載入 phase_l_final.csv
       → 檢查輸出：唯一公司數：170,945 家

   [ ] Cell A2 - Resume 檢查
       → 預期輸出：從頭開始，共 170,945 家

   [ ] Cell B1 - SQL 查詢函數（✅ 已修正！）
       → 檢查輸出：B1 SQL 函數定義完成（已修正 GY003 日期欄位）

   [ ] Cell B2 - Prompt & LLM 函數
       → 檢查輸出：B2 LLM 函數定義完成（含 retry）

   [ ] Cell B3 - 🚀 主流程執行
       → 這個 Cell 會執行 ~29 小時

3. 執行後 15 分鐘，檢查成功率：

   在新 cell 中執行以下程式碼：

   ```python
   import json
   from pathlib import Path

   file = Path(r"D:\yujui\痛點需求地圖\phase2_output\phase2_deep_labels.jsonl")
   if file.exists():
       lines = [json.loads(l) for l in file.read_text(encoding='utf-8').strip().split('\n') if l.strip()]
       success = sum(1 for r in lines if r.get('labels') and '_error' not in r.get('labels',{}))
       empty = sum(1 for r in lines if not r.get('labels') or r['labels'] == {})
       total = len(lines)

       print(f"Total: {total:,}")
       print(f"Success: {success:,} ({success/total*100:.1f}%)")
       print(f"Empty: {empty:,} ({empty/total*100:.1f}%)")

       # 樣本檢查
       if total > 0:
           sample = lines[0]
           print(f"\n樣本記錄：")
           print(f"  company_id: {sample.get('company_id')}")
           print(f"  l_layers: {sample.get('l_layers')}")
           print(f"  labels 是否有內容: {bool(sample.get('labels'))}")
   ```

   預期結果：
   - ✅ Success 應該 > 50%（不再是 0.9%）
   - ✅ Empty 應該 < 20%（不再是 99%）

-----------------------------------------------------------------
預估執行時間：
-----------------------------------------------------------------

總公司數：170,945 家
RPM 限制：100 次/分鐘
並發數：15 workers

預估時間：~29 小時

開始時間：____________________
預計完成：約 29 小時後

-----------------------------------------------------------------
備份檔案位置：
-----------------------------------------------------------------

D:\yujui\痛點需求地圖\phase2_output\
  - phase2_deep_labels_backup_20260430_114911.jsonl (59MB - 最早的備份)
  - phase2_deep_labels_error_ym_20260430_163550.jsonl (3.5MB - YM錯誤版本)

=================================================================

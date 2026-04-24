# -*- coding: utf-8 -*-
import json

def cc(cid, src):
    """code cell"""
    return {"cell_type":"code","id":cid,"metadata":{},"outputs":[],"execution_count":None,"source":src}
def mc(cid, src):
    """markdown cell"""
    return {"cell_type":"markdown","id":cid,"metadata":{},"source":src}

# ─────────────────────────────────────────────────────────
# Cell source strings (all plain strings, no triple-quote nesting)
# ─────────────────────────────────────────────────────────

SRC_S0 = "!pip install google-genai pyodbc pandas tqdm"

SRC_S1 = "\n".join([
    "import os, re, json, time, hashlib, configparser",
    "from pathlib import Path",
    "from datetime import datetime",
    "from tqdm.auto import tqdm",
    "import pandas as pd",
    "",
    "# ── 路徑 ──────────────────────────────────────────────",
    'BASE_DIR   = Path(r"D:\\yujui\\痛點需求地圖")',
    'OUTPUT_DIR = BASE_DIR / "corp_label_output"',
    "OUTPUT_DIR.mkdir(parents=True, exist_ok=True)",
    "",
    'RESULT_JSONL  = OUTPUT_DIR / "company_labels.jsonl"',
    'PROGRESS_FILE = OUTPUT_DIR / "_progress.json"',
    "",
    "# ── LLM 設定 ──────────────────────────────────────────",
    'MODEL          = "gemini-2.0-flash"',
    "TEMP           = 0.1",
    "RPM_LIMIT      = 14",
    "SLEEP_PER_CALL = 60 / RPM_LIMIT   # ≈ 4.3 秒",
    "",
    "# ── 撈取設定 ──────────────────────────────────────────",
    "TOP_N_LOGS  = 20    # 每家公司取最近 N 篇日報",
    "MIN_LOG_LEN = 30    # 最短日報字數",
    "",
    'print("設定完成")',
    'print(f"  OUTPUT_DIR : {OUTPUT_DIR}")',
    'print(f"  MODEL={MODEL}  RPM={RPM_LIMIT}  TOP_N={TOP_N_LOGS}")',
])

SRC_S2 = "\n".join([
    "import pyodbc",
    "from google import genai",
    "",
    "# ── SQL Server ────────────────────────────────────────",
    "cfg = configparser.ConfigParser()",
    'cfg.read(r"D:\\yujui\\SqlServer18.txt", encoding="utf-8")',
    'sec = cfg["mssql"]',
    "conn = pyodbc.connect(",
    '    f"DRIVER={{SQL Server}};SERVER={sec[\'server\']};DATABASE=DSC_CRM_SP;"',
    '    f"UID={sec[\'uid\']};PWD={sec[\'pwd\']};",',
    "    autocommit=True,",
    ")",
    'print("SQL Server 連線成功")',
    "",
    "# ── Gemini ────────────────────────────────────────────",
    "gcfg = configparser.ConfigParser()",
    'gcfg.read(r"D:\\yujui\\GoogleCloud.ini", encoding="utf-8")',
    "# 嘗試常見的 key 名稱",
    'for key in ("gemini_api_key","api_key","GEMINI_API_KEY"):',
    "    try:",
    '        _api_key = gcfg.get("DEFAULT", key)',
    "        break",
    "    except:",
    "        _api_key = None",
    "if not _api_key:",
    '    raise RuntimeError("找不到 Gemini API Key，請確認 GoogleCloud.ini 的 key 名稱")',
    "",
    "client = genai.Client(api_key=_api_key)",
    'print(f"Gemini 連線成功（key={key}）")',
])

SRC_A1 = "\n".join([
    "# ── A1：統計公司數 ───────────────────────────────────",
    "cursor = conn.cursor()",
    "sql_cnt = (",
    '    "SELECT COUNT(DISTINCT GY001) AS company_cnt "',
    '    "FROM CRMGY "',
    '    "WHERE LEN(GY012) >= 30 "',
    "    \"  AND GY012 NOT LIKE '%MA簽回%' \"",
    "    \"  AND GY012 NOT LIKE '%MA簽約%' \"",
    "    \"  AND GY012 NOT LIKE '%維護合約%'\"",
    ")",
    "cursor.execute(sql_cnt)",
    "company_cnt = cursor.fetchone()[0]",
    'print(f"符合條件的公司數：{company_cnt:,} 家")',
    "est_h = company_cnt * SLEEP_PER_CALL / 3600",
    'print(f"預估耗時（{RPM_LIMIT} RPM）：{est_h:.1f} 小時")',
    'print(f"建議：使用付費 API 提高 RPM 可大幅縮短")',
])

SRC_A2 = "\n".join([
    "# ── A2：撈取每家公司最近 N 篇日報 ────────────────────",
    "# 用 ROW_NUMBER + Python 篩選，避免 STRING_AGG / STRING_SPLIT 版本限制",
    "",
    "SQL = (",
    '    "SELECT GY001 AS company_id, "',
    '    "       GY012 AS log_content, "',
    '    "       GY003 AS log_date, "',
    '    "       ROW_NUMBER() OVER (PARTITION BY GY001 ORDER BY GY003 DESC, GY022 DESC) AS rn "',
    '    "FROM CRMGY "',
    '    "WHERE LEN(GY012) >= 30 "',
    "    \"  AND GY012 NOT LIKE '%MA簽回%' \"",
    "    \"  AND GY012 NOT LIKE '%MA簽約%' \"",
    "    \"  AND GY012 NOT LIKE '%維護合約%' \"",
    '    "  AND GY001 IS NOT NULL"',
    ")",
    "",
    'print(f"撈取中（取每家公司最近 {TOP_N_LOGS} 篇）...")',
    "logs_df = pd.read_sql(SQL, conn)",
    'logs_df = logs_df[logs_df["rn"] <= TOP_N_LOGS].copy()',
    '\'logs_df["log_content"] = logs_df["log_content"].astype(str).str.replace("\\\\n"," ").str.strip()\'',
    "",
    "# 每家公司合併為一段文字",
    "company_texts = (",
    '    logs_df.sort_values(["company_id","rn"])',
    '    .groupby("company_id")["log_content"]',
    '    .apply(lambda x: "\\n---\\n".join(x.tolist()))',
    "    .reset_index()",
    '    .rename(columns={"log_content":"combined_logs"})',
    ")",
    "",
    'print(f"公司數：{len(company_texts):,} 家")',
    "print(f\"平均日報數：{logs_df.groupby('company_id').size().mean():.1f} 篇\")",
    "company_texts.head(2)",
])

# Fix the str.replace line (avoid nested quote issues in list)
SRC_A2 = SRC_A2.replace(
    "'logs_df[\"log_content\"] = logs_df[\"log_content\"].astype(str).str.replace(\"\\\\n\",\" \").str.strip()'",
    'logs_df["log_content"] = logs_df["log_content"].astype(str).str.replace("\\n"," ").str.strip()'
)

SRC_B1 = "\n".join([
    "# ── B1：Prompt + 呼叫函數 ────────────────────────────",
    "from google.genai import types as genai_types",
    "import re",
    "",
    "SYSTEM_PROMPT = (",
    '    "你是企業情報萃取專家。根據業務日報內容，萃取這家公司的結構化資訊。\\n"',
    '    "若某項資訊在日報中未明確提及，該欄位回傳 null，不要猜測。\\n\\n"',
    '    "請回傳以下 JSON（不加說明文字）：\\n"',
    '    "{\\n"',
    '    "  \\"基本資料\\": {\\n"',
    '    "    \\"外商\\": true/false/null,\\n"',
    '    "    \\"家族企業\\": true/false/null,\\n"',
    '    "    \\"商業模式\\": \\"B2B\\"/\\"B2C\\"/\\"B2B2C\\"/\\"其他\\"/null,\\n"',
    '    "    \\"員工人數\\": \\"<100\\"/\\"100-499\\"/\\"500-999\\"/\\"1000+\\"/null\\n"',
    '    "  },\\n"',
    '    "  \\"聯絡人\\": {\\n"',
    '    "    \\"決策者\\": [\\"姓名或職稱\\"],\\n"',
    '    "    \\"家族企業人員\\": [\\"姓名及關係，如老闆娘、二代\\"]\\n"',
    '    "  },\\n"',
    '    "  \\"進出口資訊\\": {\\"國家\\": [\\"進出口往來國家名稱\\"]},\\n"',
    '    "  \\"銷售資訊\\": {\\"競爭者\\": [\\"競爭公司名稱\\"]},\\n"',
    '    "  \\"集團資訊\\": {\\n"',
    '    "    \\"集團\\": \\"集團名稱或null\\",\\n"',
    '    "    \\"母公司\\": \\"母公司名稱或null\\",\\n"',
    '    "    \\"關係企業\\": [\\"關聯公司名稱\\"],\\n"',
    '    "    \\"分公司\\": [\\"分公司名稱或地點\\"],\\n"',
    '    "    \\"品牌名稱\\": [\\"品牌名稱\\"]\\n"',
    '    "  },\\n"',
    '    "  \\"偏好及總結\\": {\\"關注議題\\": [\\"關注主題，限5個以內，如：數位轉型、降本、ESG\\"]},\\n"',
    '    "  \\"產業\\": {\\"產業龍頭\\": true/false/null},\\n"',
    '    "  \\"產業鏈\\": {\\n"',
    '    "    \\"法人的客戶\\": [\\"此公司的下游客戶名稱\\"],\\n"',
    '    "    \\"法人的供應商\\": [\\"此公司的上游供應商名稱\\"]\\n"',
    '    "  }\\n"',
    '    "}"',
    ")",
    "",
    "_JSON_PAT = re.compile(r'{[\\s\\S]+}')",
    "",
    "def extract_labels(company_id, combined_logs):",
    '    """送 LLM 萃取 8 大類標籤，失敗回傳空結構"""',
    "    empty = {",
    '        "基本資料":{"外商":None,"家族企業":None,"商業模式":None,"員工人數":None},',
    '        "聯絡人":{"決策者":[],"家族企業人員":[]},',
    '        "進出口資訊":{"國家":[]},',
    '        "銷售資訊":{"競爭者":[]},',
    '        "集團資訊":{"集團":None,"母公司":None,"關係企業":[],"分公司":[],"品牌名稱":[]},',
    '        "偏好及總結":{"關注議題":[]},',
    '        "產業":{"產業龍頭":None},',
    '        "產業鏈":{"法人的客戶":[],"法人的供應商":[]},',
    "    }",
    "    try:",
    "        resp = client.models.generate_content(",
    "            model=MODEL,",
    '            contents=f"以下是公司 {company_id} 的業務日報（最近{TOP_N_LOGS}篇）：\\n\\n{combined_logs[:3000]}",',
    "            config=genai_types.GenerateContentConfig(",
    "                system_instruction=SYSTEM_PROMPT,",
    "                temperature=TEMP,",
    '                response_mime_type="application/json",',
    "            ),",
    "        )",
    "        m = _JSON_PAT.search(resp.text.strip())",
    "        if not m:",
    "            return empty",
    "        return json.loads(m.group())",
    "    except Exception as e:",
    "        return empty",
    "",
    'print("B1 函數定義完成")',
])

SRC_B2 = "\n".join([
    "# ── B2：批次萃取（斷點續跑）────────────────────────────",
    "RESUME = True",
    "",
    "def load_progress():",
    "    if PROGRESS_FILE.exists():",
    '        return set(json.loads(PROGRESS_FILE.read_text())["done"])',
    "    return set()",
    "",
    "def save_progress(done):",
    '    PROGRESS_FILE.write_text(json.dumps({"done": list(done), "updated_at": datetime.now().isoformat()}))',
    "",
    "done_ids = load_progress() if RESUME else set()",
    "if done_ids:",
    '    print(f"斷點續跑：已完成 {len(done_ids):,} 家")',
    "",
    'run_df = company_texts[~company_texts["company_id"].isin(done_ids)].reset_index(drop=True)',
    "total  = len(run_df)",
    'print(f"待處理：{total:,} 家")',
    "",
    "written = errors = 0",
    "",
    'with open(RESULT_JSONL, "a", encoding="utf-8") as fout:',
    '    for _, row in tqdm(run_df.iterrows(), total=total, desc="法人標籤萃取"):',
    '        cid  = row["company_id"]',
    '        logs = row["combined_logs"]',
    "        try:",
    "            labels = extract_labels(cid, logs)",
    "        except Exception as e:",
    '            print(f"[錯誤] {cid}: {e}")',
    "            errors += 1",
    "            time.sleep(2)",
    "            continue",
    "",
    "        fout.write(json.dumps({",
    '            "company_id":    cid,',
    '            "labels":        labels,',
    '            "log_count":     logs.count("---") + 1,',
    '            "extracted_at":  datetime.now().isoformat(),',
    "        }, ensure_ascii=False) + \"\\n\")",
    "        done_ids.add(cid)",
    "        written += 1",
    "",
    "        if written % 100 == 0:",
    "            save_progress(done_ids)",
    "",
    "        time.sleep(SLEEP_PER_CALL)",
    "",
    "save_progress(done_ids)",
    'print(f"\\n完成：{written:,} 家 → {RESULT_JSONL}")',
    'if errors: print(f"⚠️  錯誤：{errors} 家")',
])

SRC_E1 = "\n".join([
    "# ── E1：覆蓋率統計 ──────────────────────────────────────",
    'results = [json.loads(l) for l in open(RESULT_JSONL, encoding="utf-8") if l.strip()]',
    "total_r  = len(results)",
    'print(f"法人標籤結果：{total_r:,} 家\\n")',
    "",
    "def pct(lst, key_path):",
    '    """計算某欄位非 null/非空的比例"""',
    "    count = 0",
    "    for r in lst:",
    '        val = r["labels"]',
    "        for k in key_path:",
    "            val = val.get(k) if isinstance(val, dict) else None",
    "            if val is None: break",
    '        if val not in (None, [], ""): count += 1',
    "    return count, count/total_r*100 if total_r else 0",
    "",
    "checks = [",
    '    (["基本資料","外商"],    "外商"),',
    '    (["基本資料","家族企業"], "家族企業"),',
    '    (["基本資料","商業模式"], "商業模式"),',
    '    (["基本資料","員工人數"], "員工人數"),',
    '    (["聯絡人","決策者"],    "決策者"),',
    '    (["進出口資訊","國家"],  "進出口國家"),',
    '    (["銷售資訊","競爭者"],  "競爭者"),',
    '    (["集團資訊","集團"],    "集團"),',
    '    (["偏好及總結","關注議題"],"關注議題"),',
    '    (["產業","產業龍頭"],    "產業龍頭"),',
    '    (["產業鏈","法人的客戶"],"法人客戶"),',
    '    (["產業鏈","法人的供應商"],"法人供應商"),',
    "]",
    "",
    'print("── 各欄位萃取覆蓋率 ─────────────────────────")',
    "for path, label in checks:",
    "    n, p = pct(results, path)",
    '    print(f"  {label:<12s} {n:>7,} 家  ({p:.1f}%)")',
])

SRC_E2 = "\n".join([
    "# ── E2：輸出 CSV（供 Excel 檢視）──────────────────────────",
    'FLAT_CSV = OUTPUT_DIR / "company_labels_flat.csv"',
    "",
    "rows = []",
    "for r in results:",
    '    lb = r["labels"]',
    "    rows.append({",
    '        "company_id":    r["company_id"],',
    '        "外商":          lb.get("基本資料",{}).get("外商"),',
    '        "家族企業":      lb.get("基本資料",{}).get("家族企業"),',
    '        "商業模式":      lb.get("基本資料",{}).get("商業模式"),',
    '        "員工人數":      lb.get("基本資料",{}).get("員工人數"),',
    '        "決策者":        ", ".join(lb.get("聯絡人",{}).get("決策者") or []),',
    '        "家族企業人員":  ", ".join(lb.get("聯絡人",{}).get("家族企業人員") or []),',
    '        "進出口國家":    ", ".join(lb.get("進出口資訊",{}).get("國家") or []),',
    '        "競爭者":        ", ".join(lb.get("銷售資訊",{}).get("競爭者") or []),',
    '        "集團":          lb.get("集團資訊",{}).get("集團"),',
    '        "母公司":        lb.get("集團資訊",{}).get("母公司"),',
    '        "關係企業":      ", ".join(lb.get("集團資訊",{}).get("關係企業") or []),',
    '        "分公司":        ", ".join(lb.get("集團資訊",{}).get("分公司") or []),',
    '        "品牌名稱":      ", ".join(lb.get("集團資訊",{}).get("品牌名稱") or []),',
    '        "關注議題":      ", ".join(lb.get("偏好及總結",{}).get("關注議題") or []),',
    '        "產業龍頭":      lb.get("產業",{}).get("產業龍頭"),',
    '        "法人的客戶":    ", ".join(lb.get("產業鏈",{}).get("法人的客戶") or []),',
    '        "法人的供應商":  ", ".join(lb.get("產業鏈",{}).get("法人的供應商") or []),',
    '        "extracted_at":  r.get("extracted_at",""),',
    "    })",
    "",
    'pd.DataFrame(rows).to_csv(FLAT_CSV, index=False, encoding="utf-8-sig")',
    'print(f"CSV 輸出：{FLAT_CSV}  ({len(rows):,} 筆)")',
])

# ─────────────────────────────────────────────────────────
# Build notebook
# ─────────────────────────────────────────────────────────

cells = [
    mc("md-title", (
        "# Phase 1：法人標籤萃取\n\n"
        "每家公司取最近 20 篇日報，一次 LLM 呼叫萃取 8 大類標籤。\n\n"
        "| 類別 | 欄位 |\n"
        "|------|------|\n"
        "| 基本資料 | 外商 / 家族企業 / 商業模式 / 員工人數 |\n"
        "| 聯絡人 | 決策者 / 家族企業人員 |\n"
        "| 進出口資訊 | 國家 |\n"
        "| 銷售資訊 | 競爭者 |\n"
        "| 集團資訊 | 集團 / 母公司 / 關係企業 / 分公司 / 品牌名稱 |\n"
        "| 偏好及總結 | 關注議題 |\n"
        "| 產業 | 產業龍頭 |\n"
        "| 產業鏈 | 法人的客戶 / 法人的供應商 |\n"
    )),
    mc("md-s0", "## 0. 安裝套件"),
    cc("code-s0", SRC_S0),
    mc("md-s1", "## 1. 匯入套件 & 全域設定"),
    cc("code-s1", SRC_S1),
    mc("md-s2", "## 2. 載入設定 & 建立連線"),
    cc("code-s2", SRC_S2),
    mc("md-a", (
        "---\n## 子任務 A：資料撈取 & 彙整\n\n"
        "每家公司取最近 `TOP_N_LOGS`（20）篇日報，在 Python 側合併為單一文字段落送 LLM。\n"
    )),
    cc("code-a1", SRC_A1),
    cc("code-a2", SRC_A2),
    mc("md-b", (
        "---\n## 子任務 B：LLM 萃取（8 大類標籤）\n\n"
        "每家公司一次 API 呼叫，萃取全部 8 大類。\n"
        "資訊不足的欄位回傳 `null`，不猜測。\n"
    )),
    cc("code-b1", SRC_B1),
    cc("code-b2", SRC_B2),
    mc("md-e", "---\n## 子任務 E：報告\n"),
    cc("code-e1", SRC_E1),
    cc("code-e2", SRC_E2),
]

nb = {
    "nbformat": 4,
    "nbformat_minor": 5,
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.10.0"},
    },
    "cells": cells,
}

out = r"d:\yujui\痛點需求地圖\prompt定版\法人標籤.ipynb"
with open(out, "w", encoding="utf-8") as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)
print("OK:", out)

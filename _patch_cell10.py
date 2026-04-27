# -*- coding: utf-8 -*-
import json

nb = json.load(open(r'd:/yujui/痛點需求地圖/prompt定版/商機等級.ipynb', encoding='utf-8'))

new_src = '''import os, re, json, csv, time
import pandas as pd
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor

# ════════════════════════════════════════════════════════════════
# 關鍵詞快篩字典（Stage A > B > C1 > C2 > D > E > none）
# ════════════════════════════════════════════════════════════════
_KW = {
    "A": ["簽約","合約","議價","議約","成交","用印","簽署","下訂",
          "訂單確認","定案","採購單","付款","發票","尾款","首款",
          "簽訂","正式合約","合約簽訂","簽合約","已簽"],
    "B": ["DEMO","demo","展示","報價","簡報","競爭","POC","poc",
          "評估方案","競標","提案報告","技術評估","排除疑慮","決標",
          "比稿","投標","標案","比較方案","方案評估","報價單"],
    "C1": ["立案","決策者","高層拜訪","形成共識","採購委員會",
           "需求確認","RFP","規格書","評估名單","專案啟動",
           "納入評估","正式評估","列入評估","提需求","需求書"],
    "C2": ["痛點","問題點","探詢需求","認同問題","初步提案",
           "商機確認","提出解決","客戶認同","擴大痛點","需求探討",
           "痛點確認","找到問題","問題確認","提出方向"],
    "D":  ["初訪","潛在客戶","引發興趣","初步接觸","有興趣了解",
           "開發拜訪","感興趣","有意願了解","想了解","初步了解",
           "初次拜訪","首次拜訪","建立關係","開發客戶"],
    "E":  ["潛客","電話開發","名單","陌開","冷開","陌生開發"],
}

_NONE_KW = ["電話未接","未接電話","不在位","無人接聽","已離職","婉拒",
            "拒絕","無需求","暫無需求","沒有興趣","已有系統","已導入",
            "無法聯繫","關機","空號","電話打不通","失聯"]

_STAGE_GROUP = {"A":"成交後","B":"成交前","C1":"成交前",
                "C2":"成交前","D":"成交前","E":"成交前"}

_stats = {"kw": 0, "llm": 0}

# ── 基礎結果 ─────────────────────────────────────────────────────
def _none_result(reason=""):
    return {"E":False,"D":False,"C2":False,"C1":False,
            "B":False,"A":False,"stage_group":"none","reason":reason}

def _stage_result(stage, reason):
    r = _none_result(reason)
    r[stage] = True
    r["stage_group"] = _STAGE_GROUP[stage]
    return r

# ── 關鍵詞快篩 ───────────────────────────────────────────────────
def keyword_stage_check(text):
    t = text or ""
    if len(t.strip()) < 15:
        return _none_result("文字過短")
    for kw in _NONE_KW:
        if kw in t:
            return _none_result(kw)
    for stage in ["A","B","C1","C2","D","E"]:
        for kw in _KW[stage]:
            if kw in t:
                return _stage_result(stage, kw)
    return None

# ── 批次 LLM（10 筆/call，節省 RPM）────────────────────────────
BATCH_LLM_N = 10

_BATCH_PROMPT = (
    "以下 {n} 筆業務日誌，逐筆判斷銷售階段。\\n"
    "階段：A議價簽約 / B報價DEMO評估 / C1立案決策者 / C2確認痛點 / D引發興趣 / E陌生開發 / none無明確行為\\n\\n"
    "每筆輸出一行，格式「編號|代碼|關鍵依據15字內」，不加其他文字：\\n\\n"
    "{records}"
)

def _parse_batch_line(line, n):
    parts = line.split("|")
    if len(parts) < 2:
        return None, None
    try:
        idx = int(re.sub(r"\\D", "", parts[0])) - 1
    except ValueError:
        return None, None
    if not (0 <= idx < n):
        return None, None
    stage_raw = parts[1].strip().upper()
    reason = parts[2].strip()[:30] if len(parts) > 2 else ""
    for s in ["A","B","C1","C2","D","E"]:
        if s in stage_raw:
            return idx, _stage_result(s, reason)
    return idx, _none_result(reason or "無明確銷售行為")

def llm_batch_check(texts, max_retries=3):
    n = len(texts)
    records = "\\n".join(f"[{i+1}] {t[:400]}" for i, t in enumerate(texts))
    prompt = _BATCH_PROMPT.format(n=n, records=records)
    for attempt in range(max_retries):
        try:
            resp = model.generate_content(prompt, request_options={"timeout": 60})
            results = [None] * n
            for line in resp.text.strip().splitlines():
                line = line.strip()
                if not line:
                    continue
                idx, res = _parse_batch_line(line, n)
                if idx is not None:
                    results[idx] = res
            return [r if r is not None else _none_result("批次解析失敗") for r in results]
        except Exception:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
    return [_none_result("逾時/失敗")] * n

# ── 並行化：關鍵詞全量快篩 → LLM 批次補完 ───────────────────────
def parallel_stage_check(batch, max_workers=6):
    records = batch.to_dict("records")
    results = [None] * len(records)
    llm_indices = []

    for i, row in enumerate(records):
        kw = keyword_stage_check(row["LD010"])
        if kw is not None:
            results[i] = kw
            _stats["kw"] += 1
        else:
            llm_indices.append(i)

    if llm_indices:
        _stats["llm"] += len(llm_indices)
        llm_texts = [records[i]["LD010"] for i in llm_indices]
        mini_batches = [llm_texts[i:i+BATCH_LLM_N]
                        for i in range(0, len(llm_texts), BATCH_LLM_N)]
        with ThreadPoolExecutor(max_workers=max_workers) as ex:
            batch_results = list(ex.map(llm_batch_check, mini_batches))
        flat = [r for sub in batch_results for r in sub]
        for i, idx in enumerate(llm_indices):
            results[idx] = flat[i]

    return pd.DataFrame(results, index=batch.index)

def print_kw_stats():
    total = _stats["kw"] + _stats["llm"]
    if total:
        print(f"關鍵詞命中：{_stats['kw']:,}（{_stats['kw']/total:.0%}）  LLM批次：{_stats['llm']:,}（{_stats['llm']/total:.0%}）")

print(f"✅ 載入完成：批次 LLM（{BATCH_LLM_N} 筆/call）+ 關鍵詞快篩")
'''

nb['cells'][10]['source'] = new_src
json.dump(nb, open(r'd:/yujui/痛點需求地圖/prompt定版/商機等級.ipynb', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('done')

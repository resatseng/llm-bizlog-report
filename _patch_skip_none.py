# -*- coding: utf-8 -*-
"""
對 Phase L Step1 SKIP 日誌補跑：
1. 加入 none 層（拒絕/無需求訊號）
2. 補充各層短句關鍵詞
3. 結果 append 到 phase_l_final.csv
"""
import json, pyodbc, configparser, pandas as pd, hashlib
from pathlib import Path
from datetime import datetime
from tqdm import tqdm

STEP1_JSONL  = Path(r'd:\yujui\痛點需求地圖\step1_output\step1_results.jsonl')
FINAL_CSV    = Path(r'd:\yujui\痛點需求地圖\step3_output\phase_l_final.csv')
OUTPUT_PATCH = Path(r'd:\yujui\痛點需求地圖\step3_output\phase_l_patch_none.csv')

# ── 補充關鍵詞規則 ─────────────────────────────────────────────
PATCH_RULES = {
    "none": {
        "keywords": [
            # 明確拒絕
            "不需要", "沒有需求", "無需求", "目前無需求", "暫無需求",
            "不需要系統", "不缺系統", "不用系統", "已有系統",
            "不感興趣", "沒興趣", "婉拒", "拒絕", "不接受",
            "別再來", "不要再打", "不願被拜訪", "不願多談",
            "unfriendly", "抗拒", "厭煩",
            # 公司狀態異常
            "公司已停業", "停業", "已停業", "結束營業", "解散",
            "空號", "暫停營業", "已結束", "不在營業",
            # 已有競品
            "已導入", "已在用", "去年底開始導入", "已有在用",
            # 不開發
            "不開發", "已有業務經營",
        ],
        "negations": []
    },
    "L5": {
        "keywords": [
            "討論demo", "demo時間", "了解需求", "訪談了解",
            "需求討論", "需求說明", "快篩分析", "初訪",
            "業務初訪", "顧問初訪", "首訪", "第一次拜訪",
        ],
        "negations": []
    },
    "L6": {
        "keywords": [
            "起案簡報", "起案", "重新起案", "提案討論",
        ],
        "negations": []
    },
    "L7": {
        "keywords": [
            "出單", "建立潛客", "pass單", "PASS單",
        ],
        "negations": []
    },
}

SHORT_TEXT_LEN = 50

def match_patch(text: str):
    """依 PATCH_RULES 分類，none 層優先檢查"""
    # none 優先
    for layer in ["none", "L7", "L6", "L5"]:
        if layer not in PATCH_RULES:
            continue
        cfg = PATCH_RULES[layer]
        if any(neg in text for neg in cfg["negations"]):
            continue
        if any(kw in text for kw in cfg["keywords"]):
            return layer
    return None

# ── 讀取 SKIP event_ids ────────────────────────────────────────
print("讀取 SKIP event_ids...")
skip_ids = set()
with open(STEP1_JSONL, encoding='utf-8') as f:
    for line in f:
        r = json.loads(line)
        if r.get('step1_confidence') == 'SKIP':
            skip_ids.add(r['event_id'])

print(f"SKIP 總數：{len(skip_ids):,}")

# ── 連 DB 撈 SKIP 日誌原文 ────────────────────────────────────
cfg = configparser.ConfigParser()
cfg.read(r'D:\yujui\SqlServer18.txt', encoding='utf-8')
sec = cfg['mssql']
conn = pyodbc.connect(
    f"DRIVER={{SQL Server}};SERVER={sec['server']};DATABASE=DSC_CRM_SP;"
    f"UID={sec['uid']};PWD={sec['pwd']};", autocommit=True
)

print("撈取短日誌原文（< 50 字）...")
logs = pd.read_sql("""
    SELECT GY001 AS company_id, GY003 AS salesperson_id,
           GY004 AS contact_date, GY012 AS log_content,
           LEN(GY012) AS log_len,
           FORMAT(CREATE_DATE,'yyyy-MM') AS ym
    FROM CRMGY
    WHERE LEN(GY012) >= 5 AND LEN(GY012) < 50
""", conn)

logs['event_id'] = logs['log_content'].astype(str).apply(
    lambda t: hashlib.sha256(t.encode()).hexdigest()[:16]
)

# 只保留 SKIP 的那些
logs = logs[logs['event_id'].isin(skip_ids)].copy()
print(f"匹配到 SKIP 日誌：{len(logs):,} 筆")

# ── 補分類 ────────────────────────────────────────────────────
print("補跑關鍵詞分類...")
results = []
matched = 0
for _, row in tqdm(logs.iterrows(), total=len(logs), desc="補分類"):
    layer = match_patch(str(row['log_content']))
    if layer:
        matched += 1
        results.append({
            'event_id':   row['event_id'],
            'company_id': row['company_id'],
            'ym':         row['ym'],
            'l_layer':    layer,
            'confidence': 0.7,
            'source':     'patch_none',
        })

print(f"\n命中：{matched:,} 筆（{matched/len(logs)*100:.1f}%）")
if not results:
    print("無新結果，結束")
    exit()

patch_df = pd.DataFrame(results)
print("\n補分類結果分布：")
print(patch_df['l_layer'].value_counts().to_string())

# ── Append 到 phase_l_final.csv ───────────────────────────────
# 先確認不重複（phase_l_final 已有的 event_id 不再追加）
final = pd.read_csv(FINAL_CSV, usecols=['event_id'], low_memory=False)
existing_ids = set(final['event_id'].dropna())
new_rows = patch_df[~patch_df['event_id'].isin(existing_ids)]
print(f"\n新增（排除重複）：{len(new_rows):,} 筆")

# 先存 patch 獨立檔案備查
patch_df.to_csv(OUTPUT_PATCH, index=False, encoding='utf-8-sig')
print(f"備份：{OUTPUT_PATCH}")

# Append
new_rows.to_csv(FINAL_CSV, mode='a', header=False, index=False, encoding='utf-8-sig')
print(f"Append 完成 → {FINAL_CSV}")

# 驗證總數
total = sum(1 for _ in open(FINAL_CSV, encoding='utf-8')) - 1
print(f"\nphase_l_final.csv 最終行數：{total:,}")
print(f"  原始：1,802,590")
print(f"  新增：{total - 1802590:,}")
print("\n✅ 補丁完成")

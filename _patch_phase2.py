# -*- coding: utf-8 -*-
"""修改 L-Phase2深度標籤.ipynb：
1. Cell 9  RESUME 只跳過成功記錄，錯誤的重跑
2. Cell 12 call_llm 加 retry + 指數退避
"""
import json, re

NB_PATH = r'd:\yujui\痛點需求地圖\prompt定版\L-Phase2深度標籤.ipynb'
nb = json.load(open(NB_PATH, encoding='utf-8'))

# ── Cell 9：修正 RESUME 邏輯 ──────────────────────────────────
nb['cells'][9]['source'] = [
    '# ── A2：Resume（只跳過成功記錄，_error 重跑）──\n',
    'done_ids = set()\n',
    'if RESUME and RESULT_JSONL.exists():\n',
    '    with open(RESULT_JSONL, encoding="utf-8") as f:\n',
    '        for l in f:\n',
    '            if not l.strip(): continue\n',
    '            r = json.loads(l)\n',
    '            if "_error" not in r.get("labels", {}) and r.get("labels"):\n',
    '                done_ids.add(r["company_id"])\n',
    '    print(f"已完成（成功）：{len(done_ids):,} 家")\n',
    '    print(f"將重跑錯誤/空標籤：{len(ALL_COMPANIES)-len(done_ids):,} 家")\n',
    'else:\n',
    '    if not RESUME and RESULT_JSONL.exists():\n',
    '        os.remove(RESULT_JSONL)\n',
    '    print(f"從頭開始，共 {len(ALL_COMPANIES):,} 家")\n',
    '\n',
    'TODO_COMPANIES = [c for c in ALL_COMPANIES if c not in done_ids]\n',
    'print(f"本次待處理：{len(TODO_COMPANIES):,} 家")\n',
]
print("Cell 9 修改完成")

# ── Cell 12：加 retry 退避 ────────────────────────────────────
old_src = ''.join(nb['cells'][12]['source'])

new_call_llm = '''def call_llm(company_id: str, logs_by_layer: dict) -> dict:
    prompt = build_prompt(logs_by_layer)
    if not prompt.strip() or len(logs_by_layer) == 0:
        return {}
    for attempt in range(5):
        try:
            resp = client.models.generate_content(
                model=MODEL,
                contents=prompt,
                config=genai_types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    temperature=TEMP,
                    response_mime_type='application/json',
                ),
            )
            m = _JSON_PAT.search(resp.text.strip())
            return json.loads(m.group()) if m else {}
        except Exception as e:
            err = str(e)
            if '429' in err or 'RESOURCE_EXHAUSTED' in err:
                wait = min(30 * (2 ** attempt), 300)
                time.sleep(wait)
                continue
            return {'_error': err}
    return {'_error': 'max retries (429)'}

print('B2 LLM 函數定義完成（含 retry）')
'''

pattern = r'def call_llm.*?print\([^\n]*B2[^\n]*\)'
new_src = re.sub(pattern, new_call_llm.strip(), old_src, flags=re.DOTALL)

if new_src == old_src:
    print("警告：Cell 12 pattern 未匹配，手動替換")
    # fallback：直接在最後附加新定義
    new_src = old_src + '\n\n# ── retry 版本 ──\n' + new_call_llm
else:
    print("Cell 12 修改完成（regex 替換成功）")

nb['cells'][12]['source'] = [new_src]

# ── 儲存 ──────────────────────────────────────────────────────
json.dump(nb, open(NB_PATH, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print("notebook 儲存完成")
print()
print("重跑步驟：")
print("  1. 重啟 Kernel")
print("  2. Run All Cells（Cell 1 → 13）")
print("  3. 只有 81 筆成功記錄會跳過，其餘 171k+ 筆重新跑")

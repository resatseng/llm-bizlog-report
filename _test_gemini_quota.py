# -*- coding: utf-8 -*-
"""測試 Gemini API 配額是否恢復"""
import configparser, time
from google import genai

GCP_INI = r"D:\yujui\GoogleCloud.ini"
cfg = configparser.ConfigParser()
cfg.read(GCP_INI, encoding="utf-8")

def _get_ini(cfg, key):
    for sec in list(cfg.sections()) + ['DEFAULT']:
        for k in (key, f"'{key}'"):
            try:
                v = cfg.get(sec, k)
                if v: return v.strip("'\" ")
            except: pass
    raise KeyError(f'{key} not found')

GEMINI_KEY = _get_ini(cfg, 'gemini_api_key')
client = genai.Client(api_key=GEMINI_KEY)

# 用 Phase 2 同款 model 打測試
MODEL = "gemini-2.5-flash"

print(f"模型：{MODEL}")
print("發送測試請求...")

try:
    t0 = time.time()
    resp = client.models.generate_content(
        model=MODEL,
        contents="請回答：1+1=?（只回數字）",
    )
    elapsed = time.time() - t0
    print(f"成功！回應：{resp.text.strip()}  ({elapsed:.1f}s)")
    print()

    # 連打 3 次確認不會立刻 429
    for i in range(2, 4):
        resp2 = client.models.generate_content(
            model=MODEL,
            contents=f"請回答：{i}+{i}=?（只回數字）",
        )
        print(f"第 {i} 次：{resp2.text.strip()}")
        time.sleep(0.5)

    print()
    print("配額正常，可以重跑 Phase 2")

except Exception as e:
    err = str(e)
    if "429" in err or "RESOURCE_EXHAUSTED" in err:
        print("仍然 429 RESOURCE_EXHAUSTED，配額尚未恢復")
    elif "quota" in err.lower():
        print("配額問題：" + err[:200])
    else:
        print("其他錯誤：" + err[:300])

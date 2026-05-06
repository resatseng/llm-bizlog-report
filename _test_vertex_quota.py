# -*- coding: utf-8 -*-
"""測試 Vertex AI Gemini 配額和 model 可用性"""
import configparser, time, os
from google import genai
from google.genai import types as genai_types

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

# Vertex AI 設定
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"C:/Users/DSC/yujui/auto-upload-dataset/digiwin-ai-cf22a107ca03.json"
PROJECT_ID = _get_ini(cfg, 'project_id')
client = genai.Client(vertexai=True, project=PROJECT_ID, location='us-central1')
print(f"Vertex AI 連線成功（project={PROJECT_ID}）\n")

# 測試多個 model（優先測試 2.5-flash）
test_models = [
    "gemini-2.5-flash",      # 較新版本（優先測試）
    "gemini-1.5-flash",      # 穩定版
    "gemini-2.0-flash",      # notebook 當前使用
    "gemini-2.0-flash-exp",  # 實驗版
]

for model_name in test_models:
    print(f"{'='*60}")
    print(f"測試 Model: {model_name}")
    print(f"{'='*60}")

    try:
        t0 = time.time()
        resp = client.models.generate_content(
            model=model_name,
            contents="測試：1+1=?（只回數字）",
            config=genai_types.GenerateContentConfig(
                temperature=0.1,
                response_mime_type='application/json',
            ),
        )
        elapsed = time.time() - t0
        print(f"[OK] Success! Response: {resp.text.strip()[:50]}  ({elapsed:.1f}s)")

        # 連續測試 5 次確認 RPM
        print("Testing continuous requests (RPM check)...")
        success_count = 0
        for i in range(5):
            try:
                t1 = time.time()
                resp2 = client.models.generate_content(
                    model=model_name,
                    contents=f"{i}+{i}=?",
                )
                elapsed2 = time.time() - t1
                success_count += 1
                print(f"  [{i+1}/5] OK ({elapsed2:.1f}s)")
                time.sleep(0.1)  # 避免太快
            except Exception as e2:
                err2 = str(e2)
                if "429" in err2:
                    print(f"  [{i+1}/5] FAIL: 429 (RPM exceeded)")
                    break
                else:
                    print(f"  [{i+1}/5] FAIL: {err2[:50]}")
                    break

        print(f"Consecutive success: {success_count}/5\n")

        if success_count == 5:
            print(f">>> RECOMMENDED: {model_name}\n")
            break

    except Exception as e:
        err = str(e)
        if "404" in err or "NOT_FOUND" in err:
            print(f"[404] Model not found\n")
        elif "429" in err or "RESOURCE_EXHAUSTED" in err:
            print(f"[429] RESOURCE_EXHAUSTED\n")
        else:
            print(f"[ERROR] {err[:100]}\n")

print(f"{'='*60}")
print("測試完成")

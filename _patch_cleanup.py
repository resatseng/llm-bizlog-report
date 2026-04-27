# -*- coding: utf-8 -*-
import json

nb = json.load(open(r'd:/yujui/痛點需求地圖/prompt定版/商機等級.ipynb', encoding='utf-8'))

# 合併 Cell 4 + Cell 5 → 一個乾淨的 Gemini 設定 cell
clean_setup = '''import os, configparser
import google.generativeai as genai

cfg = configparser.ConfigParser()
cfg.read(r"D:\\yujui\\GoogleCloud.ini")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", cfg.get("gcp", "gemini_api_key", fallback=""))
if not GEMINI_API_KEY:
    raise RuntimeError("找不到 gemini_api_key，請確認 D:\\\\yujui\\\\GoogleCloud.ini")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")
print("✅ Gemini API 設定完成")
'''

# 用合併後的 cell 取代 Cell 4，刪除 Cell 5
nb['cells'][4]['source'] = clean_setup
del nb['cells'][5]

json.dump(nb, open(r'd:/yujui/痛點需求地圖/prompt定版/商機等級.ipynb', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# 驗證結果
for i, cell in enumerate(nb['cells']):
    src = ''.join(cell['source']).strip()[:80].replace('\n',' ')
    print(f'Cell {i:2d} [{cell["cell_type"]:8s}] {src}')

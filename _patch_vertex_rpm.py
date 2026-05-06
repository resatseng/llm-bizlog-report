# -*- coding: utf-8 -*-
"""更新 Cell 4 的 RPM_LIMIT / N_WORKERS（Vertex AI 配額高，加速跑）"""
import json

NB_PATH = r'd:\yujui\痛點需求地圖\prompt定版\L-Phase2深度標籤.ipynb'
nb = json.load(open(NB_PATH, encoding='utf-8'))

src = ''.join(nb['cells'][4]['source'])

# 調高 Vertex AI 可用配額
src = src.replace('RPM_LIMIT  = 30',  'RPM_LIMIT  = 300')
src = src.replace('N_WORKERS  = 6',   'N_WORKERS  = 20')

nb['cells'][4]['source'] = [src]
json.dump(nb, open(NB_PATH, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# 驗證
src2 = ''.join(nb['cells'][4]['source'])
print("RPM_LIMIT :", "300" in src2)
print("N_WORKERS :", "20" in src2)
print("儲存完成")

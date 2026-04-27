# -*- coding: utf-8 -*-
import json, re

nb = json.load(open(r'd:/yujui/痛點需求地圖/prompt定版/商機等級.ipynb', encoding='utf-8'))
src = ''.join(nb['cells'][5]['source'])

# 找到 KNN 區塊的起始（═══ 那行）和結束（print("✅ KNN 函式載入完成") 那行）
start_marker = '# ════════════════════════════════════════════════════════════════\n# KNN 分類'
end_marker   = 'print(f"✅ KNN 函式載入完成'

idx_start = src.find(start_marker)
idx_end   = src.find(end_marker)
if idx_start == -1 or idx_end == -1:
    print(f'marker not found: start={idx_start}, end={idx_end}')
else:
    # 取到 end_marker 那行的行尾
    idx_end_line = src.find('\n', idx_end) + 1
    old_block = src[idx_start:idx_end_line]

    new_block = '''# ════════════════════════════════════════════════════════════════
# KNN 分類（TF-IDF + sklearn，零 API 呼叫）
# ════════════════════════════════════════════════════════════════
import numpy as np
from sklearn.neighbors import KNeighborsClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize
import pickle
from pathlib import Path

KNN_K          = 5
KNN_CONF       = 0.65   # ≥ 4/5 票視為高信心（同 L1L7 Step2）
KNN_MODEL_PATH = r"D:\\yujui\\痛點需求地圖\\stage_knn_model.pkl"

knn        = None   # 訓練完再 assign
vectorizer = None   # TF-IDF vectorizer

# 若模型已存在則直接載入
if Path(KNN_MODEL_PATH).exists():
    _m = pickle.load(open(KNN_MODEL_PATH, "rb"))
    knn = _m["knn"]
    vectorizer = _m.get("vectorizer")
    print(f"✅ 已載入既有 KNN 模型（{_m.get('n_train',0):,} 筆種子）")

def batch_embed(texts):
    """TF-IDF 向量化，回傳 sparse matrix（零 API 呼叫）"""
    return vectorizer.transform([t[:800] for t in texts])

print(f"✅ KNN 函式載入完成（TF-IDF，信心門檻 {KNN_CONF:.0%}）")
'''
    new_src = src[:idx_start] + new_block + src[idx_end_line:]
    nb['cells'][5]['source'] = new_src
    json.dump(nb, open(r'd:/yujui/痛點需求地圖/prompt定版/商機等級.ipynb', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('Cell 5 OK')
    # verify
    src_check = ''.join(nb['cells'][5]['source'])
    print('TfidfVectorizer:', 'TfidfVectorizer' in src_check)
    print('EMBED_MODEL removed:', 'EMBED_MODEL' not in src_check)
    print('batch_embed OK:', 'vectorizer.transform' in src_check)

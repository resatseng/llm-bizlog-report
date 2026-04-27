# -*- coding: utf-8 -*-
"""把 batch_embed（Gemini API）改成 TF-IDF（sklearn，零 API 呼叫）"""
import json

nb = json.load(open(r'd:/yujui/痛點需求地圖/prompt定版/商機等級.ipynb', encoding='utf-8'))

# ── Cell 5：函式 cell ─────────────────────────────────────────────
src5 = ''.join(nb['cells'][5]['source'])

# 移除 API embedding 相關常數 + 函式，換成 TF-IDF
old_embed_block = '''# ════════════════════════════════════════════════════════════════
# KNN 分類（Embedding + sklearn，近乎零 RPM）
# ════════════════════════════════════════════════════════════════
import numpy as np
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import normalize
import pickle

EMBED_MODEL      = "models/embedding-001"
EMBED_BATCH_SIZE = 100      # 每次 embedding API 送幾筆
KNN_K            = 5
KNN_CONF         = 0.65     # ≥ 4/5 票視為高信心（同 L1L7 Step2）
KNN_MODEL_PATH   = r"D:\\yujui\\痛點需求地圖\\stage_knn_model.pkl"

knn = None  # 訓練完再 assign

def batch_embed(texts):
    """分批取 embedding，回傳 np.ndarray (N, dim)"""
    # 確保使用 API key（非 service account）
    if GEMINI_API_KEY:
        genai.configure(api_key=GEMINI_API_KEY)
    all_vecs = []
    for i in range(0, len(texts), EMBED_BATCH_SIZE):
        chunk = [t[:800] for t in texts[i:i+EMBED_BATCH_SIZE]]
        try:
            res = genai.embed_content(
                model=EMBED_MODEL,
                content=chunk,
                task_type="classification"
            )
            # SDK 回傳 list[list[float]] 或 list[float]（單筆時）
            embs = res["embedding"]
            if isinstance(embs[0], float):   # 單筆退化
                embs = [embs]
            all_vecs.extend(embs)
        except Exception as e:
            print(f"  embed 失敗（batch {i}）: {e}")
            # 補零向量，不中斷流程
            all_vecs.extend([[0.0]*768] * len(chunk))
    return np.array(all_vecs, dtype=np.float32)'''

new_embed_block = '''# ════════════════════════════════════════════════════════════════
# KNN 分類（TF-IDF + sklearn，零 API 呼叫）
# ════════════════════════════════════════════════════════════════
import numpy as np
from sklearn.neighbors import KNeighborsClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize
import pickle

KNN_K          = 5
KNN_CONF       = 0.65   # ≥ 4/5 票視為高信心（同 L1L7 Step2）
KNN_MODEL_PATH = r"D:\\yujui\\痛點需求地圖\\stage_knn_model.pkl"

knn        = None   # 訓練完再 assign
vectorizer = None   # TF-IDF vectorizer

def batch_embed(texts):
    """TF-IDF 向量化，回傳 sparse matrix"""
    return vectorizer.transform([t[:800] for t in texts])'''

new_src5 = src5.replace(old_embed_block, new_embed_block)
if new_src5 == src5:
    print('ERROR: Cell 5 replace failed')
    # show the relevant part
    idx = src5.find('KNN 分類')
    print(repr(src5[idx:idx+200]))
else:
    nb['cells'][5]['source'] = new_src5
    print('Cell 5 OK')

# ── Cell 8：KNN 訓練 cell ─────────────────────────────────────────
src8 = ''.join(nb['cells'][8]['source'])

old_knn_train = '''# 批次 Embedding
print("\\n生成訓練 embedding（可能需要 1-2 分鐘）...")
train_texts  = train_df["LD010"].astype(str).tolist()
train_labels = train_df["top_stage"].tolist()
train_emb    = normalize(batch_embed(train_texts))
print(f"  embedding shape: {train_emb.shape}")

# 訓練 KNN
knn = KNeighborsClassifier(n_neighbors=KNN_K, metric="cosine", algorithm="brute", n_jobs=-1)
knn.fit(train_emb, train_labels)
print(f"\\n✅ KNN 訓練完成（k={KNN_K}，{len(train_labels)} 筆種子）")

# 儲存
with open(KNN_MODEL_PATH, "wb") as f:
    pickle.dump({"knn": knn, "n_train": len(train_labels)}, f)
print(f"✅ 模型已儲存：{KNN_MODEL_PATH}")'''

new_knn_train = '''# TF-IDF 向量化（字元 2-3 gram，無需 API）
print("\\n訓練 TF-IDF 向量化器...")
train_texts  = train_df["LD010"].astype(str).tolist()
train_labels = train_df["top_stage"].tolist()

vectorizer = TfidfVectorizer(
    analyzer="char_wb", ngram_range=(2, 3),
    max_features=30000, sublinear_tf=True
)
X_train = vectorizer.fit_transform(train_texts)
print(f"  特徵維度：{X_train.shape[1]:,}")

# 訓練 KNN
knn = KNeighborsClassifier(n_neighbors=KNN_K, metric="cosine", algorithm="brute", n_jobs=-1)
knn.fit(X_train, train_labels)
print(f"\\n✅ KNN 訓練完成（k={KNN_K}，{len(train_labels)} 筆種子，零 API 呼叫）")

# 儲存
with open(KNN_MODEL_PATH, "wb") as f:
    pickle.dump({"knn": knn, "vectorizer": vectorizer, "n_train": len(train_labels)}, f)
print(f"✅ 模型已儲存：{KNN_MODEL_PATH}")'''

new_src8 = src8.replace(old_knn_train, new_knn_train)
if new_src8 == src8:
    print('ERROR: Cell 8 replace failed')
    idx = src8.find('批次 Embedding')
    print(repr(src8[idx:idx+200]))
else:
    nb['cells'][8]['source'] = new_src8
    print('Cell 8 OK')

# ── Cell 8：也要在載入模型時還原 vectorizer ────────────────────────
# 如果模型已存在，要同時載入 vectorizer
old_load = '''knn = None  # 訓練完再 assign
vectorizer = None   # TF-IDF vectorizer'''

# 在 Cell 5 的 knn/vectorizer 宣告後加上：嘗試從磁碟載入
new_load = '''knn = None        # 訓練完再 assign
vectorizer = None  # TF-IDF vectorizer

# 若模型檔已存在則直接載入
if Path(KNN_MODEL_PATH).exists():
    _m = pickle.load(open(KNN_MODEL_PATH, "rb"))
    knn = _m["knn"]
    vectorizer = _m.get("vectorizer")
    print(f"✅ 已載入既有 KNN 模型（{_m.get('n_train',0):,} 筆種子）")'''

src5_v2 = ''.join(nb['cells'][5]['source'])
# 需要先 import Path
if 'from pathlib import Path' not in src5_v2:
    src5_v2 = src5_v2.replace('import pickle', 'import pickle\nfrom pathlib import Path')

src5_v2 = src5_v2.replace(old_load, new_load)
if src5_v2 == ''.join(nb['cells'][5]['source']):
    print('Cell 5 autoload: no change (might be OK)')
else:
    nb['cells'][5]['source'] = src5_v2
    print('Cell 5 autoload OK')

json.dump(nb, open(r'd:/yujui/痛點需求地圖/prompt定版/商機等級.ipynb', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('\n全部完成！重新執行 Cell 5 → Cell 8 → Cell 9')

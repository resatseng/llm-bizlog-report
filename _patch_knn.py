# -*- coding: utf-8 -*-
"""
把商機等級.ipynb 改成 KNN 分類流程：
  Cell 10  ：加入 batch_embed / parallel_stage_check_knn
  Cell 16 後：插入「建立 KNN 模型」cell
  Cell 17  ：主流程改用 parallel_stage_check_knn
"""
import json, copy

nb = json.load(open(r'd:/yujui/痛點需求地圖/prompt定版/商機等級.ipynb', encoding='utf-8'))

# ══════════════════════════════════════════════════════════════
# 1. Cell 10：在原有函式後面追加 KNN 相關函式
# ══════════════════════════════════════════════════════════════
knn_addon = '''
# ════════════════════════════════════════════════════════════════
# KNN 分類（Embedding + sklearn，近乎零 RPM）
# ════════════════════════════════════════════════════════════════
import numpy as np
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import normalize
import pickle

EMBED_MODEL      = "models/text-embedding-004"
EMBED_BATCH_SIZE = 100      # 每次 embedding API 送幾筆
KNN_K            = 5
KNN_CONF         = 0.60     # ≥ 3/5 票視為高信心
KNN_MODEL_PATH   = r"D:\\yujui\\痛點需求地圖\\stage_knn_model.pkl"

knn = None  # 訓練完再 assign

def batch_embed(texts):
    """分批取 embedding，回傳 np.ndarray (N, dim)"""
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
    return np.array(all_vecs, dtype=np.float32)

def parallel_stage_check_knn(batch, max_workers=6):
    """關鍵詞 → KNN → LLM 批次（僅低信心）"""
    global _stats
    records = batch.to_dict("records")
    results = [None] * len(records)
    knn_indices = []

    # Step 1：關鍵詞快篩
    for i, row in enumerate(records):
        kw = keyword_stage_check(row["LD010"])
        if kw is not None:
            results[i] = kw
            _stats["kw"] += 1
        else:
            knn_indices.append(i)

    if not knn_indices:
        return pd.DataFrame(results, index=batch.index)

    # Step 2：KNN 分類
    knn_texts  = [records[i]["LD010"] for i in knn_indices]
    embeddings = normalize(batch_embed(knn_texts))
    proba      = knn.predict_proba(embeddings)
    classes    = knn.classes_

    llm_needed = []
    for j, orig_idx in enumerate(knn_indices):
        max_p  = proba[j].max()
        stage  = classes[proba[j].argmax()]
        if max_p >= KNN_CONF:
            results[orig_idx] = _stage_result(stage, f"KNN {max_p:.0%}")
            _stats["knn"] = _stats.get("knn", 0) + 1
        else:
            llm_needed.append(orig_idx)

    # Step 3：LLM 批次（僅低信心）
    if llm_needed:
        _stats["llm"] += len(llm_needed)
        llm_texts    = [records[i]["LD010"] for i in llm_needed]
        mini_batches = [llm_texts[i:i+BATCH_LLM_N]
                        for i in range(0, len(llm_texts), BATCH_LLM_N)]
        with ThreadPoolExecutor(max_workers=max_workers) as ex:
            batch_res = list(ex.map(llm_batch_check, mini_batches))
        flat = [r for sub in batch_res for r in sub]
        for k, orig_idx in enumerate(llm_needed):
            results[orig_idx] = flat[k]

    return pd.DataFrame(results, index=batch.index)

def print_kw_stats():
    kw  = _stats.get("kw",  0)
    knn_n = _stats.get("knn", 0)
    llm = _stats.get("llm", 0)
    total = kw + knn_n + llm
    if total:
        print(f"關鍵詞：{kw:,}（{kw/total:.0%}）  "
              f"KNN：{knn_n:,}（{knn_n/total:.0%}）  "
              f"LLM：{llm:,}（{llm/total:.0%}）")

print(f"✅ KNN 函式載入完成（信心門檻 {KNN_CONF:.0%}，每批 embed {EMBED_BATCH_SIZE} 筆）")
'''

src10 = ''.join(nb['cells'][10]['source'])
# 移除舊的 print_kw_stats 和 print 語句，追加新版
src10 = src10.replace(
    '''def print_kw_stats():
    total = _stats["kw"] + _stats["llm"]
    if total:
        print(f"關鍵詞命中：{_stats['kw']:,}（{_stats['kw']/total:.0%}）  LLM批次：{_stats['llm']:,}（{_stats['llm']/total:.0%}）")

print(f"✅ 載入完成：批次 LLM（{BATCH_LLM_N} 筆/call）+ 關鍵詞快篩")''',
    f'print(f"✅ 基礎函式載入完成")'
)
nb['cells'][10]['source'] = src10 + knn_addon

# ══════════════════════════════════════════════════════════════
# 2. 在 Cell 16 後插入「建立 KNN 模型」cell
# ══════════════════════════════════════════════════════════════
train_knn_cell = {
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": '''# ── 建立 KNN 分類器（用現有標注結果當種子）──────────────────────
from pathlib import Path
import pandas as pd, numpy as np
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import normalize
import pickle

VALID_STAGES = ["A","B","C1","C2","D","E","none"]
MIN_PER_CLASS = 5   # 每個 stage 至少需要幾筆才納入訓練

seed_df = pd.read_csv(OUTPUT_FILE, encoding="utf-8-sig", low_memory=False)
seed_df = seed_df[seed_df["top_stage"].isin(VALID_STAGES)].dropna(subset=["LD010","top_stage"])
print(f"種子資料：{len(seed_df):,} 筆")
print(seed_df["top_stage"].value_counts().to_string())

# 各 stage 取樣上限（避免 none 嚴重失衡）
MAX_PER_CLASS = 3000
train_parts = []
for stage, grp in seed_df.groupby("top_stage"):
    if len(grp) >= MIN_PER_CLASS:
        train_parts.append(grp.sample(min(len(grp), MAX_PER_CLASS), random_state=42))
train_df = pd.concat(train_parts).sample(frac=1, random_state=42)
print(f"\\n訓練集：{len(train_df):,} 筆（各類上限 {MAX_PER_CLASS}）")

# 批次 Embedding
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
print(f"✅ 模型已儲存：{KNN_MODEL_PATH}")
'''
}

# 找 Cell 16 的位置並在其後插入
nb['cells'].insert(17, train_knn_cell)
print("訓練 KNN cell 插入在 Cell 16 後（現在是 Cell 17）")

# ══════════════════════════════════════════════════════════════
# 3. Cell 18（原 Cell 17）：主流程改用 parallel_stage_check_knn
# ══════════════════════════════════════════════════════════════
main_cell = nb['cells'][18]
src18 = ''.join(main_cell['source'])
src18 = src18.replace(
    'batch_results = parallel_stage_check(batch, max_workers=MAX_WORKERS)',
    'batch_results = parallel_stage_check_knn(batch, max_workers=MAX_WORKERS)'
)
src18 = src18.replace(
    'print_kw_stats()  # 顯示關鍵詞命中率\n',
    'print_kw_stats()\n'
)
nb['cells'][18]['source'] = src18

if 'parallel_stage_check_knn' in src18:
    print("Cell 18 主流程已改用 parallel_stage_check_knn ✅")
else:
    print("Cell 18 替換失敗，請手動確認")

json.dump(nb, open(r'd:/yujui/痛點需求地圖/prompt定版/商機等級.ipynb', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print("\n全部完成！")

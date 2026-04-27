# -*- coding: utf-8 -*-
import json

nb = json.load(open(r'd:/yujui/痛點需求地圖/prompt定版/商機等級.ipynb', encoding='utf-8'))
src = ''.join(nb['cells'][6]['source'])

# 1. 換成 v1beta 支援的 embedding-001
src = src.replace(
    'EMBED_MODEL      = "models/text-embedding-004"',
    'EMBED_MODEL      = "models/embedding-001"'
)

# 2. batch_embed 加 genai.configure(api_key) 確保不走 service account
old = 'def batch_embed(texts):\n    """分批取 embedding，回傳 np.ndarray (N, dim)"""\n    all_vecs = []'
new = ('def batch_embed(texts):\n'
       '    """分批取 embedding，回傳 np.ndarray (N, dim)"""\n'
       '    if GEMINI_API_KEY:\n'
       '        genai.configure(api_key=GEMINI_API_KEY)\n'
       '    all_vecs = []')

new_src = src.replace(old, new)
if new_src == src:
    print('replace failed, trying partial match...')
    print(repr(src[src.find('def batch_embed'):src.find('def batch_embed')+150]))
else:
    nb['cells'][6]['source'] = new_src
    json.dump(nb, open(r'd:/yujui/痛點需求地圖/prompt定版/商機等級.ipynb', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('done - embedding-001 + API key configure')

# -*- coding: utf-8 -*-
import json

nb = json.load(open(r'd:/yujui/痛點需求地圖/prompt定版/商機等級.ipynb', encoding='utf-8'))

fixed = False
for i, cell in enumerate(nb['cells']):
    src = ''.join(cell['source'])
    if '_stage_result' in src and '_STAGE_GROUP' in src:
        # Fix 1: _stage_result 處理 none 和 np.str_
        old = '''def _stage_result(stage, reason):
    r = _none_result(reason)
    r[stage] = True
    r["stage_group"] = _STAGE_GROUP[stage]
    return r'''

        new = '''def _stage_result(stage, reason):
    stage = str(stage)  # 確保是 Python str（KNN 回傳 np.str_）
    if stage not in _STAGE_GROUP:   # "none" 或未知 stage
        return _none_result(reason)
    r = _none_result(reason)
    r[stage] = True
    r["stage_group"] = _STAGE_GROUP[stage]
    return r'''

        new_src = src.replace(old, new)
        if new_src != src:
            nb['cells'][i]['source'] = new_src
            print(f'Cell {i} fixed')
            fixed = True
            break

if not fixed:
    print('not found, checking...')
    for i, cell in enumerate(nb['cells']):
        src = ''.join(cell['source'])
        if '_stage_result' in src:
            idx = src.find('def _stage_result')
            print(f'Cell {i}:', repr(src[idx:idx+150]))

json.dump(nb, open(r'd:/yujui/痛點需求地圖/prompt定版/商機等級.ipynb', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

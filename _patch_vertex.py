# -*- coding: utf-8 -*-
"""修改 L-Phase2深度標籤.ipynb Cell 6：改用 Vertex AI（服務帳號）取代 API Key"""
import json

NB_PATH = r'd:\yujui\痛點需求地圖\prompt定版\L-Phase2深度標籤.ipynb'
nb = json.load(open(NB_PATH, encoding='utf-8'))

old_src = ''.join(nb['cells'][6]['source'])
print("Cell 6 原始內容：")
print(old_src)
print("---")

# 找到要換掉的區段
OLD_BLOCK = (
    "GEMINI_KEY = _get_ini(cfg, 'gemini_api_key')\n"
    "client = genai.Client(api_key=GEMINI_KEY)\n"
    'print("Gemini 連線成功")\n'
)

NEW_BLOCK = (
    "import os\n"
    'os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = '
    r'r"C:/Users/DSC/yujui/auto-upload-dataset/digiwin-ai-cf22a107ca03.json"' + "\n"
    "PROJECT_ID = _get_ini(cfg, 'project_id')  # digiwin-ai\n"
    "client = genai.Client(vertexai=True, project=PROJECT_ID, location='us-central1')\n"
    'print(f"Vertex AI 連線成功（project={PROJECT_ID}）")\n'
)

if OLD_BLOCK in old_src:
    new_src = old_src.replace(OLD_BLOCK, NEW_BLOCK)
    print(">>> regex 替換成功")
else:
    # fallback：用 bytes 比對 mojibake 版本
    # 直接抓行號替換
    lines = old_src.split('\n')
    new_lines = []
    skip_next = False
    replaced = False
    for i, line in enumerate(lines):
        if "GEMINI_KEY" in line or ("api_key=GEMINI_KEY" in line):
            if not replaced:
                new_lines.append("import os")
                new_lines.append(r'os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"C:/Users/DSC/yujui/auto-upload-dataset/digiwin-ai-cf22a107ca03.json"')
                new_lines.append("PROJECT_ID = _get_ini(cfg, 'project_id')  # digiwin-ai")
                new_lines.append("client = genai.Client(vertexai=True, project=PROJECT_ID, location='us-central1')")
                replaced = True
        elif replaced and 'print' in line and ('Gemini' in line or '連線成功' in line or '\xc3\xba' in line or 's\xba\x9a' in line):
            new_lines.append('print(f"Vertex AI 連線成功（project={PROJECT_ID}）")')
            replaced = False  # 只替換一次
        else:
            new_lines.append(line)
    new_src = '\n'.join(new_lines)
    if new_src != old_src:
        print(">>> fallback 行替換成功")
    else:
        print("警告：未找到替換點，請手動修改")

nb['cells'][6]['source'] = [new_src]
json.dump(nb, open(NB_PATH, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print("notebook 已儲存")
print()
print("Cell 6 新內容：")
print(new_src)

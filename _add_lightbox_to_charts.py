# -*- coding: utf-8 -*-
"""
为痛点分类图表添加 lightbox 点击放大功能
"""
import re

# 读取 index.html
with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 三张需要添加点击功能的图片
images_to_add = [
    {
        'filename': 'heatmap_black_text_20260507.png',
        'caption': '痛需熱圖（完整分類 - 12類別）',
        'pattern': r'(<img src="痛點分類結果_Final/heatmap_black_text_20260507\.png"[^>]*>)'
    },
    {
        'filename': '痛點類別分布_v9.png',
        'caption': '痛點類別分布（總計 123,893 筆）',
        'pattern': r'(<img src="痛點分類結果_Final/痛點類別分布_v9\.png"[^>]*>)'
    },
    {
        'filename': '痛點類別完整統計_v2.png',
        'caption': '痛點類別完整統計（4維度分析）',
        'pattern': r'(<img src="痛點分類結果_Final/痛點類別完整統計_v2\.png"[^>]*>)'
    }
]

# 查找 LB_ITEMS 数组的结束位置
lb_items_match = re.search(r'(var LB_ITEMS = \[.*?\]);', html, re.DOTALL)
if not lb_items_match:
    print('[ERROR] Cannot find LB_ITEMS array')
    exit(1)

# 获取当前 LB_ITEMS 的内容
lb_items_content = lb_items_match.group(1)

# 为每张图片添加 onclick 和 LB_ITEMS 条目
for i, img_info in enumerate(images_to_add):
    # 添加 onclick 到 img 标签
    img_match = re.search(img_info['pattern'], html)
    if img_match:
        original_img = img_match.group(1)
        # 检查是否已有 onclick
        if 'onclick=' not in original_img:
            # 需要找到当前有多少个 LB_ITEMS
            current_count = lb_items_content.count('{src:')
            new_index = current_count + i

            # 添加 onclick 和 cursor:pointer style
            modified_img = original_img.replace(
                'style="',
                f'onclick="openLB({new_index})" style="cursor:pointer; '
            )
            if 'style="' not in original_img:
                modified_img = original_img.replace(
                    '>',
                    f' onclick="openLB({new_index})" style="cursor:pointer;">'
                )

            html = html.replace(original_img, modified_img)
            print('[OK] Added onclick to:', img_info["filename"])
        else:
            print('[SKIP] Already has onclick:', img_info["filename"])
    else:
        print('[WARNING] Image not found:', img_info["filename"])

# 在 LB_ITEMS 数组末尾添加新条目
new_items = []
for img_info in images_to_add:
    new_item = f',{{src:"痛點分類結果_Final/{img_info["filename"]}",caption:"{img_info["caption"]}"}}'
    new_items.append(new_item)

# 在 ]; 之前插入新条目
html = html.replace(
    lb_items_match.group(0),
    lb_items_content + ''.join(new_items) + '];'
)

# 保存修改后的文件
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('[SUCCESS] Lightbox feature added to all charts')

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增強 lightbox 功能：
1. 全螢幕顯示
2. 滾輪縮放
3. 拖曳移動（縮放後）
"""

import re

with open("REPORT.html", "r", encoding="utf-8") as f:
    content = f.read()

# 1. 更新 CSS - 全螢幕顯示 + 支援縮放和拖曳
old_lb_img_css = r'#lb-img\{max-width:92vw;max-height:88vh;border-radius:10px;box-shadow:0 0 40px rgba\(0,0,0,\.8\)\}'

new_lb_img_css = '''#lb-img{
  max-width:98vw;
  max-height:98vh;
  border-radius:4px;
  box-shadow:0 0 60px rgba(0,0,0,.9);
  cursor:grab;
  transition:transform 0.2s ease-out;
  user-select:none;
}
#lb-img.dragging{cursor:grabbing}
#lb-img.zoomed{cursor:move}'''

content = re.sub(old_lb_img_css, new_lb_img_css, content)

# 2. 添加縮放提示文字的 CSS
caption_css_insert = '''#lb-caption{color:#fff;margin-top:16px;font-size:1.1em;text-align:center;max-width:90vw}
#lb-zoom-hint{position:absolute;bottom:20px;left:50%;transform:translateX(-50%);color:#fff;font-size:0.9em;opacity:0.7;background:rgba(0,0,0,0.6);padding:8px 16px;border-radius:20px}'''

# 在 #lb-caption 之前插入（如果不存在）
if '#lb-zoom-hint' not in content:
    content = re.sub(
        r'(#lb-caption\{)',
        caption_css_insert + '\n',
        content
    )

# 3. 更新 HTML - 添加縮放提示
lb_nav_html = r'(<div id="lb-nav">.*?</div>)'
new_lb_nav_html = r'''\g<1>
  <div id="lb-zoom-hint">滾輪縮放 | 拖曳移動 | Esc 關閉</div>'''

if 'lb-zoom-hint' not in content:
    content = re.sub(lb_nav_html, new_lb_nav_html, content, flags=re.DOTALL)

# 4. 更新 JavaScript - 添加縮放和拖曳功能
js_function_insert = '''
// Lightbox 縮放和拖曳功能
var lbScale = 1;
var lbPosX = 0, lbPosY = 0;
var lbDragging = false;
var lbStartX = 0, lbStartY = 0;

function openLB(i){
  lbCur = i;
  lbScale = 1;
  lbPosX = 0;
  lbPosY = 0;
  var ov = document.getElementById('lb-overlay');
  var img = document.getElementById('lb-img');
  img.src = LB_ITEMS[i].src;
  img.style.transform = 'scale(1) translate(0px, 0px)';
  img.classList.remove('zoomed');
  document.getElementById('lb-caption').textContent = LB_ITEMS[i].caption;
  ov.classList.add('active');
  document.body.style.overflow='hidden';
}

// 滾輪縮放
document.addEventListener('wheel', function(e){
  var ov = document.getElementById('lb-overlay');
  if(!ov.classList.contains('active')) return;

  e.preventDefault();
  var img = document.getElementById('lb-img');
  var delta = e.deltaY > 0 ? -0.1 : 0.1;
  lbScale = Math.min(Math.max(0.5, lbScale + delta), 5);

  if(lbScale > 1.1) {
    img.classList.add('zoomed');
  } else {
    img.classList.remove('zoomed');
    lbPosX = 0;
    lbPosY = 0;
  }

  img.style.transform = `scale(${lbScale}) translate(${lbPosX}px, ${lbPosY}px)`;
}, {passive: false});

// 拖曳功能
document.getElementById('lb-img').addEventListener('mousedown', function(e){
  if(lbScale <= 1.1) return;
  lbDragging = true;
  lbStartX = e.clientX - lbPosX;
  lbStartY = e.clientY - lbPosY;
  this.classList.add('dragging');
});

document.addEventListener('mousemove', function(e){
  if(!lbDragging) return;
  e.preventDefault();
  lbPosX = e.clientX - lbStartX;
  lbPosY = e.clientY - lbStartY;
  document.getElementById('lb-img').style.transform = `scale(${lbScale}) translate(${lbPosX}px, ${lbPosY}px)`;
});

document.addEventListener('mouseup', function(){
  lbDragging = false;
  document.getElementById('lb-img').classList.remove('dragging');
});

'''

# 找到 openLB 函數並替換
old_openLB_pattern = r'function openLB\(i\)\{[^}]+\}'
if re.search(old_openLB_pattern, content):
    # 先移除舊的 openLB 函數
    content = re.sub(old_openLB_pattern, '', content)

# 在 closeLB 函數之前插入新的縮放和拖曳代碼
content = re.sub(
    r'(function closeLB\(\))',
    js_function_insert + r'\1',
    content
)

print("正在儲存...")
with open("REPORT.html", "w", encoding="utf-8") as f:
    f.write(content)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(content)

print("\n" + "=" * 60)
print("OK - Lightbox 功能增強完成！")
print("=" * 60)
print("\n新功能：")
print("1. OK - 全螢幕顯示（98vw × 98vh）")
print("2. OK - 滾輪縮放（0.5x - 5x）")
print("3. OK - 拖曳移動（縮放 > 1.1x 時啟用）")
print("4. OK - 視覺提示（滾輪縮放 | 拖曳移動 | Esc 關閉）")
print("\n操作方式：")
print("- 點擊圖片：開啟 lightbox")
print("- 滾輪向上：放大")
print("- 滾輪向下：縮小")
print("- 滑鼠拖曳：移動圖片（放大時）")
print("- Esc 鍵：關閉")
print("- ← → 鍵：切換圖片")
print("=" * 60)

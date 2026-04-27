# -*- coding: utf-8 -*-
"""
生成：
  1. results/phaseM/radar_c{0-6}.png  — 7 張個別雷達圖（高解析）
  2. _pca_plotly.json                 — Plotly 互動 PCA 資料（嵌入 REPORT.html）
"""
import json, base64, pathlib, io
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont

BASE  = pathlib.Path(r"d:\yujui\痛點需求地圖\prompt定版")
OUT_M = BASE / "results" / "phaseM"

# ── 資料 ─────────────────────────────────────────────────────────
profiles = pd.read_csv(OUT_M / "cluster_profiles.csv", index_col=0)
clusters = pd.read_csv(OUT_M / "company_clusters.csv", dtype={"cluster": int}, low_memory=False)

CLUSTER_NAMES = {
    0: "C0 微型內銷", 1: "C1 標準內銷", 2: "C2 大型外商",
    3: "C3 多面型強者", 4: "C4 品牌驅動",
    5: "C5 家族外銷", 6: "C6 外資貿易"
}
CLUSTER_COUNTS = clusters["cluster"].value_counts().to_dict()

COLORS = {
    0: "#9e9e9e", 1: "#2196f3", 2: "#4caf50",
    3: "#ff5722", 4: "#9c27b0", 5: "#ff9800", 6: "#00bcd4"
}

# 雷達圖使用的 8 個特徵
FEAT_COLS = ["f_foreign", "f_biz_model", "f_headcount", "f_n_trade_ctry",
             "f_n_competitor", "f_n_brand", "f_n_issues", "f_n_customer"]
FEAT_LABELS = ["外商比例", "商業模式", "員工規模", "貿易國數",
               "競爭者數", "品牌數", "議題數", "客戶數"]
# 對應單位；外商比例特殊處理（×100 → %）
FEAT_UNITS  = ["%", "", "人", "國", "個", "個", "個", "個"]
FEAT_PCT    = [True, False, False, False, False, False, False, False]  # 是否 ×100

# 用 floor normalization（C0 可見）
feat_vals = profiles[FEAT_COLS].values.astype(float)
mn = feat_vals.min(axis=0)
mx = feat_vals.max(axis=0)
normed = 0.35 + 0.65 * (feat_vals - mn) / (mx - mn + 1e-9)

# ══════════════════════════════════════════════════════════════════
# 1. 7 張個別雷達圖
# ══════════════════════════════════════════════════════════════════
FONT_PATH = r"C:\Windows\Fonts\msjh.ttc"
N = len(FEAT_COLS)
ANGLES = [2 * np.pi * i / N for i in range(N)] + [0]  # 閉合

def draw_radar_single(cluster_id: int) -> pathlib.Path:
    """畫單一 cluster 雷達圖，回傳儲存路徑"""
    W, H = 700, 680
    PAD   = 80   # 四邊留給標籤
    CX, CY = W // 2, (H - 60) // 2 + 20   # 圓心（底部留 60px 給標題）
    R_MAX  = min(CX, CY) - PAD             # 最大半徑
    R_LBL  = R_MAX + 36                    # 標籤半徑

    color_hex = COLORS[cluster_id]
    vals = normed[cluster_id]
    # 閉合
    vx = [CX + vals[i] * R_MAX * np.cos(ANGLES[i] - np.pi/2) for i in range(N)] + \
         [CX + vals[0] * R_MAX * np.cos(ANGLES[0] - np.pi/2)]
    vy = [CY + vals[i] * R_MAX * np.sin(ANGLES[i] - np.pi/2) for i in range(N)] + \
         [CY + vals[0] * R_MAX * np.sin(ANGLES[0] - np.pi/2)]

    # ── matplotlib 畫雷達多邊形 ──
    fig, ax = plt.subplots(figsize=(W/100, H/100), dpi=100)
    ax.set_xlim(0, W); ax.set_ylim(0, H); ax.axis("off")
    ax.set_facecolor("#1a2035"); fig.patch.set_facecolor("#1a2035")

    # 背景同心圓
    for r in [0.25, 0.5, 0.75, 1.0]:
        bx = [CX + r * R_MAX * np.cos(ANGLES[i] - np.pi/2) for i in range(N+1)]
        by = [CY + r * R_MAX * np.sin(ANGLES[i] - np.pi/2) for i in range(N+1)]
        ax.plot(bx, by, color="#2d4a7a", linewidth=0.8, zorder=1)

    # 軸線
    for i in range(N):
        ax.plot([CX, CX + R_MAX * np.cos(ANGLES[i] - np.pi/2)],
                [CY, CY + R_MAX * np.sin(ANGLES[i] - np.pi/2)],
                color="#2d4a7a", linewidth=0.8, zorder=1)

    # 填色多邊形
    poly_color = tuple(int(color_hex[j:j+2], 16)/255 for j in (1,3,5)) + (0.35,)
    ax.fill(vx[:-1], vy[:-1], color=poly_color, zorder=2)
    ax.plot(vx, vy, color=color_hex, linewidth=2.2, zorder=3)
    ax.scatter(vx[:-1], vy[:-1], color=color_hex, s=40, zorder=4)

    # 轉成 PIL 加中文文字
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=100, facecolor=fig.get_facecolor())
    plt.close(fig)
    buf.seek(0)
    img = Image.open(buf).convert("RGB")

    draw = ImageDraw.Draw(img)
    try:
        fnt_lbl  = ImageFont.truetype(FONT_PATH, 17)
        fnt_val  = ImageFont.truetype(FONT_PATH, 13)
        fnt_title= ImageFont.truetype(FONT_PATH, 20)
        fnt_sub  = ImageFont.truetype(FONT_PATH, 14)
    except Exception:
        fnt_lbl = fnt_val = fnt_title = fnt_sub = ImageFont.load_default()

    # 8 個特徵標籤
    for i in range(N):
        lx = CX + R_LBL * np.cos(ANGLES[i] - np.pi/2)
        ly = CY + R_LBL * np.sin(ANGLES[i] - np.pi/2)
        label = FEAT_LABELS[i]
        bb = draw.textbbox((0,0), label, font=fnt_lbl)
        tw, th = bb[2]-bb[0], bb[3]-bb[1]
        draw.text((lx - tw/2, ly - th/2), label, font=fnt_lbl, fill="#7dd3fc")

        # 數值 + 單位
        raw_val = feat_vals[cluster_id][i]
        display_val = raw_val * 100 if FEAT_PCT[i] else raw_val
        unit = FEAT_UNITS[i]
        if FEAT_PCT[i]:
            val_str = f"{display_val:.1f}{unit}"
        elif display_val < 100:
            val_str = f"{display_val:.2f}{unit}"
        else:
            val_str = f"{display_val:.0f}{unit}"
        bb2 = draw.textbbox((0,0), val_str, font=fnt_val)
        tw2, th2 = bb2[2]-bb2[0], bb2[3]-bb2[1]
        draw.text((lx - tw2/2, ly - th/2 + th + 2), val_str, font=fnt_val, fill="#94a3b8")

    # C0 特別標注
    if cluster_id == 0:
        note = "各維度均為最低基準群"
        bb_n = draw.textbbox((0,0), note, font=fnt_sub)
        tw_n = bb_n[2]-bb_n[0]
        draw.text(((W-tw_n)//2, CY - 12), note, font=fnt_sub, fill="#f59e0b")

    out_path = OUT_M / f"radar_c{cluster_id}.png"
    img.save(str(out_path), dpi=(150, 150))
    print(f"  ✅ radar_c{cluster_id}.png")
    return out_path

print("生成 7 張個別雷達圖...")
radar_paths = [draw_radar_single(i) for i in range(7)]
print()

# ══════════════════════════════════════════════════════════════════
# 2. Plotly PCA 互動資料
# ══════════════════════════════════════════════════════════════════
print("生成 Plotly PCA 資料...")

SAMPLE_N = 50000
sample = clusters.dropna(subset=["pca_x","pca_y","cluster"]).copy()
sample["cluster"] = sample["cluster"].astype(int)
if len(sample) > SAMPLE_N:
    sample = sample.sample(SAMPLE_N, random_state=42)

# 準備每個 cluster 的 trace 資料
PLOTLY_COLORS = {
    0: "#9e9e9e", 1: "#2196f3", 2: "#4caf50",
    3: "#ff5722", 4: "#9c27b0", 5: "#ff9800", 6: "#00bcd4"
}

traces = []
for cid in sorted(sample["cluster"].unique()):
    sub = sample[sample["cluster"] == cid]
    cnt = CLUSTER_COUNTS.get(cid, 0)
    traces.append({
        "type": "scattergl",
        "x": sub["pca_x"].round(4).tolist(),
        "y": sub["pca_y"].round(4).tolist(),
        "mode": "markers",
        "name": f"{CLUSTER_NAMES[cid]} ({cnt:,}家)",
        "marker": {
            "color": PLOTLY_COLORS[cid],
            "size": 3,
            "opacity": 0.6
        },
        "hovertemplate": f"<b>{CLUSTER_NAMES[cid]}</b><br>PCA1: %{{x:.2f}}<br>PCA2: %{{y:.2f}}<extra></extra>"
    })

# 群中心標注
centers = clusters.groupby("cluster")[["pca_x","pca_y"]].mean().reset_index()
anno_traces = []
for _, row in centers.iterrows():
    cid = int(row["cluster"])
    anno_traces.append({
        "type": "scatter",
        "x": [round(row["pca_x"], 3)],
        "y": [round(row["pca_y"], 3)],
        "mode": "text",
        "text": [CLUSTER_NAMES[cid].split()[0]],  # "C0"
        "textfont": {"size": 13, "color": "white"},
        "showlegend": False,
        "hoverinfo": "skip"
    })

layout = {
    "paper_bgcolor": "#0f1117",
    "plot_bgcolor": "#1a2035",
    "font": {"color": "#e2e8f0", "family": "Microsoft JhengHei, sans-serif"},
    "title": {"text": "PCA 散點圖 — 7 種法人類型分布（50,000 樣本，可縮放/拖曳）",
               "font": {"size": 16, "color": "#7dd3fc"}},
    "xaxis": {"title": "PCA 主成分 1", "gridcolor": "#2d3748",
               "zerolinecolor": "#4a5568"},
    "yaxis": {"title": "PCA 主成分 2", "gridcolor": "#2d3748",
               "zerolinecolor": "#4a5568"},
    "legend": {"bgcolor": "rgba(26,32,53,0.8)", "bordercolor": "#2d4a7a",
                "borderwidth": 1},
    "margin": {"l": 60, "r": 20, "t": 60, "b": 60},
    "height": 520,
    "hovermode": "closest",
    "dragmode": "zoom"
}

plotly_data = {"data": traces + anno_traces, "layout": layout}

pca_json_path = BASE / "_pca_plotly.json"
pca_json_path.write_text(json.dumps(plotly_data, ensure_ascii=False), encoding="utf-8")
print(f"  ✅ _pca_plotly.json（{pca_json_path.stat().st_size//1024} KB）")

# ══════════════════════════════════════════════════════════════════
# 3. 更新 results/phaseM 同步雷達圖
# ══════════════════════════════════════════════════════════════════
# 也把 7 張複製到 results 供 git 追蹤
import shutil
for i in range(7):
    src = OUT_M / f"radar_c{i}.png"
    dst = BASE / "results" / "phaseM" / f"radar_c{i}.png"
    shutil.copy2(src, dst)
print("  ✅ 7 張雷達圖已複製到 results/phaseM/")

print("\n全部完成！")

# -*- coding: utf-8 -*-
"""生成 REPORT.html v2 — 含 Lightbox + 7 張個別雷達圖 + Plotly 互動 PCA"""
import base64, json, pathlib

BASE = pathlib.Path(r"d:\yujui\痛點需求地圖\prompt定版")

def b64img(rel):
    p = BASE / rel
    return base64.b64encode(p.read_bytes()).decode() if p.exists() else ""

# 7 張雷達圖 base64
radar_b64 = [b64img(f"results/phaseM/radar_c{i}.png") for i in range(7)]
pca_b64   = b64img("results/phaseM/cluster_pca_map.png")

# Plotly JSON
plotly_data = json.loads((BASE / "_pca_plotly.json").read_text(encoding="utf-8"))
plotly_json = json.dumps(plotly_data, ensure_ascii=False)

CLUSTER_INFO = [
    ("#9e9e9e", "C0 微型內銷",   "141,323 家", "所有維度最低，純本土小型企業，員工 8.6 人"),
    ("#2196f3", "C1 標準內銷",   " 38,247 家", "員工 83 人，中小規模製造內銷"),
    ("#4caf50", "C2 大型外商",   " 11,284 家", "員工 993 人，22.6% 外資，貿易國廣"),
    ("#ff5722", "C3 多面型強者", "  5,621 家", "外商 29%+家族 31%，貿易國最多，產業領袖"),
    ("#9c27b0", "C4 品牌驅動",   "  4,133 家", "品牌數最高（2.86），強品牌意識中型企業"),
    ("#ff9800", "C5 家族外銷",   "  3,872 家", "家族 99.9%，外銷製造，員工 87 人"),
    ("#00bcd4", "C6 外資貿易",   "  2,337 家", "外商 99.1%，貿易國最廣，標準外資分公司"),
]

parts = []

# ── HEAD ─────────────────────────────────────────────────────────
parts.append("""<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>業務日誌 LLM 智慧萃取系統 — 技術文件</title>
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
<style>
*{box-sizing:border-box}
body{font-family:'Microsoft JhengHei','Noto Sans TC',sans-serif;background:#0f1117;color:#e2e8f0;margin:0;padding:0}
.hero{background:linear-gradient(135deg,#1e3a5f,#0f2744 50%,#1a1040);padding:60px 40px;text-align:center;border-bottom:2px solid #2d4a7a}
.hero h1{font-size:2.4em;color:#7dd3fc;margin:0 0 12px}
.hero p{color:#94a3b8;font-size:1.1em;margin:6px 0}
.tagline{color:#a78bfa;font-size:1.2em;margin-top:18px;font-weight:bold}
.badge-row{display:flex;gap:10px;justify-content:center;margin-top:22px;flex-wrap:wrap}
.badge{background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.15);border-radius:20px;padding:5px 14px;font-size:.83em;color:#94a3b8}
.badge.green{border-color:#10b981;color:#10b981}
.badge.blue{border-color:#3b82f6;color:#3b82f6}
.badge.yellow{border-color:#f59e0b;color:#f59e0b}
nav{background:#1a1f2e;border-bottom:1px solid #2d3748;position:sticky;top:0;z-index:100;padding:0 40px}
nav ul{display:flex;list-style:none;margin:0;padding:0;overflow-x:auto}
nav a{display:block;padding:13px 17px;color:#94a3b8;text-decoration:none;font-size:.88em;white-space:nowrap;border-bottom:2px solid transparent;transition:all .2s}
nav a:hover{color:#7dd3fc;border-color:#7dd3fc}
.section{max-width:1100px;margin:0 auto;padding:56px 40px;border-bottom:1px solid #1e2a3a}
.section h2{color:#7dd3fc;font-size:1.75em;border-left:4px solid #3b82f6;padding-left:14px;margin-bottom:28px}
.section h3{color:#a78bfa;font-size:1.15em;margin-top:28px}
.phase-card{background:#1a2035;border:1px solid #2d4a7a;border-radius:12px;padding:22px 26px;margin-bottom:18px;border-left:4px solid #64748b}
.phase-card.done{border-left-color:#10b981}
.phase-card.running{border-left-color:#f59e0b}
.phase-card.pending{border-left-color:#475569}
.phase-tag{display:inline-block;padding:3px 10px;border-radius:12px;font-size:.76em;font-weight:bold;margin-bottom:8px}
.tag-done{background:#064e3b;color:#10b981;border:1px solid #10b981}
.tag-running{background:#451a03;color:#f59e0b;border:1px solid #f59e0b}
.tag-pending{background:#1e293b;color:#64748b;border:1px solid #64748b}
.phase-title{font-size:1.1em;color:#e2e8f0;font-weight:bold;margin-bottom:5px}
.phase-meta{color:#94a3b8;font-size:.88em}
.stats-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(165px,1fr));gap:14px;margin:22px 0}
.stat-box{background:#1a2035;border:1px solid #2d4a7a;border-radius:10px;padding:18px;text-align:center}
.stat-num{font-size:1.85em;font-weight:bold;color:#7dd3fc}
.stat-label{color:#94a3b8;font-size:.82em;margin-top:5px}
pre{background:#0d1117;border:1px solid #2d3748;border-radius:10px;padding:16px 20px;overflow-x:auto;margin:16px 0;line-height:1.65}
pre code{font-family:'Cascadia Code','Fira Code',Consolas,monospace;font-size:.87em;color:#e2e8f0}
.kw{color:#ff7b72}.fn{color:#d2a8ff}.st{color:#a5d6ff}.nm{color:#f2cc60}.cm{color:#8b949e;font-style:italic}
table{width:100%;border-collapse:collapse;margin:16px 0}
th{background:#1e2d4a;color:#7dd3fc;padding:9px 13px;text-align:left;font-size:.87em;border-bottom:2px solid #2d4a7a}
td{padding:9px 13px;border-bottom:1px solid #1e2a3a;font-size:.85em;color:#cbd5e1}
tr:hover td{background:#1a2035}
/* ── Radar Grid ─────────────────────── */
.radar-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:24px 0}
@media(max-width:900px){.radar-grid{grid-template-columns:repeat(2,1fr)}}
@media(max-width:500px){.radar-grid{grid-template-columns:1fr}}
.radar-card{background:#1a2035;border:1px solid #2d4a7a;border-radius:10px;overflow:hidden;cursor:zoom-in;transition:transform .2s,box-shadow .2s}
.radar-card:hover{transform:scale(1.03);box-shadow:0 4px 20px rgba(0,0,0,.5)}
.radar-card img{width:100%;display:block}
.radar-card .rc-footer{padding:8px 10px;font-size:.8em}
.rc-name{color:#7dd3fc;font-weight:bold}
.rc-count{color:#94a3b8;font-size:.78em}
/* ── PCA filter bar ─────────────────── */
.pca-filter-bar{display:flex;align-items:center;flex-wrap:wrap;gap:6px;margin:18px 0 10px;padding:10px 14px;background:#1a2035;border:1px solid #2d4a7a;border-radius:10px}
.cf-label{color:#94a3b8;font-size:.82em;margin-right:4px}
.cf-sep{color:#4a5568;margin:0 4px}
.cf-ctrl{background:#1e2a3a;border:1px solid #4a5568;color:#94a3b8;padding:4px 12px;border-radius:6px;cursor:pointer;font-size:.8em;transition:all .15s}
.cf-ctrl:hover{background:#2d3748;color:#e2e8f0}
.cf-btn{background:#1e2a3a;border:2px solid var(--c);color:#94a3b8;padding:4px 11px;border-radius:6px;cursor:pointer;font-size:.8em;font-weight:bold;transition:all .15s;opacity:.45}
.cf-btn.active{background:color-mix(in srgb,var(--c) 20%,#1a2035);color:var(--c);opacity:1;box-shadow:0 0 0 1px var(--c) inset}
/* ── PCA container ──────────────────── */
.pca-wrap{background:#1a2035;border:1px solid #2d4a7a;border-radius:12px;overflow:hidden;margin:0 0 24px}
/* ── Lightbox ───────────────────────── */
#lb-overlay{display:none;position:fixed;inset:0;background:rgba(0,0,0,.88);z-index:9999;align-items:center;justify-content:center;flex-direction:column}
#lb-overlay.active{display:flex}
#lb-img{max-width:92vw;max-height:88vh;border-radius:10px;box-shadow:0 0 40px rgba(0,0,0,.8)}
#lb-close{position:absolute;top:16px;right:24px;font-size:2em;color:#fff;cursor:pointer;opacity:.7;transition:opacity .2s;background:none;border:none;line-height:1}
#lb-close:hover{opacity:1}
#lb-caption{margin-top:12px;color:#94a3b8;font-size:.9em;text-align:center;max-width:600px}
#lb-nav{display:flex;gap:20px;margin-top:16px}
#lb-nav button{background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.2);color:#e2e8f0;padding:8px 22px;border-radius:8px;cursor:pointer;font-size:.95em;transition:background .2s}
#lb-nav button:hover{background:rgba(255,255,255,.22)}
/* layer + signal grids */
.layer-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:12px;margin:20px 0}
.lcard{background:#1a2035;border:1px solid #2d4a7a;border-radius:10px;padding:14px 16px}
.lnum{font-size:1.3em;font-weight:bold;color:#7dd3fc}
.lname{color:#a78bfa;font-weight:bold;margin-bottom:6px}
.lfields{color:#94a3b8;font-size:.83em;margin-bottom:4px}
.lexample{color:#10b981;font-size:.8em;font-style:italic}
.sig-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin:20px 0}
.scard{background:#1a2035;border:1px solid #374151;border-radius:10px;padding:16px}
.sicon{font-size:1.7em;margin-bottom:6px}
.sname{font-weight:bold;color:#e2e8f0;margin-bottom:4px;font-size:.93em}
.sdesc{color:#94a3b8;font-size:.82em}
.step-list{list-style:none;padding:0;margin:0}
.step-list li{display:flex;align-items:flex-start;gap:12px;padding:11px 0;border-bottom:1px solid #1e2a3a}
.step-list li:last-child{border-bottom:none}
.step-tag{background:#1e3a5f;color:#7dd3fc;border:1px solid #3b82f6;padding:3px 9px;border-radius:6px;font-size:.76em;font-weight:bold;white-space:nowrap;margin-top:2px;flex-shrink:0}
.sc{flex:1}
.sp{color:#94a3b8;font-size:.85em;margin-top:3px}
.sr{color:#10b981;font-size:.82em;margin-top:3px}
.two-col{display:grid;grid-template-columns:1fr 1fr;gap:20px;margin:18px 0}
.box{background:#1a2035;border:1px solid #2d4a7a;border-radius:10px;padding:16px}
.box h4{margin:0 0 10px;color:#7dd3fc;font-size:.93em}
.crow{display:flex;align-items:center;gap:10px;padding:9px 13px;border-bottom:1px solid #1e2a3a}
.cdot{width:12px;height:12px;border-radius:50%;flex-shrink:0}
.cname{font-weight:bold;color:#e2e8f0;min-width:108px;font-size:.9em}
.ccount{color:#7dd3fc;min-width:90px;font-size:.85em}
.cdesc{color:#94a3b8;font-size:.82em}
footer{text-align:center;padding:36px;color:#475569;font-size:.83em;border-top:1px solid #1e2a3a}
@media(max-width:768px){.two-col,.sig-grid{grid-template-columns:1fr}.section{padding:36px 18px}.hero{padding:36px 18px}}
</style>
</head>
<body>
""")

# ── HERO ─────────────────────────────────────────────────────────
parts.append("""
<div class="hero">
  <h1>業務日誌 LLM 智慧萃取系統</h1>
  <p class="tagline">百萬篇業務日報 → 零人工 L1–L7 分類 → 法人標籤 → 聚類分析 → 痛需地圖</p>
  <p>Business Log Intelligence Pipeline &nbsp;·&nbsp; LLM + Embedding + KNN + KMeans</p>
  <div class="badge-row">
    <span class="badge green">1,802,590 筆日報已分類</span>
    <span class="badge green">206,817 家法人已標籤</span>
    <span class="badge blue">7 群聚類已完成</span>
    <span class="badge yellow">Phase 2 執行中 6.8%</span>
    <span class="badge">Gemini 2.0 Flash</span>
    <span class="badge">sklearn KMeans + PCA</span>
  </div>
</div>
<nav><ul>
  <li><a href="#overview">系統概覽</a></li>
  <li><a href="#framework">L1–L7 框架</a></li>
  <li><a href="#phaseL">Phase L：分類</a></li>
  <li><a href="#phase1">Phase 1：法人</a></li>
  <li><a href="#phaseM">Phase M：聚類</a></li>
  <li><a href="#phase2">Phase 2：深度標籤</a></li>
  <li><a href="#results">結果一覽</a></li>
</ul></nav>
""")

# ── OVERVIEW ─────────────────────────────────────────────────────
parts.append("""
<div class="section" id="overview">
  <h2>系統概覽</h2>
  <div class="stats-grid">
    <div class="stat-box"><div class="stat-num">1,802,590</div><div class="stat-label">業務日報總筆數</div></div>
    <div class="stat-box"><div class="stat-num">206,817</div><div class="stat-label">法人公司數</div></div>
    <div class="stat-box"><div class="stat-num">82,105</div><div class="stat-label">問卷三大信號</div></div>
    <div class="stat-box"><div class="stat-num">7</div><div class="stat-label">法人聚類分群</div></div>
    <div class="stat-box"><div class="stat-num">73.67%</div><div class="stat-label">KNN 分類準確率</div></div>
    <div class="stat-box"><div class="stat-num">0</div><div class="stat-label">人工標注（Phase L）</div></div>
  </div>
  <h3>流程架構</h3>
  <div class="phase-card done"><span class="phase-tag tag-done">✅ 完成</span>
    <div class="phase-title">Phase 0 — 問卷 Adapter</div>
    <div class="phase-meta">萃取 82,105 筆三大信號（Pain / Need / Insight），格式化為 survey_signals.jsonl</div></div>
  <div class="phase-card done"><span class="phase-tag tag-done">✅ 完成</span>
    <div class="phase-title">Phase L — L1–L7 零人工分類（1,802,590 筆）</div>
    <div class="phase-meta">Step 0 LLM 種子庫（2,375 筆，73.67% KNN）→ Step 1 規則快篩（867k）→ Step 2 Embedding+KNN（936k）→ Step 3 SC LLM（14 筆）</div></div>
  <div class="phase-card done"><span class="phase-tag tag-done">✅ 完成</span>
    <div class="phase-title">Phase 1 — 法人標籤（206,817 家）</div>
    <div class="phase-meta">8 大類法人屬性：外商 / 家族 / 商業模式 / 員工規模 / 貿易國數 / 競爭者數 / 品牌數 / 議題數</div></div>
  <div class="phase-card done"><span class="phase-tag tag-done">✅ 完成</span>
    <div class="phase-title">Phase M — 分層聚類 + 痛需地圖</div>
    <div class="phase-meta">KMeans(k=7) × PCA 視覺化 × Top-30 熱路徑，產出 7 種法人類型</div></div>
  <div class="phase-card running"><span class="phase-tag tag-running">🔄 執行中 6.8%</span>
    <div class="phase-title">Phase 2 — 日報深度標籤（L1–L7 結構化）</div>
    <div class="phase-meta">每篇日報 × 7 層 × 3 欄位，~178,790 家公司，Gemini 2.0 Flash，6 Workers</div></div>
  <div class="phase-card pending"><span class="phase-tag tag-pending">⬜ 待建立</span>
    <div class="phase-title">Phase 3 — 痛需熱圖 + 三輸出</div>
    <div class="phase-meta">Phase 2 × 商機等級（E/D/C2/C1/B/A）× PhaseM 聚類 → 推薦問項 / 開發方案卡 / 機會卡</div></div>
</div>
""")

# ── FRAMEWORK ─────────────────────────────────────────────────────
parts.append("""
<div class="section" id="framework">
  <h2>L1–L7 七層框架</h2>
  <div class="layer-grid">
    <div class="lcard"><div class="lnum">L1</div><div class="lname">痛點層</div><div class="lfields">痛點類型 / 衝擊程度 / 緊迫度</div><div class="lexample">例：原料成本上漲 / 高 / 急迫</div></div>
    <div class="lcard"><div class="lnum">L2</div><div class="lname">角色層</div><div class="lfields">決策角色 / 壓力來源 / 負責 KPI</div><div class="lexample">例：採購經理 / 總部壓成本 / 毛利率</div></div>
    <div class="lcard"><div class="lnum">L3</div><div class="lname">目標層</div><div class="lfields">目標類型 / 時程 / 核心 KPI</div><div class="lexample">例：降低庫存 / Q3 達成 / 周轉天數</div></div>
    <div class="lcard"><div class="lnum">L4</div><div class="lname">議題層</div><div class="lfields">議題名稱 / 驅動因素 / 客戶立場</div><div class="lexample">例：ERP 升級 / 法規要求 / 觀望評估</div></div>
    <div class="lcard"><div class="lnum">L5</div><div class="lname">評估層</div><div class="lfields">評估項目 / 競爭者 / 決策標準</div><div class="lexample">例：交期/品質 / SAP/Oracle / 價格優先</div></div>
    <div class="lcard"><div class="lnum">L6</div><div class="lname">方向層</div><div class="lfields">策略方向 / 觸發事件 / 當前溫度</div><div class="lexample">例：轉向數位化 / 客訴增加 / 積極</div></div>
    <div class="lcard"><div class="lnum">L7</div><div class="lname">成果層</div><div class="lfields">結果類型 / 關鍵因素 / 下一步</div><div class="lexample">例：成交 / 價格合理 / 安排簽約</div></div>
  </div>
  <h3>三大信號（Phase 0 問卷萃取）</h3>
  <div class="sig-grid">
    <div class="scard"><div class="sicon">💢</div><div class="sname">Pain 痛點信號</div><div class="sdesc">客戶明確表達的困難與阻礙，對應 L1，用於驗證日報萃取準確性</div></div>
    <div class="scard"><div class="sicon">🎯</div><div class="sname">Need 需求信號</div><div class="sdesc">客戶希望達成的目標，對應 L3，反映採購決策的核心動機</div></div>
    <div class="scard"><div class="sicon">💡</div><div class="sname">Insight 洞察信號</div><div class="sdesc">業務員主觀判斷，對應 L4–L6，補充日報空白</div></div>
  </div>
</div>
""")

# ── PHASE L ───────────────────────────────────────────────────────
parts.append("""
<div class="section" id="phaseL">
  <h2>Phase L — L1–L7 零人工分類</h2>
  <ul class="step-list">
    <li><span class="step-tag">Step 0</span><div class="sc"><strong>LLM 種子庫建立（2,375 筆）</strong><div class="sp">目的：從真實日報 LLM 標注，建立 KNN 分類基礎</div><div class="sr">結果：73.67% Top-1 準確率（目標 70%），各層 ≥ 291 筆</div></div></li>
    <li><span class="step-tag">Step 1</span><div class="sc"><strong>關鍵詞規則快篩（HIGH 867,023 筆）</strong><div class="sp">HIGH_THRESHOLD=2（命中 ≥2 詞直接定案）；SHORT_TEXT_LEN=50 過濾雜訊</div><div class="sr">覆蓋率 20.93%；MEDIUM 23.22% 送 Step 2；SKIP 55.85%</div></div></li>
    <li><span class="step-tag">Step 2</span><div class="sc"><strong>Embedding + KNN（935,570 筆）</strong><div class="sp">text-embedding-004（768 維），KNN k=5，cosine 距離，HIGH ≥ 0.65</div><div class="sr">100% HIGH，L1 最多（343,184），L4 最少（25,695）</div></div></li>
    <li><span class="step-tag">Step 3</span><div class="sc"><strong>Self-Consistency LLM（14 筆兜底）</strong><div class="sp">同一日報送 Gemini 3 次取多數決，confidence ≥ 0.67</div><div class="sr">71.4% CONFIRM_HIGH，21.4% UNCERTAIN（標記降權）</div></div></li>
  </ul>
  <table>
    <tr><th>L 層</th><th>Step1 HIGH</th><th>Step2 HIGH</th><th>最終合計</th></tr>
    <tr><td>L1 痛點層</td><td>118,076</td><td>343,184</td><td>461,267</td></tr>
    <tr><td>L2 角色層</td><td>190,008</td><td>176,434</td><td>366,442</td></tr>
    <tr><td>L3 目標層</td><td> 68,938</td><td>114,686</td><td>183,624</td></tr>
    <tr><td>L4 議題層</td><td> 30,981</td><td> 25,695</td><td> 56,679</td></tr>
    <tr><td>L5 評估層</td><td>314,471</td><td>119,093</td><td>433,565</td></tr>
    <tr><td>L6 方向層</td><td>  6,667</td><td>107,900</td><td>114,567</td></tr>
    <tr><td>L7 成果層</td><td>137,882</td><td> 48,528</td><td>186,410</td></tr>
  </table>
</div>
""")

# ── PHASE 1 ───────────────────────────────────────────────────────
parts.append("""
<div class="section" id="phase1">
  <h2>Phase 1 — 法人標籤（206,817 家）</h2>
  <div class="two-col">
    <div class="box"><h4>模型設定</h4>
      <pre style="margin:0"><code>MODEL = <span class="st">"gemini-2.0-flash"</span>
TEMP = <span class="nm">0.1</span>  |  RPM_LIMIT = <span class="nm">30</span></code></pre>
    </div>
    <div class="box"><h4>8 大標籤維度</h4>
      <ul style="color:#94a3b8;font-size:.85em;margin:0;padding-left:18px;line-height:2">
        <li>外商比例 / 家族企業 / 商業模式</li>
        <li>員工規模 / 貿易國數 / 競爭者數</li>
        <li>品牌數 / 議題數</li>
      </ul>
    </div>
  </div>
</div>
""")

# ── PHASE M ───────────────────────────────────────────────────────
parts.append("""
<div class="section" id="phaseM">
  <h2>Phase M — 分層聚類 + 痛需地圖</h2>
  <ul class="step-list">
    <li><span class="step-tag">A1–A2</span><div class="sc"><strong>特徵萃取 + L 層路徑索引</strong><div class="sp">15 維數值向量 + company_index {id→{L層→[年月]}}</div></div></li>
    <li><span class="step-tag">B1–B3</span><div class="sc"><strong>StandardScaler → KMeans(k=7) → PCA(2D)</strong><div class="sp">消除量綱 → 分群 → PCA 解釋率 ~60%</div><div class="sr">7 種法人類型，群間分離明顯</div></div></li>
    <li><span class="step-tag">C1–C2</span><div class="sc"><strong>compress_path() → Top-30 熱路徑</strong><div class="sp">去除連續重複 L 層，保留轉折；L2→L1 以 3.97% 居首</div></div></li>
  </ul>
""")

# PCA 互動圖 + 篩選按鈕
cluster_filter_buttons = ""
for i, (color, name, count, desc) in enumerate(CLUSTER_INFO):
    short = name.split()[0]  # "C0"
    cluster_filter_buttons += f"""<button class="cf-btn active" data-idx="{i}" style="--c:{color}" onclick="toggleCluster({i},this)">{short}</button>"""

parts.append(f"""
  <h3>PCA 散點圖 — 互動版（可縮放 / 拖曳 / Hover）</h3>
  <div class="pca-filter-bar">
    <span class="cf-label">篩選群組：</span>
    <button class="cf-ctrl" onclick="selectAllClusters()">全選</button>
    <button class="cf-ctrl" onclick="clearAllClusters()">全消</button>
    <span class="cf-sep">|</span>
    {cluster_filter_buttons}
  </div>
  <div class="pca-wrap">
    <div id="pca-plot" style="width:100%;height:520px"></div>
  </div>
  <script>
  (function(){{
    var plotlyData = {plotly_json};
    var config = {{responsive:true, displayModeBar:true,
                   modeBarButtonsToRemove:['select2d','lasso2d','autoScale2d'],
                   displaylogo:false}};
    Plotly.newPlot('pca-plot', plotlyData.data, plotlyData.layout, config);

    /* 篩選按鈕邏輯 ---------------------------------------- */
    /* plotlyData.data 前 7 條是 scattergl（cluster 0-6），後面是標注 */
    var N_CLUSTER = 7;
    var visible = [true,true,true,true,true,true,true];

    function applyVisibility(){{
      /* cluster traces: indices 0~6; annotation traces 7~13 */
      var vArr = visible.map(function(v){{return v ? true : 'legendonly';}});
      var annoVArr = visible.map(function(v){{return v ? true : 'legendonly';}});
      Plotly.restyle('pca-plot', {{visible: vArr}}, [...Array(N_CLUSTER).keys()]);
      if(plotlyData.data.length > N_CLUSTER){{
        Plotly.restyle('pca-plot', {{visible: annoVArr}},
          [...Array(plotlyData.data.length - N_CLUSTER).keys()].map(function(k){{return k+N_CLUSTER;}}));
      }}
    }}

    window.toggleCluster = function(idx, btn){{
      visible[idx] = !visible[idx];
      btn.classList.toggle('active', visible[idx]);
      applyVisibility();
    }};
    window.selectAllClusters = function(){{
      visible = visible.map(function(){{return true;}});
      document.querySelectorAll('.cf-btn').forEach(function(b){{b.classList.add('active');}});
      applyVisibility();
    }};
    window.clearAllClusters = function(){{
      visible = visible.map(function(){{return false;}});
      document.querySelectorAll('.cf-btn').forEach(function(b){{b.classList.remove('active');}});
      applyVisibility();
    }};
  }})();
  </script>
""")

# 7 張個別雷達圖
radar_cards = ""
for i, (color, name, count, desc) in enumerate(CLUSTER_INFO):
    short = name.split()[0]  # "C0"
    b64 = radar_b64[i]
    radar_cards += f"""
    <div class="radar-card" onclick="openLB({i})" title="點擊放大 {name}">
      <img src="data:image/png;base64,{b64}" alt="{name}" loading="lazy">
      <div class="rc-footer">
        <div class="rc-name" style="color:{color}">{name}</div>
        <div class="rc-count">{count.strip()} &nbsp;·&nbsp; {desc}</div>
      </div>
    </div>"""

parts.append(f"""
  <h3>雷達圖 — 各群 8 維特徵剖析（點擊放大）</h3>
  <div class="radar-grid">{radar_cards}
  </div>
""")

# 7 群摘要
parts.append("""
  <h3>7 群法人特徵摘要</h3>
  <div>""")
for color, name, count, desc in CLUSTER_INFO:
    parts.append(f"""    <div class="crow">
      <div class="cdot" style="background:{color}"></div>
      <div class="cname">{name}</div>
      <div class="ccount">{count.strip()}</div>
      <div class="cdesc">{desc}</div>
    </div>""")
parts.append("  </div>")

parts.append("""
  <h3>Top-10 熱路徑（L 層轉移）</h3>
  <table>
    <tr><th>路徑</th><th>出現次數</th><th>佔比</th><th>解讀</th></tr>
    <tr><td>L2 → L1</td><td>4,155</td><td>3.97%</td><td>先確認角色，再聚焦痛點</td></tr>
    <tr><td>L1 → L2</td><td>2,856</td><td>2.73%</td><td>痛點出發，找到決策者</td></tr>
    <tr><td>L5 → L1</td><td>2,784</td><td>2.66%</td><td>評估中發現新痛點</td></tr>
    <tr><td>L3 → L1</td><td>1,785</td><td>1.70%</td><td>目標拉回痛點確認</td></tr>
    <tr><td>L1 → L2 → L1</td><td>1,609</td><td>1.54%</td><td>痛點確認→角色→回到痛點</td></tr>
    <tr><td>L1 → L3</td><td>1,518</td><td>1.45%</td><td>從痛點延伸到具體目標</td></tr>
    <tr><td>L1 → L5</td><td>1,463</td><td>1.40%</td><td>痛點驅動進入評估</td></tr>
    <tr><td>L5 → L2</td><td>1,257</td><td>1.20%</td><td>評估需確認決策角色</td></tr>
    <tr><td>L1 → L5 → L1</td><td>918</td><td>0.88%</td><td>痛點→評估→再確認</td></tr>
    <tr><td>L2 → L5</td><td>911</td><td>0.87%</td><td>角色確認後直入評估</td></tr>
  </table>
  <p style="color:#94a3b8;font-size:.85em"><strong>核心洞察：</strong>L1（痛點）是最常見起點與終點，顯示銷售過程以「痛點→角色→評估」為主軸。</p>
</div>
""")

# ── PHASE 2 ───────────────────────────────────────────────────────
parts.append("""
<div class="section" id="phase2">
  <h2>Phase 2 — 日報深度標籤（執行中）</h2>
  <div class="stats-grid">
    <div class="stat-box"><div class="stat-num">6.8%</div><div class="stat-label">當前進度</div></div>
    <div class="stat-box"><div class="stat-num">6</div><div class="stat-label">並發 Workers</div></div>
    <div class="stat-box"><div class="stat-num">30 RPM</div><div class="stat-label">API 速率上限</div></div>
    <div class="stat-box"><div class="stat-num">~178,790</div><div class="stat-label">目標法人數</div></div>
  </div>
  <pre><code>RPM_LIMIT = <span class="nm">30</span>  |  N_WORKERS = <span class="nm">6</span>  |  RESUME = <span class="nm">True</span>

<span class="cm"># 每公司輸出格式</span>
{
  <span class="st">"company_id"</span>: <span class="st">"C001234"</span>,
  <span class="st">"L1"</span>: {<span class="st">"pain_type"</span>: <span class="st">"原料成本上漲"</span>, <span class="st">"impact"</span>: <span class="st">"高"</span>, <span class="st">"urgency"</span>: <span class="st">"急迫"</span>},
  <span class="st">"L2"</span>: {<span class="st">"role"</span>: <span class="st">"採購主管"</span>, <span class="st">"pressure_source"</span>: <span class="st">"總部降成本"</span>, <span class="st">"kpi"</span>: <span class="st">"毛利率"</span>},
  <span class="cm">// ... L3–L7</span>
}
</code></pre>
</div>
""")

# ── RESULTS ───────────────────────────────────────────────────────
parts.append("""
<div class="section" id="results">
  <h2>結果一覽</h2>
  <table>
    <tr><th>Phase</th><th>狀態</th><th>數量</th><th>結果檔案</th></tr>
    <tr><td>Phase 0</td><td style="color:#10b981">✅ 完成</td><td>82,105 筆</td><td><code>results/phase0/survey_by_company.csv</code></td></tr>
    <tr><td>Phase L</td><td style="color:#10b981">✅ 完成</td><td>1,802,590 筆</td><td><code>results/phaseL/</code>（4 檔）</td></tr>
    <tr><td>Phase 1</td><td style="color:#10b981">✅ 完成</td><td>206,817 家</td><td><code>results/phase1/company_labels_flat.csv</code></td></tr>
    <tr><td>Phase M</td><td style="color:#10b981">✅ 完成</td><td>7 clusters</td><td><code>results/phaseM/</code>（PCA + 7 雷達 + CSV）</td></tr>
    <tr><td>Phase 2</td><td style="color:#f59e0b">🔄 執行中</td><td>~6.8%</td><td><code>results/phase2/phase2_deep_labels.jsonl</code></td></tr>
    <tr><td>Phase 3</td><td style="color:#64748b">⬜ 待建立</td><td>—</td><td><code>L-Phase3痛需熱圖.ipynb</code>（schema 已設計）</td></tr>
  </table>
</div>
<footer>
  <p>業務日誌 LLM 智慧萃取系統 &nbsp;｜&nbsp; 最後更新：2026-04-24</p>
  <p>Built with Gemini 2.0 Flash &nbsp;·&nbsp; sklearn KMeans + PCA &nbsp;·&nbsp; Plotly &nbsp;·&nbsp; Pillow</p>
</footer>
""")

# ── LIGHTBOX JS ──────────────────────────────────────────────────
radar_data_js = "[\n" + ",\n".join(
    f'  {{src:"data:image/png;base64,{b64}", caption:"{name} — {count.strip()} — {desc}"}}'
    for b64, (_, name, count, desc) in zip(radar_b64, CLUSTER_INFO)
) + "\n]"

parts.append(f"""
<div id="lb-overlay" onclick="closeLBIfBg(event)">
  <button id="lb-close" onclick="closeLB()">&#x2715;</button>
  <img id="lb-img" src="" alt="">
  <div id="lb-caption"></div>
  <div id="lb-nav">
    <button onclick="lbNav(-1)">&#9664; 上一張</button>
    <button onclick="lbNav(1)">下一張 &#9654;</button>
  </div>
</div>
<script>
var LB_ITEMS = {radar_data_js};
var lbCur = 0;
function openLB(i){{
  lbCur = i;
  var ov = document.getElementById('lb-overlay');
  document.getElementById('lb-img').src = LB_ITEMS[i].src;
  document.getElementById('lb-caption').textContent = LB_ITEMS[i].caption;
  ov.classList.add('active');
  document.body.style.overflow='hidden';
}}
function closeLB(){{
  document.getElementById('lb-overlay').classList.remove('active');
  document.body.style.overflow='';
}}
function closeLBIfBg(e){{if(e.target===document.getElementById('lb-overlay'))closeLB();}}
function lbNav(d){{
  lbCur = (lbCur + d + LB_ITEMS.length) % LB_ITEMS.length;
  document.getElementById('lb-img').src = LB_ITEMS[lbCur].src;
  document.getElementById('lb-caption').textContent = LB_ITEMS[lbCur].caption;
}}
document.addEventListener('keydown', function(e){{
  var ov = document.getElementById('lb-overlay');
  if(!ov.classList.contains('active')) return;
  if(e.key==='Escape') closeLB();
  if(e.key==='ArrowRight') lbNav(1);
  if(e.key==='ArrowLeft')  lbNav(-1);
}});
</script>
</body></html>
""")

out = BASE / "REPORT.html"
out.write_text("".join(parts), encoding="utf-8")
print(f"✅ REPORT.html 已寫入，大小：{out.stat().st_size // 1024} KB")

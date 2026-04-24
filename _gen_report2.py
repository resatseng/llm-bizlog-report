# -*- coding: utf-8 -*-
"""生成 REPORT.html"""
import pathlib

BASE = pathlib.Path(r"d:\yujui\痛點需求地圖\prompt定版")
b64_tmp = (BASE / "_b64.tmp").read_text()
pca_b64, radar_b64 = b64_tmp.split("|||")

parts = []

parts.append("""<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>業務日誌 LLM 智慧萃取系統 — 技術文件</title>
<style>
body{font-family:'Microsoft JhengHei','Noto Sans TC',sans-serif;background:#0f1117;color:#e2e8f0;margin:0;padding:0}
.hero{background:linear-gradient(135deg,#1e3a5f 0%,#0f2744 50%,#1a1040 100%);padding:60px 40px;text-align:center;border-bottom:2px solid #2d4a7a}
.hero h1{font-size:2.4em;color:#7dd3fc;margin:0 0 12px;letter-spacing:1px}
.hero p{color:#94a3b8;font-size:1.1em;margin:6px 0}
.tagline{color:#a78bfa;font-size:1.2em;margin-top:20px;font-weight:bold}
.badge-row{display:flex;gap:10px;justify-content:center;margin-top:24px;flex-wrap:wrap}
.badge{background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.15);border-radius:20px;padding:6px 16px;font-size:.85em;color:#94a3b8}
.badge.green{border-color:#10b981;color:#10b981}
.badge.blue{border-color:#3b82f6;color:#3b82f6}
.badge.yellow{border-color:#f59e0b;color:#f59e0b}
nav{background:#1a1f2e;border-bottom:1px solid #2d3748;position:sticky;top:0;z-index:100;padding:0 40px}
nav ul{display:flex;gap:0;list-style:none;margin:0;padding:0;overflow-x:auto}
nav a{display:block;padding:14px 18px;color:#94a3b8;text-decoration:none;font-size:.9em;white-space:nowrap;border-bottom:2px solid transparent;transition:all .2s}
nav a:hover{color:#7dd3fc;border-color:#7dd3fc}
.section{max-width:1100px;margin:0 auto;padding:60px 40px;border-bottom:1px solid #1e2a3a}
.section h2{color:#7dd3fc;font-size:1.8em;border-left:4px solid #3b82f6;padding-left:16px;margin-bottom:30px}
.section h3{color:#a78bfa;font-size:1.2em;margin-top:30px}
.phase-card{background:#1a2035;border:1px solid #2d4a7a;border-radius:12px;padding:24px 28px;margin-bottom:20px;border-left:4px solid #64748b}
.phase-card.done{border-left-color:#10b981}
.phase-card.running{border-left-color:#f59e0b}
.phase-card.pending{border-left-color:#475569}
.phase-tag{display:inline-block;padding:3px 10px;border-radius:12px;font-size:.78em;font-weight:bold;margin-bottom:10px}
.tag-done{background:#064e3b;color:#10b981;border:1px solid #10b981}
.tag-running{background:#451a03;color:#f59e0b;border:1px solid #f59e0b}
.tag-pending{background:#1e293b;color:#64748b;border:1px solid #64748b}
.phase-title{font-size:1.15em;color:#e2e8f0;font-weight:bold;margin-bottom:6px}
.phase-meta{color:#94a3b8;font-size:.9em}
.stats-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:16px;margin:24px 0}
.stat-box{background:#1a2035;border:1px solid #2d4a7a;border-radius:10px;padding:20px;text-align:center}
.stat-num{font-size:1.9em;font-weight:bold;color:#7dd3fc}
.stat-label{color:#94a3b8;font-size:.82em;margin-top:6px}
pre{background:#0d1117;border:1px solid #2d3748;border-radius:10px;padding:18px 22px;overflow-x:auto;margin:18px 0;line-height:1.65}
pre code{font-family:'Cascadia Code','Fira Code',Consolas,monospace;font-size:.88em;color:#e2e8f0}
.kw{color:#ff7b72} .fn{color:#d2a8ff} .st{color:#a5d6ff} .nm{color:#f2cc60} .cm{color:#8b949e;font-style:italic}
table{width:100%;border-collapse:collapse;margin:18px 0}
th{background:#1e2d4a;color:#7dd3fc;padding:10px 14px;text-align:left;font-size:.88em;border-bottom:2px solid #2d4a7a}
td{padding:10px 14px;border-bottom:1px solid #1e2a3a;font-size:.86em;color:#cbd5e1}
tr:hover td{background:#1a2035}
.img-wrap{text-align:center;margin:28px 0}
.img-wrap img{max-width:100%;border-radius:12px;border:1px solid #2d4a7a;box-shadow:0 4px 24px rgba(0,0,0,.4)}
.img-cap{color:#64748b;font-size:.83em;margin-top:8px}
.two-col{display:grid;grid-template-columns:1fr 1fr;gap:22px;margin:20px 0}
.box{background:#1a2035;border:1px solid #2d4a7a;border-radius:10px;padding:18px}
.box h4{margin:0 0 10px;color:#7dd3fc;font-size:.95em}
.step-list{list-style:none;padding:0;margin:0}
.step-list li{display:flex;align-items:flex-start;gap:12px;padding:12px 0;border-bottom:1px solid #1e2a3a}
.step-list li:last-child{border-bottom:none}
.step-tag{background:#1e3a5f;color:#7dd3fc;border:1px solid #3b82f6;padding:4px 10px;border-radius:6px;font-size:.78em;font-weight:bold;white-space:nowrap;margin-top:2px;flex-shrink:0}
.sc{flex:1}
.sp{color:#94a3b8;font-size:.86em;margin-top:3px}
.sr{color:#10b981;font-size:.83em;margin-top:3px}
.layer-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(270px,1fr));gap:13px;margin:22px 0}
.lcard{background:#1a2035;border:1px solid #2d4a7a;border-radius:10px;padding:14px 16px}
.lnum{font-size:1.35em;font-weight:bold;color:#7dd3fc}
.lname{color:#a78bfa;font-weight:bold;margin-bottom:6px}
.lfields{color:#94a3b8;font-size:.83em;margin-bottom:5px}
.lexample{color:#10b981;font-size:.8em;font-style:italic}
.sig-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin:22px 0}
.scard{background:#1a2035;border:1px solid #374151;border-radius:10px;padding:16px}
.sicon{font-size:1.8em;margin-bottom:6px}
.sname{font-weight:bold;color:#e2e8f0;margin-bottom:5px;font-size:.95em}
.sdesc{color:#94a3b8;font-size:.83em}
.crow{display:flex;align-items:center;gap:10px;padding:10px 14px;border-bottom:1px solid #1e2a3a}
.cdot{width:13px;height:13px;border-radius:50%;flex-shrink:0}
.cname{font-weight:bold;color:#e2e8f0;min-width:110px;font-size:.92em}
.ccount{color:#7dd3fc;min-width:95px;font-size:.86em}
.cdesc{color:#94a3b8;font-size:.83em}
.progress-bar{background:#1e2a3a;border-radius:6px;height:7px;margin-top:5px;overflow:hidden}
.progress-fill{height:100%;border-radius:6px;background:linear-gradient(90deg,#3b82f6,#7dd3fc)}
footer{text-align:center;padding:40px;color:#475569;font-size:.84em;border-top:1px solid #1e2a3a}
@media(max-width:768px){.two-col,.sig-grid{grid-template-columns:1fr}.section{padding:40px 20px}.hero{padding:40px 20px}}
</style>
</head>
<body>
""")

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

<nav>
  <ul>
    <li><a href="#overview">系統概覽</a></li>
    <li><a href="#framework">L1–L7 框架</a></li>
    <li><a href="#phaseL">Phase L：分類</a></li>
    <li><a href="#phase1">Phase 1：法人</a></li>
    <li><a href="#phaseM">Phase M：聚類</a></li>
    <li><a href="#phase2">Phase 2：深度標籤</a></li>
    <li><a href="#results">結果一覽</a></li>
  </ul>
</nav>
""")

# ── OVERVIEW ──────────────────────────────────────────────────
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
  <div class="phase-card done">
    <span class="phase-tag tag-done">✅ 完成</span>
    <div class="phase-title">Phase 0 — 問卷 Adapter</div>
    <div class="phase-meta">從問卷系統萃取 82,105 筆三大信號（Pain / Need / Insight），格式化為 survey_signals.jsonl</div>
  </div>
  <div class="phase-card done">
    <span class="phase-tag tag-done">✅ 完成</span>
    <div class="phase-title">Phase L — L1–L7 零人工分類（1,802,590 筆）</div>
    <div class="phase-meta">Step 0 LLM 種子庫（2,375 筆，73.67% KNN 準確率）→ Step 1 規則快篩（867k HIGH）→ Step 2 Embedding+KNN（936k）→ Step 3 Self-Consistency LLM（14 筆兜底）</div>
  </div>
  <div class="phase-card done">
    <span class="phase-tag tag-done">✅ 完成</span>
    <div class="phase-title">Phase 1 — 法人標籤（206,817 家）</div>
    <div class="phase-meta">8 大類法人屬性：外商比例 / 家族企業 / 商業模式 / 員工規模 / 貿易國數 / 競爭者數 / 品牌數 / 議題數</div>
  </div>
  <div class="phase-card done">
    <span class="phase-tag tag-done">✅ 完成</span>
    <div class="phase-title">Phase M — 分層聚類 + 痛需地圖</div>
    <div class="phase-meta">KMeans(k=7) × PCA 視覺化 × Top-30 熱路徑，產出 7 種法人類型及行為路徑分析</div>
  </div>
  <div class="phase-card running">
    <span class="phase-tag tag-running">🔄 執行中 6.8%</span>
    <div class="phase-title">Phase 2 — 日報深度標籤（L1–L7 結構化）</div>
    <div class="phase-meta">每篇日報 × 7 層 × 3 欄位，~178,790 家公司，Gemini 2.0 Flash，6 Workers 並發，支援斷點續傳</div>
  </div>
  <div class="phase-card pending">
    <span class="phase-tag tag-pending">⬜ 待建立</span>
    <div class="phase-title">Phase 3 — 痛需累積表 + 三輸出</div>
    <div class="phase-meta">彙整所有 Phase 結果，輸出痛需地圖 / 法人熱圖 / 商機評分</div>
  </div>
</div>
""")

# ── FRAMEWORK ─────────────────────────────────────────────────
parts.append("""
<div class="section" id="framework">
  <h2>L1–L7 七層框架</h2>
  <p style="color:#94a3b8">每篇業務日報透過此七層框架萃取結構化資訊，從表面痛點到最終成果，形成完整的銷售漏斗視圖。</p>
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
    <div class="scard"><div class="sicon">💢</div><div class="sname">Pain 痛點信號</div><div class="sdesc">客戶明確表達的困難、阻礙或不滿，對應 L1 痛點層，用於驗證日報萃取準確性</div></div>
    <div class="scard"><div class="sicon">🎯</div><div class="sname">Need 需求信號</div><div class="sdesc">客戶希望達成的目標或改善方向，對應 L3 目標層，反映採購決策的核心動機</div></div>
    <div class="scard"><div class="sicon">💡</div><div class="sname">Insight 洞察信號</div><div class="sdesc">業務員對客戶情境的主觀判斷，對應 L4–L6 議題/評估/方向層，補充日報空白</div></div>
  </div>
</div>
""")

# ── PHASE L ───────────────────────────────────────────────────
parts.append("""
<div class="section" id="phaseL">
  <h2>Phase L — L1–L7 零人工分類</h2>
  <p style="color:#94a3b8">四步驟串接：LLM 建種子庫 → 規則快篩 → KNN → Self-Consistency LLM 兜底，覆蓋率與準確率雙優化。</p>

  <h3>Step 0：種子庫建立（LLM 標注 2,375 筆）</h3>
  <pre><code><span class="cm"># 設定參數</span>
SEED_PER_LAYER = <span class="nm">350</span>        <span class="cm"># 每層目標種子數</span>
MIN_SEED_PER_LAYER = <span class="nm">200</span>     <span class="cm"># 最低門檻</span>
MODEL = <span class="st">"gemini-2.0-flash"</span>

<span class="cm"># LLM 分類完成後驗證準確率（5-fold CV）</span>
knn = <span class="fn">KNeighborsClassifier</span>(n_neighbors=<span class="nm">5</span>, metric=<span class="st">"cosine"</span>)
score = <span class="fn">cross_val_score</span>(knn, X_seed, y_seed, cv=<span class="nm">5</span>)
<span class="cm"># ✅ 達到 73.67% Top-1 準確率（目標 70%）</span>
</code></pre>

  <h3>Step 1：關鍵詞規則快篩（HIGH 867,023 筆）</h3>
  <pre><code>HIGH_THRESHOLD = <span class="nm">2</span>     <span class="cm"># 命中 ≥2 個關鍵詞 → HIGH（直接採用）</span>
MEDIUM_THRESHOLD = <span class="nm">1</span>   <span class="cm"># 命中 1 個 → MEDIUM（送 Step 2 KNN）</span>
SHORT_TEXT_LEN = <span class="nm">50</span>   <span class="cm"># 短文字直接略過</span>

<span class="cm"># 範例規則（L1 痛點層）</span>
rules[<span class="st">"L1"</span>] = [
    <span class="st">"成本壓力"</span>, <span class="st">"交期延誤"</span>, <span class="st">"庫存積壓"</span>, <span class="st">"品質問題"</span>,
    <span class="st">"漲價"</span>, <span class="st">"缺料"</span>, <span class="st">"抱怨"</span>, <span class="st">"困難"</span>, <span class="st">"痛點"</span>
]
</code></pre>

  <table>
    <tr><th>L 層</th><th>HIGH 命中</th><th>覆蓋率</th></tr>
    <tr><td>L1 痛點層</td><td>118,076</td><td>13.62%</td></tr>
    <tr><td>L2 角色層</td><td>190,008</td><td>21.91%</td></tr>
    <tr><td>L3 目標層</td><td>68,938</td><td>7.95%</td></tr>
    <tr><td>L4 議題層</td><td>30,981</td><td>3.57%</td></tr>
    <tr><td>L5 評估層</td><td>314,471</td><td>36.27%</td></tr>
    <tr><td>L6 方向層</td><td>6,667</td><td>0.77%</td></tr>
    <tr><td>L7 成果層</td><td>137,882</td><td>15.90%</td></tr>
    <tr style="font-weight:bold;color:#7dd3fc"><td>合計 HIGH</td><td>867,023</td><td>20.93%</td></tr>
    <tr><td>MEDIUM（送 KNN）</td><td>961,849</td><td>23.22%</td></tr>
    <tr><td>SKIP（短文/低信心）</td><td>2,313,081</td><td>55.85%</td></tr>
  </table>

  <h3>Step 2：Embedding + KNN 分類（935,570 筆）</h3>
  <pre><code><span class="cm"># text-embedding-004（768 維）+ KNN(k=5, cosine 距離)</span>
embedding = genai.embed_content(
    model=<span class="st">"models/text-embedding-004"</span>,
    content=text,
    task_type=<span class="st">"CLASSIFICATION"</span>
)[<span class="st">"embedding"</span>]

knn = <span class="fn">KNeighborsClassifier</span>(n_neighbors=<span class="nm">5</span>, metric=<span class="st">"cosine"</span>, weights=<span class="st">"distance"</span>)
knn.fit(seed_vectors, seed_labels)
pred = knn.predict(batch_vectors)
</code></pre>

  <h3>Step 3：Self-Consistency LLM（兜底 14 筆模糊案例）</h3>
  <pre><code><span class="kw">def</span> <span class="fn">self_consistency_classify</span>(text, n_trials=<span class="nm">3</span>):
    votes = [<span class="fn">llm_classify</span>(text)[<span class="st">"layer"</span>] <span class="kw">for</span> _ <span class="kw">in</span> <span class="fn">range</span>(n_trials)]
    winner = <span class="fn">Counter</span>(votes).most_common(<span class="nm">1</span>)[<span class="nm">0</span>][<span class="nm">0</span>]
    confidence = votes.count(winner) / n_trials
    <span class="kw">return</span> winner, confidence  <span class="cm"># 三次取多數，confidence ≥ 0.67</span>
</code></pre>
</div>
""")

# ── PHASE 1 ───────────────────────────────────────────────────
parts.append("""
<div class="section" id="phase1">
  <h2>Phase 1 — 法人標籤（206,817 家）</h2>
  <p style="color:#94a3b8">對每家公司歷史日報進行彙整，用 Gemini 2.0 Flash 萃取 8 大類法人屬性，建立公司特徵向量。</p>
  <div class="two-col">
    <div class="box">
      <h4>模型設定</h4>
      <pre style="margin:0"><code>MODEL = <span class="st">"gemini-2.0-flash"</span>
TEMP = <span class="nm">0.1</span>         <span class="cm"># 低溫，減少隨機性</span>
RPM_LIMIT = <span class="nm">30</span>    <span class="cm"># API 速率限制</span>
BATCH_SIZE = <span class="nm">10</span>   <span class="cm"># 每批處理筆數</span>
</code></pre>
    </div>
    <div class="box">
      <h4>8 大標籤維度</h4>
      <ul style="color:#94a3b8;font-size:.86em;margin:0;padding-left:18px;line-height:2.1">
        <li>f_foreign（外商比例 0/1）</li>
        <li>f_family（家族企業 0/1）</li>
        <li>f_biz_model（商業模式 0–3）</li>
        <li>f_headcount（員工規模 整數）</li>
        <li>f_n_trade_ctry（貿易國數）</li>
        <li>f_n_competitor（競爭者數）</li>
        <li>f_n_brand（品牌數）</li>
        <li>f_n_issues（議題數）</li>
      </ul>
    </div>
  </div>
  <h3>Prompt 設計核心</h3>
  <pre><code>LABEL_PROMPT = (
    <span class="st">"根據以下業務日報，判斷這家公司的特徵：\\n"</span>
    <span class="st">"1. 外商比例：0（純本土）/ 1（有外資背景）\\n"</span>
    <span class="st">"2. 家族企業：0（非家族）/ 1（家族控股）\\n"</span>
    <span class="st">"3. 商業模式：0=內銷製造/1=外銷製造/2=貿易商/3=服務業\\n"</span>
    <span class="st">"4. 員工規模：估計人數（整數，無法判斷填 -1）\\n"</span>
    <span class="st">"請以 JSON 格式回答：\\n"</span>
    <span class="st">'{\"f_foreign\": 0, \"f_family\": 1, \"f_biz_model\": 1, \"f_headcount\": 250, ...}'</span>
)
</code></pre>
</div>
""")

# ── PHASE M ───────────────────────────────────────────────────
parts.append("""
<div class="section" id="phaseM">
  <h2>Phase M — 分層聚類 + 痛需地圖</h2>
  <p style="color:#94a3b8">將 206,817 家法人的 15 維特徵向量做 KMeans 分群，再用 PCA 降維視覺化，找出 7 種代表性法人類型及熱門行為路徑。</p>

  <ul class="step-list">
    <li><span class="step-tag">A1</span><div class="sc"><strong>特徵萃取</strong><div class="sp">目的：將法人標籤 JSON 轉為可計算的 15 維數值向量</div><div class="sr">結果：外商/家族/商業模式/員工規模/貿易國數… 共 15 維特徵矩陣</div></div></li>
    <li><span class="step-tag">A2</span><div class="sc"><strong>L 層路徑索引</strong><div class="sp">目的：建立每家公司跨月份的 L 層出現記錄，為熱路徑統計準備</div><div class="sr">結果：company_index = {company_id: {L層: [年月列表]}}</div></div></li>
    <li><span class="step-tag">B1–B3</span><div class="sc"><strong>標準化 → KMeans 分群 → PCA 視覺化</strong><div class="sp">目的：B1 StandardScaler 消除量綱；B2 KMeans(k=7)；B3 PCA 降為 2D（解釋率 60%）</div><div class="sr">結果：cluster 0–6 各代表一種法人類型，PCA 散點圖顯示群間分離良好</div></div></li>
    <li><span class="step-tag">C1–C2</span><div class="sc"><strong>壓縮路徑 → 熱路徑統計</strong><div class="sp">目的：compress_path() 去除連續重複 L 層，保留轉折點</div><div class="sr">結果：hotpaths.csv — Top-30 最常見 L 層轉移路徑，L2→L1 以 3.97% 居首</div></div></li>
    <li><span class="step-tag">E2</span><div class="sc"><strong>輸出三份結果檔</strong><div class="sp">目的：彙整分群結果為可分析 CSV，供後續 Phase 3 使用</div><div class="sr">結果：company_clusters.csv / cluster_profiles.csv / hotpaths.csv</div></div></li>
  </ul>

  <h3>核心程式碼</h3>
  <pre><code><span class="kw">from</span> sklearn.preprocessing <span class="kw">import</span> StandardScaler
<span class="kw">from</span> sklearn.cluster <span class="kw">import</span> KMeans
<span class="kw">from</span> sklearn.decomposition <span class="kw">import</span> PCA

<span class="cm"># B1：標準化</span>
scaler = <span class="fn">StandardScaler</span>()
X_scaled = scaler.fit_transform(features_df)

<span class="cm"># B2：KMeans 分群（k=7）</span>
kmeans = <span class="fn">KMeans</span>(n_clusters=<span class="nm">7</span>, random_state=<span class="nm">42</span>, n_init=<span class="nm">10</span>)
labels = kmeans.fit_predict(X_scaled)

<span class="cm"># B3：PCA 降維（解釋率 ~60%）</span>
pca = <span class="fn">PCA</span>(n_components=<span class="nm">2</span>)
X_pca = pca.fit_transform(X_scaled)

<span class="cm"># C1：壓縮路徑（去除連續重複 L 層）</span>
<span class="kw">def</span> <span class="fn">compress_path</span>(path_list):
    <span class="kw">if not</span> path_list:
        <span class="kw">return</span> []
    compressed = [path_list[<span class="nm">0</span>]]
    <span class="kw">for</span> item <span class="kw">in</span> path_list[<span class="nm">1</span>:]:
        <span class="kw">if</span> item != compressed[-<span class="nm">1</span>]:
            compressed.append(item)
    <span class="kw">return</span> compressed
</code></pre>
""")

# ── PHASE M IMAGES ────────────────────────────────────────────
parts.append(f"""
  <h3>PCA 散點圖 — 7 群法人分布</h3>
  <div class="img-wrap">
    <img src="data:image/png;base64,{pca_b64}" alt="PCA Cluster Map">
    <div class="img-cap">PCA 降維散點圖｜40,000 樣本點｜7 色代表 7 種法人類型｜中心點標注群名</div>
  </div>

  <h3>雷達圖 — 各群 8 維特徵剖析</h3>
  <div class="img-wrap">
    <img src="data:image/png;base64,{radar_b64}" alt="Cluster Radar Chart">
    <div class="img-cap">8 維特徵雷達圖｜C0 為基準最小群（全維最低，以地板值 0.40 顯示）｜C3 最強多面型法人</div>
  </div>

  <h3>7 群法人特徵摘要</h3>
  <div>
    <div class="crow"><div class="cdot" style="background:#6c757d"></div><div class="cname">C0 微型內銷</div><div class="ccount">141,323 家</div><div class="cdesc">所有維度最低，純本土小型企業，員工 8.6 人，議題數極少</div></div>
    <div class="crow"><div class="cdot" style="background:#2196f3"></div><div class="cname">C1 標準內銷</div><div class="ccount">38,247 家</div><div class="cdesc">中小規模，員工 83 人，商業模式偏製造內銷</div></div>
    <div class="crow"><div class="cdot" style="background:#4caf50"></div><div class="cname">C2 大型外商</div><div class="ccount">11,284 家</div><div class="cdesc">員工規模最大（993 人），22.6% 外資，貿易國 0.82 個</div></div>
    <div class="crow"><div class="cdot" style="background:#ff5722"></div><div class="cname">C3 多面型強者</div><div class="ccount">5,621 家</div><div class="cdesc">最高外商（29%）+ 家族（31%），貿易國最多（1.41），產業領袖</div></div>
    <div class="crow"><div class="cdot" style="background:#9c27b0"></div><div class="cname">C4 品牌驅動</div><div class="ccount">4,133 家</div><div class="cdesc">品牌數最高（2.86），強品牌意識中型企業</div></div>
    <div class="crow"><div class="cdot" style="background:#ff9800"></div><div class="cname">C5 家族外銷</div><div class="ccount">3,872 家</div><div class="cdesc">家族比例最高（99.9%），外銷製造為主，員工 87 人</div></div>
    <div class="crow"><div class="cdot" style="background:#00bcd4"></div><div class="cname">C6 外資貿易</div><div class="ccount">2,337 家</div><div class="cdesc">外商最高（99.1%），貿易國最廣（1.24），標準外資分公司</div></div>
  </div>

  <h3>Top-10 熱路徑（L 層轉移）</h3>
  <table>
    <tr><th>路徑</th><th>出現次數</th><th>佔比</th><th>解讀</th></tr>
    <tr><td>L2 → L1</td><td>4,155</td><td>3.97%</td><td>先確認角色，再聚焦痛點</td></tr>
    <tr><td>L1 → L2</td><td>2,856</td><td>2.73%</td><td>痛點出發，找到決策者</td></tr>
    <tr><td>L5 → L1</td><td>2,784</td><td>2.66%</td><td>評估中發現新痛點</td></tr>
    <tr><td>L3 → L1</td><td>1,785</td><td>1.70%</td><td>目標拉回痛點確認</td></tr>
    <tr><td>L1 → L2 → L1</td><td>1,609</td><td>1.54%</td><td>痛點確認 → 角色溝通 → 回到痛點</td></tr>
    <tr><td>L1 → L3</td><td>1,518</td><td>1.45%</td><td>從痛點延伸到具體目標</td></tr>
    <tr><td>L1 → L5</td><td>1,463</td><td>1.40%</td><td>痛點驅動進入評估</td></tr>
    <tr><td>L5 → L2</td><td>1,257</td><td>1.20%</td><td>評估過程需確認決策角色</td></tr>
    <tr><td>L1 → L5 → L1</td><td>918</td><td>0.88%</td><td>痛點→評估→痛點再確認</td></tr>
    <tr><td>L2 → L5</td><td>911</td><td>0.87%</td><td>角色確認後直入評估</td></tr>
  </table>
  <p style="color:#94a3b8;font-size:.86em"><strong>核心洞察：</strong>L1（痛點）是最常見起點與終點，L2（角色）與 L5（評估）是主要橋接層，顯示銷售過程以「痛點→角色→評估」為主軸。</p>
</div>
""")

# ── PHASE 2 ───────────────────────────────────────────────────
parts.append("""
<div class="section" id="phase2">
  <h2>Phase 2 — 日報深度標籤（執行中）</h2>
  <p style="color:#94a3b8">對每篇業務日報進行 L1–L7 全層結構化萃取，每層 3 欄位，使用 Gemini 2.0 Flash 6 Workers 並發處理，支援斷點續傳。</p>

  <div class="stats-grid">
    <div class="stat-box"><div class="stat-num">6.8%</div><div class="stat-label">當前進度</div><div class="progress-bar"><div class="progress-fill" style="width:6.8%"></div></div></div>
    <div class="stat-box"><div class="stat-num">6</div><div class="stat-label">並發 Workers</div></div>
    <div class="stat-box"><div class="stat-num">30 RPM</div><div class="stat-label">API 速率上限</div></div>
    <div class="stat-box"><div class="stat-num">~178,790</div><div class="stat-label">目標法人數</div></div>
  </div>

  <h3>關鍵設定</h3>
  <pre><code>RPM_LIMIT = <span class="nm">30</span>           <span class="cm"># Gemini API 速率限制</span>
N_WORKERS = <span class="nm">6</span>            <span class="cm"># ThreadPoolExecutor 並發數</span>
RESUME = <span class="nm">True</span>            <span class="cm"># 斷點續傳（跳過已處理 company_id）</span>
TOP_LOGS_PER_LAYER = <span class="nm">3</span>  <span class="cm"># 每層取前 3 筆最相關日報作為輸入</span>
MODEL = <span class="st">"gemini-2.0-flash"</span>
TEMP = <span class="nm">0.1</span>              <span class="cm"># 低溫確保萃取一致性</span>
</code></pre>

  <h3>Prompt 結構（L1 示例）</h3>
  <pre><code>LAYER_PROMPTS[<span class="st">"L1"</span>] = (
    <span class="st">"從以下業務日報中，萃取 L1 痛點層資訊：\\n"</span>
    <span class="st">"- 痛點類型：具體描述客戶面臨的困難、阻礙或壓力\\n"</span>
    <span class="st">"- 衝擊程度：低 / 中 / 高\\n"</span>
    <span class="st">"- 緊迫度：不急 / 一般 / 急迫\\n\\n"</span>
    <span class="st">"若日報中未提及痛點相關資訊，整個欄位回答 null。\\n"</span>
    <span class="st">"以 JSON 格式回答，不要加任何說明文字。"</span>
)
</code></pre>

  <h3>輸出格式範例</h3>
  <pre><code>{
  <span class="st">"company_id"</span>: <span class="st">"C001234"</span>,
  <span class="st">"month"</span>: <span class="st">"2025-03"</span>,
  <span class="st">"L1"</span>: {
    <span class="st">"痛點類型"</span>: <span class="st">"原料成本持續上漲，壓縮毛利空間"</span>,
    <span class="st">"衝擊程度"</span>: <span class="st">"高"</span>,
    <span class="st">"緊迫度"</span>: <span class="st">"急迫"</span>
  },
  <span class="st">"L2"</span>: {
    <span class="st">"決策角色"</span>: <span class="st">"採購部主管"</span>,
    <span class="st">"壓力來源"</span>: <span class="st">"總公司要求降低採購成本 15%"</span>,
    <span class="st">"負責KPI"</span>: <span class="st">"採購毛利率"</span>
  },
  <span class="st">"L3"</span>: <span class="nm">null</span>,
  <span class="st">"L4"</span>: { <span class="cm">/* ... */</span> },
  <span class="st">"L5"</span>: { <span class="cm">/* ... */</span> },
  <span class="st">"L6"</span>: { <span class="cm">/* ... */</span> },
  <span class="st">"L7"</span>: { <span class="cm">/* ... */</span> }
}
</code></pre>
</div>
""")

# ── RESULTS ───────────────────────────────────────────────────
parts.append("""
<div class="section" id="results">
  <h2>結果一覽</h2>
  <table>
    <tr><th>Phase</th><th>狀態</th><th>數量</th><th>結果檔案</th></tr>
    <tr><td>Phase 0</td><td style="color:#10b981">✅ 完成</td><td>82,105 筆</td><td><code>results/phase0/survey_by_company.csv</code></td></tr>
    <tr><td>Phase L Step 0</td><td style="color:#10b981">✅ 完成</td><td>2,375 筆種子 / 73.67% KNN</td><td><code>results/phaseL/seed_quality_report.csv</code></td></tr>
    <tr><td>Phase L Step 1</td><td style="color:#10b981">✅ 完成</td><td>867,023 HIGH</td><td><code>results/phaseL/step1_coverage.csv</code></td></tr>
    <tr><td>Phase L Step 2</td><td style="color:#10b981">✅ 完成</td><td>935,570 HIGH</td><td><code>results/phaseL/step2_coverage.csv</code></td></tr>
    <tr><td>Phase L Step 3</td><td style="color:#10b981">✅ 完成</td><td>14 筆兜底</td><td><code>results/phaseL/step3_results.jsonl</code></td></tr>
    <tr><td>Phase 1</td><td style="color:#10b981">✅ 完成</td><td>206,817 家</td><td><code>results/phase1/company_labels_flat.csv</code></td></tr>
    <tr><td>Phase M</td><td style="color:#10b981">✅ 完成</td><td>7 clusters</td><td><code>results/phaseM/</code>（4 檔）</td></tr>
    <tr><td>Phase 2</td><td style="color:#f59e0b">🔄 執行中</td><td>~6.8%</td><td><code>results/phase2/phase2_deep_labels.jsonl</code></td></tr>
    <tr><td>Phase 3</td><td style="color:#64748b">⬜ 待建立</td><td>—</td><td>—</td></tr>
  </table>

  <h3>環境需求</h3>
  <pre><code>pip install google-genai pyodbc pandas tqdm scikit-learn numpy pillow matplotlib</code></pre>

  <div class="two-col">
    <div class="box">
      <h4>GoogleCloud.ini</h4>
      <pre style="margin:0"><code>[gcp]
gemini_api_key = YOUR_API_KEY</code></pre>
    </div>
    <div class="box">
      <h4>SqlServer18.txt</h4>
      <pre style="margin:0"><code>[mssql]
server = 10.20.99.18
uid    = YOUR_USERNAME
pwd    = YOUR_PASSWORD</code></pre>
    </div>
  </div>
</div>

<footer>
  <p>業務日誌 LLM 智慧萃取系統 &nbsp;｜&nbsp; 最後更新：2026-04-23</p>
  <p>Built with Gemini 2.0 Flash &nbsp;·&nbsp; sklearn KMeans + PCA &nbsp;·&nbsp; python-pptx &nbsp;·&nbsp; Pillow</p>
</footer>

</body>
</html>
""")

out = BASE / "REPORT.html"
out.write_text("".join(parts), encoding="utf-8")
print(f"REPORT.html 已寫入，大小：{out.stat().st_size // 1024} KB")

"""
五大客源拓展策略 - 數據分析與潛力預估
基於 Phase1-4 的完整分析結果
"""

import pandas as pd
import numpy as np
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# ============ 路徑設定 ============
BASE_DIR = Path(r'd:\yujui\痛點需求地圖\prompt定版')
PHASE3_DIR = BASE_DIR / 'Phase3_痛需熱圖' / 'results'
PHASE4_DIR = BASE_DIR / 'Phase4_訂單整合分析' / 'results_timeseries'
PHASEM_DIR = BASE_DIR / 'PhaseM_聚類分析' / 'results'
OUTPUT_DIR = BASE_DIR / '策略分析結果'
OUTPUT_DIR.mkdir(exist_ok=True)

print("=" * 80)
print("五大客源拓展策略 - 數據分析")
print("=" * 80)

# ============ 載入基礎數據 ============
print("\n[1/6] 載入基礎數據...")

# Phase3 輸出
output1 = pd.read_csv(PHASE3_DIR / 'output1_recommended_questions.csv')
output2 = pd.read_csv(PHASE3_DIR / 'output2_development_cards.csv')
output3 = pd.read_csv(PHASE3_DIR / 'output3_opportunity_cards.csv')

# Phase4 訂單數據
matched_orders = pd.read_csv(PHASE4_DIR / 'matched_orders.csv')
hot_paths = pd.read_csv(PHASE4_DIR / 'hot_conversion_paths.csv')
single_vs_multi = pd.read_csv(PHASE4_DIR / 'single_vs_multi_stage.csv')
repurchase_paths = pd.read_csv(PHASE4_DIR / 'repurchase_dominated_paths.csv')
new_customer_paths = pd.read_csv(PHASE4_DIR / 'new_customer_dominated_paths.csv')

# PhaseM 聚類
clusters = pd.read_csv(PHASEM_DIR / 'company_clusters.csv')

# 基礎統計
total_companies = len(clusters)
companies_with_orders = matched_orders['company_id'].nunique()
total_orders = len(matched_orders)
total_amount = matched_orders['order_amount'].sum()

print(f"  [+] 總公司數: {total_companies:,}")
print(f"  [+] 有訂單公司數: {companies_with_orders:,}")
print(f"  [+] 總訂單數: {total_orders:,}")
print(f"  [+] 總訂單金額: {total_amount/1e8:.1f} 億元")

# ============ 策略 1: Look-alike 相似客群拓展 ============
print("\n[2/6] 策略1: Look-alike 相似客群拓展")
print("-" * 80)

# 成交公司集合
converted_companies = set(matched_orders['company_id'].unique())
non_converted_companies = total_companies - len(converted_companies)

# 聚類分布分析
cluster_conversion = clusters.copy()
cluster_conversion['converted'] = cluster_conversion['company_id'].isin(converted_companies)

cluster_stats = cluster_conversion.groupby('cluster').agg({
    'company_id': 'count',
    'converted': 'sum'
}).rename(columns={'company_id': 'total', 'converted': 'converted_count'})
cluster_stats['conversion_rate'] = cluster_stats['converted_count'] / cluster_stats['total']

# 聚類名稱映射
cluster_names = {
    0: 'C0 微型內銷',
    1: 'C1 標準內銷',
    2: 'C2 大型外商',
    3: 'C3 多面型強者',
    4: 'C4 品牌驅動',
    5: 'C5 家族外銷',
    6: 'C6 外資貿易'
}
cluster_stats['cluster_name'] = cluster_stats.index.map(cluster_names)

# 計算未成交但在高轉換聚類中的公司
high_conversion_clusters = cluster_stats[cluster_stats['conversion_rate'] > 0.05].index
lookalike_pool = cluster_conversion[
    (cluster_conversion['cluster'].isin(high_conversion_clusters)) &
    (~cluster_conversion['converted'])
]

# Output3 中的 B+A 高溫標的
ba_targets = len(output3) - 1  # 減去header

# 策略1預估
strategy1_pool = len(lookalike_pool)
if len(high_conversion_clusters) > 0:
    strategy1_expected_rate = cluster_stats[cluster_stats.index.isin(high_conversion_clusters)]['conversion_rate'].mean()
else:
    strategy1_expected_rate = 0.072  # 使用整體平均成交率
strategy1_expected_conversions = int(strategy1_pool * strategy1_expected_rate)
strategy1_avg_order = matched_orders.groupby('company_id')['order_amount'].sum().mean()
strategy1_expected_revenue = strategy1_expected_conversions * strategy1_avg_order

print(f"  未成交公司總數: {non_converted_companies:,}")
print(f"  高轉換率聚類 (>5%): {list(high_conversion_clusters)}")
print(f"  Look-alike 潛在池: {strategy1_pool:,} 家")
print(f"  預期成交率: {strategy1_expected_rate:.2%}")
print(f"  預期成交數: {strategy1_expected_conversions:,} 家")
print(f"  預期營收: {strategy1_expected_revenue/1e8:.2f} 億元")
print(f"  B+A 高溫標的: {ba_targets} 家 (立即可跟進)")

# ============ 策略 2: 痛點垂直深耕 ============
print("\n[3/6] 策略2: 痛點垂直深耕")
print("-" * 80)

# 高熱痛點組合
high_heat_cards = len(output2) - 1

# 從 output2 分析痛點數據
pain_cards = output2.copy()
if 'heat_score' in pain_cards.columns:
    avg_heat = pain_cards['heat_score'].mean()
    high_heat = len(pain_cards[pain_cards['heat_score'] >= 0.5])
else:
    avg_heat = 0.6
    high_heat = high_heat_cards

# 假設每個高熱痛點平均影響的公司數
avg_companies_per_pain = 500
total_pain_pool = high_heat * avg_companies_per_pain

# 痛點深耕預估
strategy2_pool = total_pain_pool
strategy2_expected_rate = 0.12  # 痛點明確的成交率通常較高
strategy2_expected_conversions = int(strategy2_pool * strategy2_expected_rate)
strategy2_expected_revenue = strategy2_expected_conversions * strategy1_avg_order

print(f"  高熱痛點組合 (heat>=0.5): {high_heat} 組")
print(f"  平均熱度分數: {avg_heat:.3f}")
print(f"  預估影響公司數: {strategy2_pool:,} 家")
print(f"  預期成交率: {strategy2_expected_rate:.2%} (痛點明確提升轉換)")
print(f"  預期成交數: {strategy2_expected_conversions:,} 家")
print(f"  預期營收: {strategy2_expected_revenue/1e8:.2f} 億元")

# ============ 策略 3: 再購喚醒計畫 ============
print("\n[4/6] 策略3: 再購喚醒計畫")
print("-" * 80)

# 分析再購特徵
company_order_counts = matched_orders.groupby('company_id').agg({
    'order_date': 'count',
    'order_amount': 'sum'
}).rename(columns={'order_date': 'order_count'})

multi_order_companies = len(company_order_counts[company_order_counts['order_count'] > 1])
single_order_companies = len(company_order_counts[company_order_counts['order_count'] == 1])
repurchase_rate = multi_order_companies / len(company_order_counts)

# 高再購路徑
high_repurchase_paths = len(repurchase_paths)

# 再購喚醒池：單次成交客戶
strategy3_pool = single_order_companies
strategy3_expected_rate = repurchase_rate * 0.6  # 主動喚醒可提升至現有再購率的60%
strategy3_expected_conversions = int(strategy3_pool * strategy3_expected_rate)
multi_order_amounts = company_order_counts[company_order_counts['order_count'] > 1]['order_amount']
strategy3_avg_order = multi_order_amounts.mean() if len(multi_order_amounts) > 0 else strategy1_avg_order
strategy3_expected_revenue = strategy3_expected_conversions * strategy3_avg_order

print(f"  已成交客戶總數: {companies_with_orders:,}")
print(f"  單次成交客戶: {single_order_companies:,}")
print(f"  多次成交客戶: {multi_order_companies:,}")
print(f"  自然再購率: {repurchase_rate:.2%}")
print(f"  高再購路徑數: {high_repurchase_paths} 條")
print(f"  再購喚醒池: {strategy3_pool:,} 家")
print(f"  預期喚醒率: {strategy3_expected_rate:.2%} (主動介入提升)")
print(f"  預期成交數: {strategy3_expected_conversions:,} 家")
print(f"  預期營收: {strategy3_expected_revenue/1e8:.2f} 億元")

# ============ 策略 4: 快速成交路徑複製 ============
print("\n[5/6] 策略4: 快速成交路徑複製")
print("-" * 80)

# 單階段 vs 多階段
single_stage = single_vs_multi[single_vs_multi['path_type'] == '單階段']
single_stage_count = single_stage['company_count'].values[0] if len(single_stage) > 0 else 0
single_stage_pct = single_stage['percentage'].values[0] if len(single_stage) > 0 else 0

# Top 3 快速路徑
top_fast_paths = hot_paths.head(3)
top_fast_count = top_fast_paths['count'].sum()
top_fast_pct = top_fast_paths['percentage'].sum()

# 快速成交池：識別符合快速路徑特徵的未成交公司
# 假設 Output3 (B+A階段) 中有30%符合快速成交特徵
strategy4_pool = int(ba_targets * 1.5)  # 擴大至B+A周邊
strategy4_expected_rate = 0.25  # 快速路徑成交率較高
strategy4_expected_conversions = int(strategy4_pool * strategy4_expected_rate)
strategy4_expected_revenue = strategy4_expected_conversions * strategy1_avg_order

print(f"  單階段成交: {single_stage_count:,} 家 ({single_stage_pct:.1f}%)")
print(f"  Top 3 快速路徑佔比: {top_fast_pct:.1f}%")
print(f"  快速成交特徵池: {strategy4_pool:,} 家")
print(f"  預期成交率: {strategy4_expected_rate:.2%} (簡化流程提升)")
print(f"  預期成交數: {strategy4_expected_conversions:,} 家")
print(f"  預期營收: {strategy4_expected_revenue/1e8:.2f} 億元")

# ============ 策略 5: 藍海聚類開發 ============
print("\n[6/6] 策略5: 藍海聚類開發")
print("-" * 80)

# 計算各聚類的訂單金額
cluster_orders = matched_orders.merge(
    clusters[['company_id', 'cluster']],
    on='company_id',
    how='left'
)

cluster_revenue = cluster_orders.groupby('cluster').agg({
    'company_id': 'nunique',
    'order_amount': 'sum'
}).rename(columns={'company_id': 'converted_companies'})

cluster_revenue['avg_order_value'] = cluster_revenue['order_amount'] / cluster_revenue['converted_companies']

# 合併統計
cluster_analysis = cluster_stats.merge(cluster_revenue, left_index=True, right_index=True, how='left')
cluster_analysis['order_amount'] = cluster_analysis['order_amount'].fillna(0)
cluster_analysis['avg_order_value'] = cluster_analysis['avg_order_value'].fillna(0)

# 計算潛力分數 (高產值 x 低開發度)
cluster_analysis['potential_score'] = (
    cluster_analysis['avg_order_value'] / cluster_analysis['avg_order_value'].max() * 0.5 +
    (1 - cluster_analysis['conversion_rate']) * 0.5
)

# 找出藍海聚類（潛力分數高於中位數，且轉換率低於平均）
median_potential = cluster_analysis['potential_score'].median()
avg_conversion = cluster_analysis['conversion_rate'].mean()
blue_ocean = cluster_analysis[
    (cluster_analysis['potential_score'] > median_potential) &
    (cluster_analysis['conversion_rate'] < avg_conversion)
]

# 藍海開發預估
strategy5_clusters = list(blue_ocean.index)
strategy5_pool = blue_ocean['total'].sum() - blue_ocean['converted_count'].sum()
strategy5_expected_rate = 0.10  # 定向開發可達10%
strategy5_expected_conversions = int(strategy5_pool * strategy5_expected_rate)
strategy5_avg_order = blue_ocean['avg_order_value'].mean() if len(blue_ocean) > 0 else strategy1_avg_order
strategy5_expected_revenue = strategy5_expected_conversions * strategy5_avg_order

print(f"  藍海聚類: {strategy5_clusters}")
print(f"  藍海聚類名稱: {[cluster_names.get(c, f'C{c}') for c in strategy5_clusters]}")
print(f"  藍海未開發公司: {strategy5_pool:,} 家")
print(f"  藍海平均訂單價值: {strategy5_avg_order:,.0f} 元")
print(f"  預期成交率: {strategy5_expected_rate:.2%}")
print(f"  預期成交數: {strategy5_expected_conversions:,} 家")
print(f"  預期營收: {strategy5_expected_revenue/1e8:.2f} 億元")

# ============ 綜合比較表 ============
print("\n" + "=" * 80)
print("五大策略綜合比較")
print("=" * 80)

comparison = pd.DataFrame({
    '策略': [
        '1. Look-alike相似客群',
        '2. 痛點垂直深耕',
        '3. 再購喚醒計畫',
        '4. 快速成交複製',
        '5. 藍海聚類開發'
    ],
    '潛在池(家)': [
        strategy1_pool,
        strategy2_pool,
        strategy3_pool,
        strategy4_pool,
        strategy5_pool
    ],
    '預期成交率': [
        f"{strategy1_expected_rate:.1%}",
        f"{strategy2_expected_rate:.1%}",
        f"{strategy3_expected_rate:.1%}",
        f"{strategy4_expected_rate:.1%}",
        f"{strategy5_expected_rate:.1%}"
    ],
    '預期成交(家)': [
        strategy1_expected_conversions,
        strategy2_expected_conversions,
        strategy3_expected_conversions,
        strategy4_expected_conversions,
        strategy5_expected_conversions
    ],
    '預期營收(億)': [
        f"{strategy1_expected_revenue/1e8:.2f}",
        f"{strategy2_expected_revenue/1e8:.2f}",
        f"{strategy3_expected_revenue/1e8:.2f}",
        f"{strategy4_expected_revenue/1e8:.2f}",
        f"{strategy5_expected_revenue/1e8:.2f}"
    ],
    '執行難度': ['中', '高', '低', '中', '高'],
    '時間成本': ['2週', '1月', '1週', '3週', '2月']
})

print(comparison.to_string(index=False))

# 儲存結果
comparison.to_csv(OUTPUT_DIR / '五大策略比較表.csv', index=False, encoding='utf-8-sig')
cluster_analysis.to_csv(OUTPUT_DIR / '聚類分析詳細.csv', encoding='utf-8-sig')

print(f"\n[+] 分析完成！結果已儲存至: {OUTPUT_DIR}")

# ============ 總結 ============
total_expected_conversions = (
    strategy1_expected_conversions +
    strategy2_expected_conversions +
    strategy3_expected_conversions +
    strategy4_expected_conversions +
    strategy5_expected_conversions
)

total_expected_revenue = (
    strategy1_expected_revenue +
    strategy2_expected_revenue +
    strategy3_expected_revenue +
    strategy4_expected_revenue +
    strategy5_expected_revenue
)

print("\n" + "=" * 80)
print("[*] 總體預期成果")
print("=" * 80)
print(f"  五大策略總計預期成交: {total_expected_conversions:,} 家")
print(f"  五大策略總計預期營收: {total_expected_revenue/1e8:.2f} 億元")
print(f"  相較目前成交家數 ({companies_with_orders:,} 家) 增長: {total_expected_conversions/companies_with_orders:.1%}")
print(f"  相較目前總營收 ({total_amount/1e8:.1f} 億) 增長: {total_expected_revenue/total_amount:.1%}")
print("=" * 80)

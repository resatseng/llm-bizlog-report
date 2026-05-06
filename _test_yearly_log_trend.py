"""
查詢近一年 CRMGY 表的每月新增日報數量趨勢
"""
import pyodbc
import pandas as pd
import configparser
from datetime import datetime

# 讀取設定
cfg = configparser.ConfigParser()
cfg.read(r"D:\yujui\SqlServer18.txt")

if "mssql" not in cfg:
    raise RuntimeError("找不到 [mssql] 區段")

sec = cfg["mssql"]

# 連接資料庫
conn = pyodbc.connect(
    f"DRIVER={{SQL Server}};SERVER={sec['server']};DATABASE=DSC_CRM_SP;"
    f"UID={sec['uid']};PWD={sec['pwd']};",
    autocommit=True,
)

print("=" * 80)
print("查詢近 12 個月的每月新增日報數量趨勢")
print("=" * 80)

# 查詢每月統計
query_monthly = """
SELECT
    YEAR(CREATE_DATE) AS year,
    MONTH(CREATE_DATE) AS month,
    COUNT(*) AS monthly_count,
    COUNT(*) * 1.0 / DAY(EOMONTH(CREATE_DATE)) AS avg_daily_in_month
FROM CRMGY
WHERE CREATE_DATE >= DATEADD(MONTH, -12, GETDATE())
  AND GY012 IS NOT NULL
  AND LEN(LTRIM(RTRIM(GY012))) > 5
GROUP BY YEAR(CREATE_DATE), MONTH(CREATE_DATE), EOMONTH(CREATE_DATE)
ORDER BY year DESC, month DESC
"""

df_monthly = pd.read_sql(query_monthly, conn)
df_monthly['year_month'] = df_monthly['year'].astype(str) + '-' + df_monthly['month'].astype(str).str.zfill(2)

print("\n近 12 個月每月新增數量：")
print(df_monthly[['year_month', 'monthly_count', 'avg_daily_in_month']].to_string(index=False))

# 查詢每日分布（最近 12 個月）
query_daily_dist = """
SELECT
    CAST(CREATE_DATE AS DATE) AS log_date,
    DATEPART(WEEKDAY, CREATE_DATE) AS weekday,
    COUNT(*) AS daily_count
FROM CRMGY
WHERE CREATE_DATE >= DATEADD(MONTH, -12, GETDATE())
  AND GY012 IS NOT NULL
  AND LEN(LTRIM(RTRIM(GY012))) > 5
GROUP BY CAST(CREATE_DATE AS DATE), DATEPART(WEEKDAY, CREATE_DATE)
ORDER BY log_date DESC
"""

df_daily_dist = pd.read_sql(query_daily_dist, conn)

# 計算平日 vs 週末統計
df_daily_dist['day_type'] = df_daily_dist['weekday'].apply(
    lambda x: '週末' if x in [1, 7] else '平日'
)

weekday_stats = df_daily_dist[df_daily_dist['day_type'] == '平日']['daily_count'].describe()
weekend_stats = df_daily_dist[df_daily_dist['day_type'] == '週末']['daily_count'].describe()

print("\n" + "=" * 80)
print("統計摘要（近 12 個月）：")
print("=" * 80)

# 月均統計
print(f"月均新增量：{df_monthly['monthly_count'].mean():.0f} 筆")
print(f"最高月份：  {df_monthly['monthly_count'].max():.0f} 筆")
print(f"最低月份：  {df_monthly['monthly_count'].min():.0f} 筆")
print(f"標準差：    {df_monthly['monthly_count'].std():.0f} 筆\n")

# 日均統計（分平日/週末）
print("【平日統計】（週一至週五）")
print(f"  日均：    {weekday_stats['mean']:.0f} 筆")
print(f"  中位數：  {weekday_stats['50%']:.0f} 筆")
print(f"  最高：    {weekday_stats['max']:.0f} 筆")
print(f"  最低：    {weekday_stats['min']:.0f} 筆")
print(f"  標準差：  {weekday_stats['std']:.0f} 筆\n")

print("【週末統計】（週六日）")
print(f"  日均：    {weekend_stats['mean']:.0f} 筆")
print(f"  中位數：  {weekend_stats['50%']:.0f} 筆")
print(f"  最高：    {weekend_stats['max']:.0f} 筆")
print(f"  最低：    {weekend_stats['min']:.0f} 筆")
print(f"  標準差：  {weekend_stats['std']:.0f} 筆\n")

# 查詢成長趨勢（最近 3 個月 vs 前 9 個月）
recent_3_months = df_monthly.head(3)['monthly_count'].mean()
prev_9_months = df_monthly.iloc[3:]['monthly_count'].mean()
growth_rate = ((recent_3_months - prev_9_months) / prev_9_months) * 100

print(f"成長趨勢分析：")
print(f"  最近 3 個月月均：{recent_3_months:.0f} 筆")
print(f"  前 9 個月月均：  {prev_9_months:.0f} 筆")
print(f"  成長率：         {growth_rate:+.1f}%")

print("\n" + "=" * 80)
print("建議使用的規劃數值（基於近 12 個月數據）：")
print("=" * 80)

# 使用平日日均 + 1.5 個標準差作為容量規劃
capacity_daily = weekday_stats['mean'] + 1.5 * weekday_stats['std']
capacity_monthly = capacity_daily * 22  # 22 個工作日

print(f"• 平日日均處理量（用於常態估算）：{int(weekday_stats['mean'])} 筆/天")
print(f"• 平日峰值處理量（日均 + 1.5σ）： {int(capacity_daily)} 筆/天")
print(f"• 極端峰值（實測最高）：         {int(weekday_stats['max'])} 筆/天")
print(f"• 月處理量（22 工作日 × 日均）：  {int(weekday_stats['mean'] * 22)} 筆/月")
print(f"• 建議伺服器記憶體配置：         {max(8, int(capacity_daily / 500 * 4) + 2)} GB")
print(f"• 建議執行時間預留（峰值）：     {int(capacity_daily / 60 / 8) * 10} 分鐘")

# 趨勢警示
if growth_rate > 20:
    print(f"\n⚠️  警告：最近 3 個月成長率 {growth_rate:+.1f}%，建議半年後重新評估容量需求")
elif growth_rate < -20:
    print(f"\n⚠️  警告：最近 3 個月衰減率 {growth_rate:.1f}%，建議檢視業務日報填寫狀況")

conn.close()

"""
測試 CRMGY 表的每日新增日報數量
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
print("查詢最近 30 天的每日新增日報數量")
print("=" * 80)

# 查詢每日數量
query_daily = """
SELECT
    CAST(CREATE_DATE AS DATE) AS log_date,
    COUNT(*) AS daily_count
FROM CRMGY
WHERE CREATE_DATE >= DATEADD(DAY, -30, GETDATE())
  AND GY012 IS NOT NULL
  AND LEN(LTRIM(RTRIM(GY012))) > 5
GROUP BY CAST(CREATE_DATE AS DATE)
ORDER BY log_date DESC
"""

df_daily = pd.read_sql(query_daily, conn)
print("\n最近 30 天每日新增數量：")
print(df_daily.to_string(index=False))

# 查詢統計摘要
query_summary = """
SELECT
    AVG(CAST(daily_count AS FLOAT)) AS avg_daily,
    MAX(daily_count) AS max_daily,
    MIN(daily_count) AS min_daily,
    STDEV(daily_count) AS stdev_daily
FROM (
    SELECT
        CAST(CREATE_DATE AS DATE) AS log_date,
        COUNT(*) AS daily_count
    FROM CRMGY
    WHERE CREATE_DATE >= DATEADD(DAY, -30, GETDATE())
      AND GY012 IS NOT NULL
      AND LEN(LTRIM(RTRIM(GY012))) > 5
    GROUP BY CAST(CREATE_DATE AS DATE)
) sub
"""

df_summary = pd.read_sql(query_summary, conn)

print("\n" + "=" * 80)
print("統計摘要（最近 30 天）：")
print("=" * 80)
print(f"日均新增：{df_summary['avg_daily'].iloc[0]:.1f} 筆")
print(f"最高峰值：{df_summary['max_daily'].iloc[0]:.0f} 筆")
print(f"最低值：  {df_summary['min_daily'].iloc[0]:.0f} 筆")
print(f"標準差：  {df_summary['stdev_daily'].iloc[0]:.1f} 筆")

# 查詢週間/週末分布
query_weekend = """
SELECT
    CASE
        WHEN DATEPART(WEEKDAY, CREATE_DATE) IN (1, 7) THEN '週末'
        ELSE '平日'
    END AS day_type,
    AVG(CAST(daily_count AS FLOAT)) AS avg_count,
    COUNT(*) AS days_count
FROM (
    SELECT
        CAST(CREATE_DATE AS DATE) AS log_date,
        COUNT(*) AS daily_count,
        CREATE_DATE
    FROM CRMGY
    WHERE CREATE_DATE >= DATEADD(DAY, -30, GETDATE())
      AND GY012 IS NOT NULL
      AND LEN(LTRIM(RTRIM(GY012))) > 5
    GROUP BY CAST(CREATE_DATE AS DATE), CREATE_DATE
) sub
GROUP BY
    CASE
        WHEN DATEPART(WEEKDAY, CREATE_DATE) IN (1, 7) THEN '週末'
        ELSE '平日'
    END
"""

df_weekend = pd.read_sql(query_weekend, conn)

print("\n" + "=" * 80)
print("平日 vs 週末分布：")
print("=" * 80)
print(df_weekend.to_string(index=False))

conn.close()

print("\n" + "=" * 80)
print("建議使用的規劃數值：")
print("=" * 80)
avg = df_summary['avg_daily'].iloc[0]
max_val = df_summary['max_daily'].iloc[0]
print(f"• 日均處理量（用於常態估算）：{int(avg)} 筆/天")
print(f"• 高峰處理量（用於容量規劃）：{int(max_val)} 筆/天")
print(f"• 建議伺服器記憶體配置：{max(4, int(max_val / 500 * 4))} GB")
print(f"• 建議 API quota 緩衝：{int(max_val / 60) + 1} 分鐘執行時間")

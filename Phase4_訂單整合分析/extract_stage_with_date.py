# 萃取商機階段資料（帶日期）
# 從 CRMGY 業務日誌表萃取，包含時間戳記

import pyodbc
import configparser
import pandas as pd
from datetime import datetime
import re

print("=" * 70)
print("萃取商機階段資料（帶日期）")
print("=" * 70)

# SQL 連線
SQL_INI = r"D:\yujui\SqlServer18.txt"
cfg = configparser.ConfigParser()
cfg.read(SQL_INI, encoding="utf-8")
sec = cfg["mssql"]

CONN_STR = (
    f"DRIVER={{SQL Server}};SERVER={sec['server']};"
    f"DATABASE=DSC_CRM_SP;UID={sec['uid']};PWD={sec['pwd']}"
)

conn = pyodbc.connect(CONN_STR, autocommit=True)

print("\n 查詢 CRMGY 業務日誌...")

# 查詢所有業務日誌（帶日期）
query = """
SELECT
    GY001 as company_id,
    GY012 as log_content,
    MODI_DATE as log_date
FROM DSC_CRM_SP.dbo.CRMGY
WHERE LEN(GY001) = 10
AND GY012 IS NOT NULL
AND MODI_DATE >= '20240101'
ORDER BY GY001, MODI_DATE
"""

logs_df = pd.read_sql(query, conn)
conn.close()

print(f"   查詢完成：{len(logs_df):,} 筆日誌")
print(f"   涵蓋公司：{logs_df['company_id'].nunique():,} 家")

# 轉換日期格式
logs_df['log_date'] = pd.to_datetime(logs_df['log_date'])

print("\n 判斷商機階段...")

# 商機階段關鍵字
STAGE_KEYWORDS = {
    'A': [
        '簽約', '成交', '下單', '訂單', '合約', '用印', '簽核',
        '付款', '收款', '開發票', '已簽', '已成交'
    ],
    'B': [
        '報價', '提案', '估價', '議價', '價格', '金額', '預算',
        'POC', '測試', '試用', '展示', 'demo'
    ],
    'C1': [
        '需求', '規格', '功能', '確認', '討論', '會議', '拜訪',
        '了解', '評估', '比較'
    ],
    'C2': [
        '有興趣', '考慮', '參考', '資料', '簡介', '型錄',
        '詢問', '諮詢', '洽詢'
    ],
    'D': [
        '追蹤', '後續', '聯繫', '關心', '提醒', '再次',
        '待確認', '回覆', '保持聯絡'
    ],
    'E': [
        '開發', '名單', '陌生', '初次', '介紹', '認識',
        '引流', '活動', '電話', '掃街'
    ]
}

def detect_stage(log_content):
    """偵測日誌內容的商機階段"""
    if pd.isna(log_content) or not str(log_content).strip():
        return 'none'

    content = str(log_content).lower()

    # 按優先順序檢查（A > B > C1 > C2 > D > E）
    for stage in ['A', 'B', 'C1', 'C2', 'D', 'E']:
        for keyword in STAGE_KEYWORDS[stage]:
            if keyword.lower() in content:
                return stage

    return 'none'

# 批次判斷階段
logs_df['stage'] = logs_df['log_content'].apply(detect_stage)

# 統計
stage_counts = logs_df['stage'].value_counts()
print("\n各階段日誌數量：")
for stage in ['A', 'B', 'C1', 'C2', 'D', 'E', 'none']:
    if stage in stage_counts.index:
        count = stage_counts[stage]
        pct = count / len(logs_df) * 100
        print(f"   {stage:4s}: {count:7,} ({pct:5.1f}%)")

# 只保留有商機階段的日誌
logs_with_stage = logs_df[logs_df['stage'] != 'none'].copy()
print(f"\nOK 保留有效商機日誌：{len(logs_with_stage):,} 筆")

# 儲存結果
output_path = r"d:\yujui\痛點需求地圖\lead_stage_with_date.csv"
logs_with_stage.to_csv(
    output_path,
    index=False,
    encoding='utf-8-sig'
)

print(f"\nOK 已儲存：{output_path}")
print(f"   欄位：company_id, log_content, log_date, stage")
print(f"   筆數：{len(logs_with_stage):,}")

# 預覽
print("\n範例資料（前 5 筆）：")
print(logs_with_stage.head()[['company_id', 'log_date', 'stage']].to_string(index=False))

print("\n" + "=" * 70)
print("OK 完成！")

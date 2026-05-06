# -*- coding: utf-8 -*-
import json, pyodbc, configparser, pandas as pd, hashlib, sys

skip_ids = set()
with open(r'd:\yujui\痛點需求地圖\step1_output\step1_results.jsonl', encoding='utf-8') as f:
    for line in f:
        r = json.loads(line)
        if r.get('step1_confidence') == 'SKIP':
            skip_ids.add(r['event_id'])
        if len(skip_ids) >= 2000:
            break

cfg = configparser.ConfigParser()
cfg.read(r'D:\yujui\SqlServer18.txt', encoding='utf-8')
sec = cfg['mssql']
conn = pyodbc.connect(
    f"DRIVER={{SQL Server}};SERVER={sec['server']};DATABASE=DSC_CRM_SP;"
    f"UID={sec['uid']};PWD={sec['pwd']};", autocommit=True
)

logs = pd.read_sql("SELECT GY012 FROM CRMGY WHERE LEN(GY012) >= 5 AND LEN(GY012) < 50", conn)
logs['event_id'] = logs['GY012'].astype(str).apply(
    lambda t: hashlib.sha256(t.encode()).hexdigest()[:16]
)
sample = logs[logs['event_id'].isin(skip_ids)].drop_duplicates('GY012').head(60)

out = open(r'd:\yujui\痛點需求地圖\prompt定版\_skip_samples.txt', 'w', encoding='utf-8')
out.write(f"抽樣 {len(sample)} 筆 SKIP 日誌原文：\n\n")
for txt in sample['GY012'].tolist():
    out.write(txt + '\n')
out.close()
print("done: _skip_samples.txt")

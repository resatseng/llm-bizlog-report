# Phase 1：法人屬性標籤

## 目的
從業務日誌萃取法人的 8 大基礎屬性，作為後續分析的基礎維度。

## 輸入資料
- 業務日誌（來自 SQL Server CRMGY 表）

## 輸出
- `results/company_labels_flat.csv` - 法人屬性標籤（約 19MB，178,790 家公司）

## 8 大屬性
1. 外資屬性 (f_foreign)
2. 家族企業 (f_family)
3. 商業模式 (f_biz_model)
4. 員工規模 (f_headcount)
5. 其他屬性...

## 後續使用
- Phase M 聚類分析使用這些屬性作為特徵
- Phase 3 痛需熱圖使用這些屬性豐富公司維度表

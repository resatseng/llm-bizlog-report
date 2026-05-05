# Phase M：法人分層聚類

## 目的
基於 Phase 1 的 8 大屬性，將法人公司分為 7 個典型類型（C0-C6）。

## 程式
- `L-PhaseM分層聚類.ipynb` - 使用 KMeans 聚類分析

## 輸入資料
- Phase 1 `company_labels_flat.csv` - 法人 8 大屬性

## 處理方法
1. 特徵編碼（數值化、One-Hot）
2. 標準化（StandardScaler）
3. KMeans 聚類（n_clusters=7）
4. PCA 降維視覺化

## 輸出檔案

### 聚類結果
- `company_clusters.csv` - 公司 ID 與聚類編號（約 206,797 家）
- `cluster_profiles.csv` - 各聚類的特徵輪廓

### 視覺化
- `cluster_pca_map.png` - PCA 2D 聚類分布圖
- `cluster_radar.png` - 整體雷達圖（7 個聚類對比）
- `radar_c0.png` ~ `radar_c6.png` - 各聚類獨立雷達圖

### 分析結果
- `hotpaths.csv` - 熱門路徑分析

## 聚類命名與特徵

| 編號 | 名稱 | 特徵 |
|------|------|------|
| C0 | 微型內銷 | 小規模、本土市場 |
| C1 | 標準內銷 | 中等規模、內銷為主 |
| C2 | 大型外商 | 大規模、外資背景 |
| C3 | 多面型強者 | 多元業務模式 |
| C4 | 品牌驅動 | 品牌經營為核心 |
| C5 | 家族外銷 | 家族企業、外銷導向 |
| C6 | 外資貿易 | 外資、貿易型態 |

## 後續使用
- Phase 3 使用聚類編號作為痛需熱圖的維度之一
- 商業分析使用聚類區分不同客群的需求特性

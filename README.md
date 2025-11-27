# Steam Review Fetch & Analysis Tool

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

一个专为游戏开发者设计的 Steam 评论抓取和分析工具，支持批量获取、智能分类和飞书多维表格导出。

## ✨ 功能特性

- 🚀 **批量抓取评论**：支持断点续传、自动去重、智能重试
- 🎯 **智能分类系统**：按优先级（P0-P3）和问题类型自动分类
- 📊 **多维度分析**：语言分布、游戏时长、情感分析、趋势分析
- 📈 **可视化报告**：自动生成 Markdown 报告和 Excel 汇总表
- 🔄 **飞书集成**：一键导入飞书多维表格，支持团队协作
- ⚙️ **灵活配置**：支持语言筛选、评价类型、时间范围等多种参数

## 📋 目录

- [快速开始](#-快速开始)
- [安装](#-安装)
- [使用方法](#-使用方法)
- [配置说明](#-配置说明)
- [输出文件](#-输出文件)
- [分类规则](#-分类规则)
- [项目结构](#-项目结构)
- [常见问题](#-常见问题)

## 🚀 快速开始

### 前置要求

- Python 3.7 或更高版本
- Steam App ID（在游戏的 Steam 商店页面 URL 中获取）

### 快速运行

```bash
# 1. 克隆仓库
git clone https://github.com/Seafoodsz/SteamReviewFetch.git
cd SteamReviewFetch

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置 App ID（编辑 scripts/config.json）
{
  "app_id": "你的游戏ID",
  "language": "all",
  "review_type": "all"
}

# 4. 抓取评论
python scripts/steam_reviews_fetcher_v2.py

# 5. 智能分类
python scripts/classify_reviews.py

# 6. 生成报告
python scripts/generate_report.py
```

## 📦 安装

### 方法一：使用 pip

```bash
pip install requests tqdm pandas openpyxl
```

### 方法二：使用 requirements.txt

```bash
pip install -r requirements.txt
```

### Windows 一键运行

```bash
run.bat
```

## 📖 使用方法

### 1. 抓取评论

```bash
# 使用配置文件中的 app_id
python scripts/steam_reviews_fetcher_v2.py

# 或指定 app_id
python scripts/steam_reviews_fetcher_v2.py 1091500
```

**功能特点：**
- ✅ 自动去重（基于 recommendationid）
- ✅ 断点续传（使用游标机制）
- ✅ 自动重试（网络错误自动重试 3 次）
- ✅ 进度显示（实时显示抓取进度）

### 2. 智能分类

```bash
python scripts/classify_reviews.py
```

**分类维度：**

| 维度 | 选项 | 说明 |
|------|------|------|
| **优先级** | P0/P1/P2/P3 | 基于点赞数、游戏时长、问题类型综合评分 |
| **问题类型** | 技术问题、战斗机制、内容不足等 | 关键词匹配 + 规则引擎 |
| **标签** | 正面反馈、负面反馈、有建议、退款风险 | 自动标记 |

### 3. 数据分析

```bash
# 分析单个文件
python scripts/analyze_reviews.py output/reviews_1091500_20240115.json

# 生成汇总报告
python scripts/create_summary_excel.py
```

### 4. 导入飞书

```bash
# 单次导入
python scripts/import_to_feishu.py

# 批量导入
python scripts/batch_import_to_feishu.py
```

## ⚙️ 配置说明

### config.json 参数

```json
{
  "app_id": "1091500",
  "filter": "all",
  "language": "all",
  "review_type": "all",
  "day_range": 365,
  "num_per_page": 100,
  "delay": 0.5,
  "output_dir": "output",
  "export_csv": true
}
```

| 参数 | 类型 | 可选值 | 说明 |
|------|------|--------|------|
| `app_id` | string | - | Steam 游戏 ID |
| `filter` | string | all/recent/updated | 评论筛选方式 |
| `language` | string | all/schinese/english | 语言筛选 |
| `review_type` | string | all/positive/negative | 评价类型 |
| `day_range` | int | 1-365 | 时间范围（天）|
| `num_per_page` | int | 1-100 | 每页数量 |
| `delay` | float | 0.5-2.0 | 请求间隔（秒）|
| `output_dir` | string | - | 输出目录 |
| `export_csv` | bool | true/false | 是否导出 CSV |

## 📁 输出文件

```
output/
├── reviews_{appid}_{timestamp}.json      # 原始评论数据
├── reviews_{appid}_{timestamp}.csv       # CSV 格式
├── classified_reviews.json               # 分类后的数据
├── feishu_all_reviews.csv               # 飞书导入文件
└── analysis_report_{timestamp}.md       # 分析报告
```

## 🎯 分类规则

### 优先级计算

```python
优先级分数 = 点赞权重 × 0.4 + 时长权重 × 0.3 + 问题权重 × 0.3
```

**权重说明：**
- **点赞数**：高点赞评论权重更高（最高 100 分）
- **游戏时长**：深度玩家（>50h）权重更高（最高 100 分）
- **问题类型**：技术问题 > 平衡性 > UI/UX（10-30 分）
- **差评加成**：差评额外 +20 分

### 问题类型识别

| 类型 | 关键词示例 | 权重 |
|------|-----------|------|
| 技术问题 | 闪退、卡顿、bug、报错 | 30 |
| 战斗机制 | 战斗、打击感、技能 | 20 |
| 内容不足 | 内容少、重复、单调 | 15 |
| 游戏节奏 | 节奏慢、拖沓、无聊 | 15 |
| 上手难度 | 难度高、新手不友好 | 10 |
| 平衡性 | 平衡性、数值、削弱 | 20 |

详细规则见 [resources/classification-rules.md](resources/classification-rules.md)

## 📂 项目结构

```
SteamReviewFetch/
├── scripts/                        # 核心脚本
│   ├── steam_reviews_fetcher_v2.py  # 评论抓取
│   ├── classify_reviews.py          # 智能分类
│   ├── analyze_reviews.py           # 数据分析
│   ├── generate_report.py           # 报告生成
│   ├── create_summary_excel.py      # Excel 汇总
│   ├── import_to_feishu.py          # 飞书导入
│   └── config.json                  # 配置文件
├── resources/                      # 文档资源
│   ├── steam-api-reference.md       # Steam API 文档
│   ├── classification-rules.md      # 分类规则详解
│   └── feishu-integration.md        # 飞书集成指南
├── output/                         # 数据输出目录
├── reports/                        # 报告输出目录
├── docs/                           # 使用文档
├── run.bat                         # Windows 启动脚本
├── requirements.txt                # 依赖列表
└── README.md                       # 本文件
```

## 🔧 高级用法

### 自定义分类规则

编辑 `scripts/classify_reviews.py` 中的关键词字典：

```python
ISSUE_KEYWORDS = {
    "技术问题": ["闪退", "卡顿", "bug", ...],
    "自定义类型": ["关键词1", "关键词2", ...],
    # 添加更多类型...
}
```

### API 速率限制

Steam API 无官方速率限制，但建议：
- 请求间隔 ≥ 0.5 秒
- 并发请求数 ≤ 5
- 失败重试间隔 2 秒

详见 [resources/steam-api-reference.md](resources/steam-api-reference.md)

### 飞书集成

需要配置飞书应用凭证：

```json
{
  "app_id": "飞书应用ID",
  "app_secret": "飞书应用密钥",
  "folder_token": "目标文件夹Token"
}
```

详细步骤见 [resources/feishu-integration.md](resources/feishu-integration.md)

## 📊 关键指标

| 指标 | 警戒值 | 目标值 | 说明 |
|------|--------|--------|------|
| 好评率 | < 70% | > 85% | 总体评价健康度 |
| P0/P1 问题数 | > 50 | < 20 | 高优先级问题数量 |
| 技术问题占比 | > 30% | < 10% | 严重 bug 比例 |
| 平均游戏时长 | < 2h | > 10h | 玩家留存指标 |
| 退款风险评论 | > 20 | < 5 | 包含"退款"关键词 |

## ❓ 常见问题

### Q: 抓取速度很慢怎么办？

A: 调整 `config.json` 中的 `delay` 参数（推荐 0.5-1.0 秒）

### Q: 出现重复数据怎么办？

A: 脚本已自动基于 `recommendationid` 去重，无需手动处理

### Q: 飞书导入失败？

A: 确保 CSV 文件编码为 UTF-8，或使用 API 方式导入（见飞书集成文档）

### Q: 如何获取 Steam App ID？

A: 在游戏的 Steam 商店页面 URL 中查找数字 ID：
```
https://store.steampowered.com/app/1091500/
                                   ^^^^^^^ 这就是 App ID
```

### Q: 支持哪些语言的评论？

A: 支持所有 Steam 评论语言，包括：
- schinese（简体中文）
- english（英语）
- japanese（日语）
- 以及 Steam 支持的其他所有语言

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 提交 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 🔗 相关链接

- [Steam Web API 文档](https://partner.steamgames.com/doc/webapi_overview)
- [飞书开放平台](https://open.feishu.cn/)
- [问题反馈](https://github.com/Seafoodsz/SteamReviewFetch/issues)

## 👨‍💻 作者

[@Seafoodsz](https://github.com/Seafoodsz)

---

如果这个项目对你有帮助，请给个 ⭐️ Star 支持一下！

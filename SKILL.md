---
name: analyzing-steam-reviews
description: 抓取Steam游戏评论，按优先级和问题类型智能分类，生成分析报告，并导入飞书多维表格。当用户需要收集、分析或管理Steam游戏评论进行团队协作时使用此技能。
---

# Steam评论抓取与分析

提供完整的Steam游戏评论分析和飞书导入工作流。

## 使用场景

- 用户需要抓取Steam游戏评论
- 用户需要分析玩家反馈
- 用户需要将评论数据导入飞书/Lark
- 用户需要对游戏问题进行优先级分类
- 用户询问Steam评论API

## 快速开始

询问用户的 **Steam App ID**（在游戏的Steam链接中可以找到）。

### 第一阶段：抓取评论

```bash
# 安装依赖
pip install requests tqdm

# 运行抓取器（需要config.json配置app_id）
python steam_reviews_fetcher_v2.py
```

**API端点**: `https://store.steampowered.com/appreviews/{appid}?json=1`

关键参数：
- `filter`: all(全部), recent(最近), updated(已更新)
- `language`: all(全部), schinese(简中), english(英语)
- `review_type`: all(全部), positive(好评), negative(差评)
- `num_per_page`: 1-100（默认100）
- `cursor`: 分页游标（起始值为"*"）

### 第二阶段：分类评论

```bash
python classify_reviews.py
```

分类维度：
1. **优先级**: P0-紧急, P1-高, P2-中, P3-低
2. **问题类型**: 技术问题, 战斗机制, 内容不足, 上手难度, 平衡性, UI/UX
3. **标签**: 正面反馈, 负面反馈, 有建议, 退款风险

### 第三阶段：导入飞书

使用飞书MCP工具创建Base并导入数据。

详细步骤见 `resources/feishu-integration.md`

## 输出文件

- `output/reviews_{appid}_{timestamp}.json` - 原始评论
- `output/classified_reviews.json` - 分类数据
- `output/feishu_all_reviews.csv` - 飞书导入文件
- `output/01-07_*.csv` - 分析报表

## 资源文件

- `resources/steam-api-reference.md` - Steam API文档
- `resources/classification-rules.md` - 分类逻辑详解
- `resources/feishu-integration.md` - 飞书导入指南
- `scripts/` - Python自动化脚本

## 配置文件

创建 `config.json`：
```json
{
  "app_id": "你的APP_ID",
  "filter": "all",
  "language": "all",
  "review_type": "all",
  "num_per_page": 100,
  "delay": 0.5,
  "output_dir": "output",
  "export_csv": true
}
```

## 关键指标

| 指标 | 警戒值 | 目标值 |
|------|--------|--------|
| 好评率 | < 70% | > 85% |
| P0/P1问题数 | > 50 | < 20 |
| 技术问题占比 | > 30% | < 10% |

## 常见问题

| 问题 | 解决方案 |
|------|----------|
| 抓取慢 | 增加config中的delay值 |
| 数据重复 | 脚本已用recommendationid去重 |
| 飞书导入失败 | 使用CSV导入方式，确保UTF-8编码 |

## 完整工作流

1. 获取用户的App ID
2. 配置config.json
3. 运行抓取脚本获取评论
4. 运行分类脚本分析评论
5. 创建飞书多维表格
6. 导入CSV数据到飞书
7. 创建筛选视图供团队使用

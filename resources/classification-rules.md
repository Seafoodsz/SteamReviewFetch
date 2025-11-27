# Review Classification Rules

## Priority Levels

### P0 - Urgent
Criteria (ALL must match):
- Negative review (`voted_up: false`)
- High visibility (`votes_up >= 10`)
- Contains technical keywords

Keywords: crash, bug, error, freeze, lag, stuck, broken, unplayable

### P1 - High
Criteria (ANY):
- Negative review with `votes_up >= 5`
- Contains gameplay-critical issues
- Multiple issue types detected

Keywords: difficult, hard, frustrating, unfair, boring, repetitive

### P2 - Medium
Criteria:
- Negative review with suggestions
- Positive review with constructive feedback
- Contains improvement suggestions

Keywords: hope, suggest, wish, should, could, better, improve

### P3 - Low
Default for:
- Standard positive reviews
- Short reviews without specific issues
- Reviews without actionable feedback

## Issue Categories

### Technical Issues
Keywords (CN): 崩溃, 卡顿, 闪退, bug, 报错, 掉帧, 加载, 存档
Keywords (EN): crash, bug, error, freeze, lag, fps, load, save

### Combat/Gameplay
Keywords (CN): 战斗, 打击感, 技能, 招式, 攻击, 格挡, 闪避
Keywords (EN): combat, hit, skill, attack, dodge, block, fight

### Content Depth
Keywords (CN): 内容, 流程, 小时, 太短, 不够, 单薄
Keywords (EN): content, short, hours, length, replay

### Learning Curve
Keywords (CN): 难度, 上手, 教程, 新手, 学习, 入门
Keywords (EN): difficulty, tutorial, learning, beginner, hard

### Balance
Keywords (CN): 平衡, 数值, 强弱, 太强, 太弱, 不平衡
Keywords (EN): balance, overpowered, weak, unfair, nerf, buff

### UI/UX
Keywords (CN): 界面, 操作, 按键, 手柄, 鼠标, 键盘, 菜单
Keywords (EN): UI, interface, control, controller, menu, button

### Price/Value
Keywords (CN): 价格, 定价, 贵, 值, 性价比
Keywords (EN): price, expensive, worth, value, cheap

## Tag System

### Sentiment Tags
- `positive`: `voted_up: true`
- `negative`: `voted_up: false`

### Content Tags
- `has_suggestion`: Contains improvement keywords
- `has_expectation`: Contains future/update keywords
- `refund_risk`: Contains refund/退款 keywords
- `awaiting_update`: Contains update/更新 keywords

## Priority Algorithm

```python
def calculate_priority(review):
    is_negative = not review['voted_up']
    votes = review['votes_up']
    has_tech_issue = check_keywords(review, TECH_KEYWORDS)

    if is_negative and votes >= 10 and has_tech_issue:
        return 'P0'
    elif is_negative and votes >= 5:
        return 'P1'
    elif is_negative or has_suggestions(review):
        return 'P2'
    else:
        return 'P3'
```

## Output Format

Each classified review includes:
```json
{
  "recommendationid": "...",
  "priority": "P1",
  "issue_types": ["Technical", "UI/UX"],
  "tags": ["negative", "has_suggestion"],
  "key_points": "Extracted main feedback...",
  "original_review": "..."
}
```

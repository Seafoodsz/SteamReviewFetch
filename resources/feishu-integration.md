# Feishu (Lark) Integration Guide

## Method 1: CSV Import (Recommended)

### Step 1: Prepare CSV File
Ensure `output/feishu_all_reviews.csv` exists with UTF-8 encoding.

### Step 2: Create Feishu Base
Use MCP tool:
```python
mcp__lark-mcp__bitable_v1_app_create(
    data={
        "name": "Game Reviews Analysis",
        "time_zone": "Asia/Shanghai"
    }
)
```

### Step 3: Create Table Structure
```python
mcp__lark-mcp__bitable_v1_appTable_create(
    path={"app_token": "YOUR_APP_TOKEN"},
    data={
        "table": {
            "name": "Reviews",
            "fields": [
                {"field_name": "Review ID", "type": 1},
                {"field_name": "Review Date", "type": 5},
                {"field_name": "Review Type", "type": 3, "property": {
                    "options": [
                        {"name": "Positive", "color": 1},
                        {"name": "Negative", "color": 2}
                    ]
                }},
                {"field_name": "Priority", "type": 3, "property": {
                    "options": [
                        {"name": "P0-Urgent", "color": 2},
                        {"name": "P1-High", "color": 3},
                        {"name": "P2-Medium", "color": 4},
                        {"name": "P3-Low", "color": 1}
                    ]
                }},
                {"field_name": "Issue Type", "type": 1},
                {"field_name": "Tags", "type": 1},
                {"field_name": "Review Content", "type": 1},
                {"field_name": "Key Points", "type": 1},
                {"field_name": "Language", "type": 3},
                {"field_name": "Playtime (Hours)", "type": 2},
                {"field_name": "Votes Up", "type": 2},
                {"field_name": "Steam Purchase", "type": 7},
                {"field_name": "Games Owned", "type": 2}
            ]
        }
    }
)
```

### Step 4: Import CSV
1. Open the Feishu Base URL
2. Click menu [...] -> Import -> From Local File
3. Select `feishu_all_reviews.csv`
4. Map fields and confirm

## Method 2: API Import

For automation, use record creation API:

```python
mcp__lark-mcp__bitable_v1_appTableRecord_create(
    path={
        "app_token": "YOUR_APP_TOKEN",
        "table_id": "YOUR_TABLE_ID"
    },
    data={
        "fields": {
            "Review ID": "123456",
            "Review Type": "Negative",
            "Priority": "P0-Urgent",
            "Review Content": "Game crashes...",
            "Votes Up": 15
        }
    }
)
```

**Note**: DateTime fields require Unix timestamp (milliseconds), not strings.

## Recommended Views

### 1. High Priority Board
- Filter: Priority = P0-Urgent OR P1-High
- Sort: Votes Up (descending)

### 2. Technical Issues
- Filter: Issue Type contains "Technical"
- Group by: Priority

### 3. Negative Analysis
- Filter: Review Type = Negative
- Group by: Issue Type

### 4. Language Distribution
- Group by: Language
- Summary: Count

## Field Type Reference

| Type Code | Field Type |
|-----------|------------|
| 1 | Text |
| 2 | Number |
| 3 | Single Select |
| 4 | Multi Select |
| 5 | DateTime |
| 7 | Checkbox |
| 11 | Person |

## Troubleshooting

### Import Encoding Error
- Ensure CSV is UTF-8 with BOM
- Open in Notepad, Save As -> UTF-8

### DateTime Field Error
- Use Unix timestamp in milliseconds
- Example: `1732550400000` not `"2024-11-26"`

### Batch Import Limit
- Maximum 500 records per batch
- Add delay between batches

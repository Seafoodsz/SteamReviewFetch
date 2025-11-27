# Steam Reviews API Reference

## Endpoint

```
GET https://store.steampowered.com/appreviews/{appid}?json=1
```

No API key required for public reviews.

## Parameters

| Parameter | Values | Description |
|-----------|--------|-------------|
| `json` | 1 | Return JSON format |
| `filter` | all, recent, updated | Filter type |
| `language` | all, schinese, english, etc. | Review language |
| `day_range` | 1-365 | Days range for "recent" filter |
| `cursor` | string | Pagination cursor (start with "*") |
| `review_type` | all, positive, negative | Review sentiment |
| `purchase_type` | all, steam, non_steam_purchase | Purchase source |
| `num_per_page` | 1-100 | Reviews per request |
| `filter_offtopic_activity` | 0, 1 | Filter review bombs |

## Response Structure

```json
{
  "success": 1,
  "query_summary": {
    "num_reviews": 486,
    "review_score": 8,
    "review_score_desc": "Very Positive",
    "total_positive": 406,
    "total_negative": 80,
    "total_reviews": 486
  },
  "reviews": [
    {
      "recommendationid": "unique_id",
      "author": {
        "steamid": "...",
        "num_games_owned": 100,
        "num_reviews": 10,
        "playtime_forever": 3600,
        "playtime_at_review": 1800,
        "last_played": 1732550400
      },
      "language": "schinese",
      "review": "Review text content...",
      "timestamp_created": 1732550400,
      "timestamp_updated": 1732550400,
      "voted_up": true,
      "votes_up": 10,
      "votes_funny": 2,
      "weighted_vote_score": 0.5,
      "steam_purchase": true,
      "received_for_free": false,
      "written_during_early_access": false
    }
  ],
  "cursor": "next_page_cursor"
}
```

## Pagination

1. First request: `cursor=*`
2. Use returned `cursor` for next page
3. Stop when `reviews` array is empty or cursor repeats

## Rate Limiting

- Recommended delay: 0.5-1 second between requests
- No official rate limit documented
- Use deduplication to avoid infinite loops

## Language Codes

| Code | Language |
|------|----------|
| schinese | Simplified Chinese |
| tchinese | Traditional Chinese |
| english | English |
| japanese | Japanese |
| koreana | Korean |
| all | All languages |

## Example Request

```bash
curl "https://store.steampowered.com/appreviews/3081280?json=1&filter=all&language=all&num_per_page=100&cursor=*"
```

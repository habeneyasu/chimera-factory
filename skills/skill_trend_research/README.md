# Skill: Trend Research

**Skill ID**: `skill_trend_research`  
**Version**: 1.0.0  
**Status**: 📋 **Contract Defined** (Implementation pending)

---

## Purpose

The Trend Research skill enables Chimera agents to research trending topics from multiple sources (Twitter, YouTube, News APIs, Reddit, OpenClaw) to identify emerging topics for content creation. This skill is critical for ensuring content remains relevant and aligned with current trends.

**Related User Stories**: 
- `specs/functional.md` US-001: Research Trends from Multiple Sources
- `specs/functional.md` US-002: Analyze Trend Patterns
- `specs/functional.md` US-003: Discover Trends from OpenClaw Network

---

## Use Cases

1. **Content Planning**: Research trends before creating content plans
2. **Trend Discovery**: Identify emerging topics across multiple platforms
3. **Network Intelligence**: Discover trends shared by other agents in OpenClaw
4. **Competitive Analysis**: Monitor trending topics in specific niches
5. **Content Optimization**: Find trending hashtags and related topics

---

## Input/Output Contract

### Input Contract

See `contract.json` for complete JSON Schema definition.

**Required Fields**:
- `topic` (string): Topic or keyword to research
- `sources` (array): List of sources to query (twitter, news, reddit, youtube, openclaw)

**Optional Fields**:
- `timeframe` (string, default: "24h"): Time window for trend analysis
  - Valid values: "1h", "24h", "7d", "30d"

**Example Input**:
```json
{
  "topic": "AI influencers",
  "sources": ["twitter", "news", "reddit"],
  "timeframe": "24h"
}
```

### Output Contract

See `contract.json` for complete JSON Schema definition.

**Required Fields**:
- `trends` (array): List of trend items with metadata
- `confidence` (number, 0-1): Confidence score for trend accuracy

**Trend Item Structure**:
- `title` (string): Trend title/headline
- `source` (string): Source platform (twitter, news, reddit, etc.)
- `engagement` (number): Engagement metric (likes, views, upvotes)
- `timestamp` (string, ISO 8601): When the trend was observed

**Example Output**:
```json
{
  "trends": [
    {
      "title": "AI influencers are taking over social media",
      "source": "twitter",
      "engagement": 12500,
      "timestamp": "2026-02-04T12:00:00Z"
    },
    {
      "title": "The rise of autonomous content creators",
      "source": "news",
      "engagement": 8500,
      "timestamp": "2026-02-04T11:30:00Z"
    }
  ],
  "confidence": 0.85
}
```

---

## MCP Dependencies

This skill requires the following runtime MCP servers:

1. **Twitter MCP** (`@modelcontextprotocol/server-twitter`):
   - Tool: `search_tweets` - Search Twitter for trending topics
   - Tool: `get_trending_topics` - Get trending topics by location

2. **News MCP** (`@modelcontextprotocol/server-news`):
   - Tool: `search_news` - Search news articles by topic
   - Tool: `get_headlines` - Get current headlines

3. **Reddit MCP** (`@modelcontextprotocol/server-reddit`):
   - Tool: `search_reddit` - Search Reddit posts
   - Tool: `get_trending_subreddits` - Get trending subreddits

4. **YouTube MCP** (`@modelcontextprotocol/server-youtube`):
   - Tool: `search_videos` - Search YouTube videos by topic
   - Tool: `get_trending_videos` - Get trending videos

5. **OpenClaw MCP** (custom):
   - Tool: `discover_trends` - Discover trends from OpenClaw network
   - Resource: `openclaw://trends/{trend_id}` - Access shared trends

**Note**: These are runtime MCP servers, separate from development MCP servers. See `research/tooling_strategy.md` for the distinction.

---

## Implementation Notes

### Error Handling

The skill must handle errors gracefully:

1. **Source Failures**: If one source fails, continue with other sources
2. **Rate Limiting**: Respect API rate limits and implement backoff
3. **Network Errors**: Retry with exponential backoff
4. **Invalid Input**: Validate input and return clear error messages

**Error Response Format**:
```json
{
  "error": {
    "code": "SOURCE_FAILED",
    "message": "Twitter API request failed",
    "source": "twitter",
    "retryable": true
  }
}
```

### Performance Considerations

1. **Parallel Queries**: Query multiple sources in parallel
2. **Caching**: Cache recent trend queries to reduce API calls
3. **Timeout**: Set reasonable timeouts for each source (e.g., 10 seconds)
4. **Result Limiting**: Limit results per source to prevent overwhelming responses

### Logging

All skill executions must be logged with:
- Input parameters
- Sources queried
- Number of trends found
- Execution time
- Errors encountered
- Confidence scores

---

## Examples

### Example 1: Basic Trend Research

**Input**:
```json
{
  "topic": "fashion trends",
  "sources": ["twitter", "instagram"],
  "timeframe": "24h"
}
```

**Expected Output**:
```json
{
  "trends": [
    {
      "title": "Sustainable fashion is trending",
      "source": "twitter",
      "engagement": 15200,
      "timestamp": "2026-02-04T10:00:00Z"
    }
  ],
  "confidence": 0.78
}
```

### Example 2: Multi-Source Research

**Input**:
```json
{
  "topic": "AI content creation",
  "sources": ["twitter", "news", "reddit", "youtube"],
  "timeframe": "7d"
}
```

**Expected Output**:
```json
{
  "trends": [
    {
      "title": "AI-generated content reaches new heights",
      "source": "news",
      "engagement": 25000,
      "timestamp": "2026-02-03T14:00:00Z"
    },
    {
      "title": "r/artificial discusses AI content tools",
      "source": "reddit",
      "engagement": 8500,
      "timestamp": "2026-02-04T08:00:00Z"
    }
  ],
  "confidence": 0.92
}
```

---

## Testing Requirements

See `specs/functional.md` US-001 for acceptance criteria:

- ✅ Query trends by topic/keyword across multiple sources simultaneously
- ✅ Specify timeframes (1h, 24h, 7d, 30d) for trend analysis
- ✅ Receive structured trend data with metadata
- ✅ Filter trends by relevance score and engagement metrics
- ✅ Failed source queries don't block other sources (fault tolerance)
- ✅ All trend research actions are logged for audit purposes

---

## References

- **Contract Schema**: `contract.json` (this directory)
- **Functional Specs**: `specs/functional.md` (US-001, US-002, US-003)
- **Technical Specs**: `specs/technical.md` (Trend Research API)
- **OpenClaw Integration**: `specs/openclaw_integration.md`
- **Tooling Strategy**: `research/tooling_strategy.md` (MCP vs Skills)

---

**This skill enables agents to research trends from multiple sources, providing the foundation for content planning and generation.**

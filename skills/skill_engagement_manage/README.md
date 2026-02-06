# Skill: Engagement Management

**Skill ID**: `skill_engagement_manage`  
**Version**: 1.0.0  
**Status**: 📋 **Contract Defined** (Implementation pending)

---

## Purpose

The Engagement Management skill enables Chimera agents to manage social media engagement by responding to comments, liking posts, following accounts, and maintaining authentic interactions across platforms. This skill ensures agents can build and maintain relationships with their audience.

**Related User Stories**: 
- `specs/functional.md` US-010: Monitor Social Media Engagement
- `specs/functional.md` US-011: Respond to Comments and Messages
- `specs/functional.md` US-012: Manage Follows and Interactions

---

## Use Cases

1. **Comment Responses**: Generate and post contextually appropriate responses
2. **Engagement Actions**: Like, share, and follow relevant content
3. **Relationship Building**: Maintain authentic interactions with followers
4. **Crisis Management**: Handle negative comments appropriately
5. **Community Building**: Engage with influencers and collaborators

---

## Input/Output Contract

### Input Contract

See `contract.json` for complete JSON Schema definition.

**Required Fields**:
- `action` (string): Type of engagement action
  - Valid values: "reply", "like", "follow", "comment", "share"
- `platform` (string): Target social media platform
  - Valid values: "twitter", "instagram", "tiktok", "threads"
- `target` (string): Target post/comment/user ID

**Optional Fields**:
- `content` (string): Content for reply/comment (required for reply/comment actions)
- `persona_constraints` (array): Persona constraints to apply

**Example Input (Reply)**:
```json
{
  "action": "reply",
  "platform": "twitter",
  "target": "tweet_12345",
  "content": "Thanks for the feedback! We're always working to improve. What specific feature would you like to see?",
  "persona_constraints": ["professional", "helpful", "concise"]
}
```

**Example Input (Like)**:
```json
{
  "action": "like",
  "platform": "instagram",
  "target": "post_67890",
  "persona_constraints": ["authentic"]
}
```

**Example Input (Follow)**:
```json
{
  "action": "follow",
  "platform": "twitter",
  "target": "user_fashion_influencer",
  "persona_constraints": ["relevant", "strategic"]
}
```

### Output Contract

See `contract.json` for complete JSON Schema definition.

**Required Fields**:
- `status` (string): Status of engagement action
  - Valid values: "success", "pending", "failed"

**Optional Fields**:
- `engagement_id` (string): ID of created engagement (if successful)
- `platform_response` (object): Raw response from platform API
- `error` (object): Error details (if status is failed)

**Example Output (Success)**:
```json
{
  "status": "success",
  "engagement_id": "eng_abc123",
  "platform_response": {
    "id": "1234567890",
    "created_at": "2026-02-04T12:00:00Z",
    "text": "Thanks for the feedback! We're always working to improve."
  }
}
```

**Example Output (Pending)**:
```json
{
  "status": "pending",
  "engagement_id": "eng_xyz789",
  "platform_response": {
    "message": "Engagement queued for approval",
    "approval_required": true
  }
}
```

**Example Output (Failed)**:
```json
{
  "status": "failed",
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Twitter API rate limit exceeded. Retry after 15 minutes.",
    "retryable": true,
    "retry_after": 900
  }
}
```

---

## MCP Dependencies

This skill requires the following runtime MCP servers:

1. **Twitter MCP** (`@modelcontextprotocol/server-twitter`):
   - Tool: `reply_to_tweet` - Reply to a tweet
   - Tool: `like_tweet` - Like a tweet
   - Tool: `follow_user` - Follow a user
   - Tool: `retweet` - Retweet a post
   - Tool: `get_tweet` - Get tweet details

2. **Instagram MCP** (`@modelcontextprotocol/server-instagram`):
   - Tool: `comment_on_post` - Comment on a post
   - Tool: `like_post` - Like a post
   - Tool: `follow_user` - Follow a user
   - Tool: `reply_to_comment` - Reply to a comment

3. **TikTok MCP** (`@modelcontextprotocol/server-tiktok`):
   - Tool: `comment_on_video` - Comment on a video
   - Tool: `like_video` - Like a video
   - Tool: `follow_user` - Follow a user
   - Tool: `share_video` - Share a video

4. **Threads MCP** (`@modelcontextprotocol/server-threads`):
   - Tool: `reply_to_thread` - Reply to a thread
   - Tool: `like_thread` - Like a thread
   - Tool: `follow_user` - Follow a user

**Note**: These are runtime MCP servers, separate from development MCP servers. See `research/tooling_strategy.md` for the distinction.

---

## Implementation Notes

### Action-Specific Handling

1. **Reply/Comment Actions**:
   - Generate contextually appropriate responses using LLM
   - Apply persona constraints (tone, style, length)
   - Check for sensitive content requiring human approval
   - Validate response length per platform limits

2. **Like/Follow Actions**:
   - Validate target relevance before engaging
   - Check rate limits to avoid spam
   - Log all actions for audit trail
   - Respect platform-specific limits

3. **Share Actions**:
   - Add commentary when sharing (if platform supports)
   - Ensure shared content aligns with persona
   - Track shares for analytics

### Persona Constraints

Persona constraints guide engagement behavior:

- **Professional**: Formal tone, business-focused
- **Casual**: Friendly, conversational tone
- **Authentic**: Genuine, personal responses
- **Helpful**: Supportive, solution-oriented
- **Concise**: Short, to-the-point responses
- **Strategic**: Engagement aligned with goals

### Human-in-the-Loop Integration

For sensitive engagements:

1. **Auto-Approve** (confidence > 0.90): Execute immediately with logging
2. **Async Approval** (confidence 0.70-0.90): Queue for human review
3. **Reject** (confidence < 0.70): Do not engage, log for review

See `specs/_meta.md` for HITL constraints.

### Error Handling

1. **Rate Limiting**: Implement exponential backoff
2. **Invalid Targets**: Validate target IDs before engagement
3. **Platform Errors**: Handle platform-specific errors gracefully
4. **Network Failures**: Retry with backoff strategy

**Error Response Format**:
```json
{
  "status": "failed",
  "error": {
    "code": "INVALID_TARGET",
    "message": "Target post not found or inaccessible",
    "platform": "twitter",
    "target": "tweet_12345",
    "retryable": false
  }
}
```

### Performance Considerations

1. **Batch Operations**: Batch multiple engagements when possible
2. **Rate Limit Management**: Track and respect platform rate limits
3. **Async Processing**: Process engagements asynchronously
4. **Caching**: Cache user/post metadata to reduce API calls

### Logging

All skill executions must be logged with:
- Action type and platform
- Target ID
- Content (if applicable)
- Persona constraints applied
- Execution time
- Status and result
- Errors encountered

---

## Examples

### Example 1: Reply to Comment

**Input**:
```json
{
  "action": "reply",
  "platform": "instagram",
  "target": "comment_12345",
  "content": "Great question! We're planning to release that feature next month. Stay tuned! 🚀",
  "persona_constraints": ["helpful", "enthusiastic", "concise"]
}
```

**Expected Output**:
```json
{
  "status": "success",
  "engagement_id": "eng_insta_001",
  "platform_response": {
    "id": "reply_67890",
    "created_at": "2026-02-04T12:05:00Z",
    "text": "Great question! We're planning to release that feature next month. Stay tuned! 🚀"
  }
}
```

### Example 2: Like Post

**Input**:
```json
{
  "action": "like",
  "platform": "twitter",
  "target": "tweet_98765",
  "persona_constraints": ["authentic", "relevant"]
}
```

**Expected Output**:
```json
{
  "status": "success",
  "engagement_id": "eng_twitter_002",
  "platform_response": {
    "liked": true,
    "timestamp": "2026-02-04T12:10:00Z"
  }
}
```

### Example 3: Follow User (Pending Approval)

**Input**:
```json
{
  "action": "follow",
  "platform": "instagram",
  "target": "user_collaborator",
  "persona_constraints": ["strategic"]
}
```

**Expected Output**:
```json
{
  "status": "pending",
  "engagement_id": "eng_insta_003",
  "platform_response": {
    "message": "Follow request queued for approval",
    "approval_required": true,
    "confidence": 0.75
  }
}
```

---

## Testing Requirements

See `specs/functional.md` US-010, US-011, US-012 for acceptance criteria:

- ✅ Monitor engagement across multiple platforms
- ✅ Generate contextually appropriate responses
- ✅ Handle positive, negative, and neutral engagements
- ✅ Flag sensitive comments for human review
- ✅ Request human approval for sensitive responses
- ✅ Log all responses and interactions

---

## References

- **Contract Schema**: `contract.json` (this directory)
- **Functional Specs**: `specs/functional.md` (US-010, US-011, US-012)
- **Technical Specs**: `specs/technical.md` (Engagement Management API)
- **Database Schema**: `specs/database/schema.sql` (engagements table)
- **HITL Constraints**: `specs/_meta.md` (Human-in-the-Loop)
- **Tooling Strategy**: `research/tooling_strategy.md` (MCP vs Skills)

---

**This skill enables agents to manage social media engagement, building and maintaining authentic relationships with audiences across platforms.**

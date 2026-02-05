# Entity Relationship Diagram: Project Chimera Database

**Prepared By**: habeneyasu  
**Repository**: [https://github.com/habeneyasu/chimera-factory](https://github.com/habeneyasu/chimera-factory)  
**Last Updated**: February 2026

---

## ERD Diagram

```mermaid
erDiagram
    AGENTS ||--o{ CAMPAIGNS : "participates in"
    AGENTS ||--o{ TASKS : "assigned to"
    AGENTS ||--o{ CONTENT_PLANS : "creates"
    AGENTS ||--o{ CONTENT : "generates"
    AGENTS ||--o{ ENGAGEMENTS : "performs"
    AGENTS ||--o{ TRANSACTIONS : "executes"
    
    CAMPAIGNS ||--o{ CAMPAIGN_AGENTS : "has"
    AGENTS ||--o{ CAMPAIGN_AGENTS : "belongs to"
    CAMPAIGNS ||--o{ TASKS : "contains"
    
    CONTENT_PLANS ||--o{ CONTENT_PLAN_TRENDS : "references"
    CONTENT_PLANS ||--o{ CONTENT : "generates"
    CONTENT_PLANS ||--o{ APPROVALS : "requires"
    
    CONTENT ||--o| VIDEO_METADATA : "has (if video)"
    CONTENT ||--o{ APPROVALS : "requires"
    CONTENT ||--o{ ENGAGEMENTS : "receives"
    
    AGENTS {
        uuid id PK
        varchar name
        varchar persona_id
        varchar wallet_address UK
        varchar status
        timestamp created_at
        timestamp updated_at
    }
    
    CAMPAIGNS {
        uuid id PK
        text goal
        varchar status
        timestamp created_at
        timestamp updated_at
    }
    
    CAMPAIGN_AGENTS {
        uuid campaign_id PK,FK
        uuid agent_id PK,FK
    }
    
    TASKS {
        uuid id PK
        varchar task_type
        varchar priority
        varchar status
        uuid agent_id FK
        uuid campaign_id FK
        jsonb context
        varchar assigned_worker_id
        timestamp created_at
        timestamp updated_at
    }
    
    CONTENT_PLANS {
        uuid id PK
        uuid agent_id FK
        varchar content_type
        text target_audience
        varchar platform
        float confidence_score
        varchar approval_status
        jsonb structure
        jsonb key_messages
        timestamp created_at
        timestamp updated_at
    }
    
    CONTENT_PLAN_TRENDS {
        uuid plan_id PK,FK
        uuid trend_id PK
    }
    
    CONTENT {
        uuid id PK
        uuid plan_id FK
        uuid agent_id FK
        varchar content_type
        text content_url
        jsonb metadata
        float confidence_score
        varchar status
        timestamp created_at
        timestamp updated_at
    }
    
    VIDEO_METADATA {
        uuid id PK
        uuid content_id FK,UK
        float duration_seconds
        integer width
        integer height
        varchar format
        varchar codec
        integer bitrate_kbps
        float frame_rate
        bigint file_size_bytes
        text thumbnail_url
        boolean has_audio
        boolean has_captions
        text caption_url
        varchar aspect_ratio
        timestamp created_at
    }
    
    APPROVALS {
        uuid id PK
        uuid content_id FK
        uuid plan_id FK
        varchar approval_type
        varchar status
        varchar priority
        float confidence_score
        timestamp submitted_at
        timestamp expires_at
        timestamp decided_at
        varchar decided_by
        text feedback
        jsonb modifications
    }
    
    ENGAGEMENTS {
        uuid id PK
        uuid agent_id FK
        varchar platform
        varchar action
        varchar target_id
        uuid content_id FK
        varchar status
        jsonb platform_response
        timestamp created_at
    }
    
    TRANSACTIONS {
        uuid id PK
        uuid agent_id FK
        varchar transaction_hash UK
        varchar transaction_type
        decimal amount
        varchar token_address
        varchar to_address
        varchar status
        bigint block_number
        timestamp created_at
    }
```

---

## Key Relationships

### Content Flow
1. **Trend Research** → `CONTENT_PLANS` (via `CONTENT_PLAN_TRENDS`)
2. **Content Planning** → `CONTENT_PLANS` (created by agents)
3. **Approval** → `APPROVALS` (for plans and content)
4. **Content Generation** → `CONTENT` (from approved plans)
5. **Video Metadata** → `VIDEO_METADATA` (for video content only)
6. **Engagement** → `ENGAGEMENTS` (on published content)

### Video Metadata Storage

Video metadata is stored in a **normalized table** (`VIDEO_METADATA`) that:
- Has a **one-to-one relationship** with `CONTENT` (only for video content)
- Stores structured video-specific fields (duration, resolution, codec, etc.)
- Allows efficient querying of video properties
- Supports video-specific operations (thumbnails, captions, etc.)

### Approval Workflow

The approval system supports:
- **Content Plans**: Approval before content generation
- **Generated Content**: Approval before publishing
- **Human-in-the-Loop**: Three-tier confidence-based escalation
- **Auto-Approval**: For high-confidence content (>0.90)
- **Timeout Mechanism**: Auto-approve after expiration

---

## Database Design Principles

1. **Normalization**: Video metadata is normalized into a separate table for efficient querying
2. **Flexibility**: JSONB fields store flexible metadata (structure, key_messages, etc.)
3. **Traceability**: All relationships maintain foreign keys for audit trails
4. **Performance**: Indexes on frequently queried fields (status, agent_id, content_type)
5. **Scalability**: UUID primary keys support distributed systems

---

## Video Metadata Schema Details

The `VIDEO_METADATA` table stores comprehensive video information:

- **Technical Properties**: duration, resolution (width/height), format, codec, bitrate, frame rate
- **File Information**: file size, thumbnail URL
- **Accessibility**: audio presence, caption availability, caption URL
- **Display**: aspect ratio (16:9, 9:16, 1:1 for different platforms)

This normalized structure enables:
- Efficient queries for video content by technical properties
- Platform-specific optimization (TikTok: 9:16, YouTube: 16:9)
- Content discovery by video characteristics
- Analytics on video performance by metadata

---

## References

- **Database Schema**: `specs/database/schema.sql`
- **Technical Specifications**: `specs/technical.md`
- **Functional Specifications**: `specs/functional.md`
- **Master Specification**: `specs/_meta.md`

---

**This ERD represents the complete database structure for Project Chimera, including normalized video metadata storage.**

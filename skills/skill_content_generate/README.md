# Skill: Content Generation

**Skill ID**: `skill_content_generate`  
**Version**: 1.0.0  
**Status**: 📋 **Contract Defined** (Implementation pending)

---

## Purpose

The Content Generation skill enables Chimera agents to generate multimodal content (text, images, videos) based on trends, content plans, and persona guidelines. This skill is the core creative capability that produces the actual content artifacts.

**Related User Stories**: 
- `specs/functional.md` US-006: Generate Text Content
- `specs/functional.md` US-007: Generate Image Content
- `specs/functional.md` US-008: Generate Video Content
- `specs/functional.md` US-009: Request Human Approval for Generated Content

---

## Use Cases

1. **Text Generation**: Create social media posts, captions, articles
2. **Image Generation**: Generate thumbnails, graphics, illustrations
3. **Video Generation**: Create short-form videos, reels, TikTok content
4. **Multimodal Content**: Generate content packages with text, images, and video
5. **Content Variations**: Generate multiple variations for A/B testing

---

## Input/Output Contract

### Input Contract

See `contract.json` for complete JSON Schema definition.

**Required Fields**:
- `content_type` (string): Type of content to generate
  - Valid values: "text", "image", "video", "multimodal"
- `prompt` (string): Content generation prompt

**Optional Fields**:
- `style` (string): Persona style guide reference
- `character_reference_id` (string): Character consistency lock ID for visual content

**Example Input**:
```json
{
  "content_type": "text",
  "prompt": "Create a Twitter post about AI influencers, casual tone, include 3 hashtags",
  "style": "professional-casual",
  "character_reference_id": null
}
```

**Example Input (Image)**:
```json
{
  "content_type": "image",
  "prompt": "A futuristic AI influencer in a modern cityscape, vibrant colors, 16:9 aspect ratio",
  "style": "futuristic",
  "character_reference_id": "char_12345"
}
```

**Example Input (Video)**:
```json
{
  "content_type": "video",
  "prompt": "Create a 30-second video about the future of AI content creation, upbeat music, fast cuts",
  "style": "energetic",
  "character_reference_id": "char_12345"
}
```

### Output Contract

See `contract.json` for complete JSON Schema definition.

**Required Fields**:
- `content_url` (string): URL or path to generated content
- `metadata` (object): Content metadata
- `confidence` (number, 0-1): Confidence score for content quality

**Metadata Structure**:
- `platform` (string): Target platform (twitter, instagram, tiktok, youtube)
- `format` (string): File format (jpg, png, mp4, etc.)
- `dimensions` (object): Width and height (for images/videos)
- `duration` (number): Duration in seconds (for video)

**Example Output (Text)**:
```json
{
  "content_url": "s3://chimera-content/text/post_abc123.txt",
  "metadata": {
    "platform": "twitter",
    "format": "text",
    "hashtags": ["#AI", "#Influencers", "#Future"],
    "word_count": 280
  },
  "confidence": 0.88
}
```

**Example Output (Image)**:
```json
{
  "content_url": "s3://chimera-content/images/img_xyz789.jpg",
  "metadata": {
    "platform": "instagram",
    "format": "jpg",
    "dimensions": {
      "width": 1080,
      "height": 1080
    },
    "file_size": 245678
  },
  "confidence": 0.92
}
```

**Example Output (Video)**:
```json
{
  "content_url": "s3://chimera-content/videos/vid_def456.mp4",
  "metadata": {
    "platform": "tiktok",
    "format": "mp4",
    "dimensions": {
      "width": 1080,
      "height": 1920
    },
    "duration": 30.5,
    "file_size": 5242880
  },
  "confidence": 0.85
}
```

---

## MCP Dependencies

This skill requires the following runtime MCP servers:

1. **Text Generation**:
   - LLM MCP (Claude/GPT): Text content generation
   - No external MCP required (uses internal LLM)

2. **Image Generation**:
   - **Ideogram MCP** (`@modelcontextprotocol/server-ideogram`):
     - Tool: `generate_image` - Generate images from prompts
     - Tool: `upscale_image` - Upscale generated images
   - **Midjourney MCP** (`@modelcontextprotocol/server-midjourney`):
     - Tool: `generate_image` - Alternative image generation
     - Tool: `vary_image` - Create variations

3. **Video Generation**:
   - **Runway MCP** (`@modelcontextprotocol/server-runway`):
     - Tool: `generate_video` - Generate videos from prompts
     - Tool: `extend_video` - Extend video duration
     - Tool: `add_audio` - Add audio to videos

**Note**: These are runtime MCP servers, separate from development MCP servers. See `research/tooling_strategy.md` for the distinction.

---

## Implementation Notes

### Content Type Handling

1. **Text Content**:
   - Use LLM (Claude/GPT) for generation
   - Apply persona style guidelines
   - Include relevant hashtags and mentions
   - Validate length constraints per platform

2. **Image Content**:
   - Use Ideogram or Midjourney MCP
   - Apply character reference for consistency
   - Optimize dimensions for target platform
   - Generate thumbnails for preview

3. **Video Content**:
   - Use Runway MCP for generation
   - Add captions and audio
   - Optimize format and duration for platform
   - Generate preview thumbnails

### Quality Assurance

1. **Content Validation**: Check content meets platform requirements
2. **Style Compliance**: Verify content matches persona style
3. **Safety Checks**: Filter inappropriate content
4. **Confidence Scoring**: Calculate confidence based on quality metrics

### Error Handling

1. **Generation Failures**: Retry with modified prompts
2. **API Rate Limits**: Implement backoff and queuing
3. **Storage Failures**: Handle S3/storage errors gracefully
4. **Invalid Input**: Validate input and return clear errors

**Error Response Format**:
```json
{
  "error": {
    "code": "GENERATION_FAILED",
    "message": "Image generation failed: API timeout",
    "content_type": "image",
    "retryable": true
  }
}
```

### Performance Considerations

1. **Async Generation**: Generate content asynchronously for long operations
2. **Caching**: Cache similar content generations
3. **Batch Processing**: Batch multiple content generations when possible
4. **Resource Management**: Monitor GPU/API resource usage

### Logging

All skill executions must be logged with:
- Input parameters (excluding sensitive prompts)
- Content type and platform
- Generation time
- File size and dimensions
- Confidence scores
- Errors encountered

---

## Examples

### Example 1: Text Content Generation

**Input**:
```json
{
  "content_type": "text",
  "prompt": "Create an Instagram caption about sustainable fashion, include 5 hashtags, emoji-friendly",
  "style": "eco-conscious"
}
```

**Expected Output**:
```json
{
  "content_url": "s3://chimera-content/text/insta_caption_001.txt",
  "metadata": {
    "platform": "instagram",
    "format": "text",
    "hashtags": ["#SustainableFashion", "#EcoFriendly", "#SlowFashion", "#EthicalFashion", "#GreenStyle"],
    "word_count": 120,
    "has_emoji": true
  },
  "confidence": 0.91
}
```

### Example 2: Image Content Generation

**Input**:
```json
{
  "content_type": "image",
  "prompt": "A minimalist fashion influencer in a modern apartment, natural lighting, Instagram square format",
  "style": "minimalist",
  "character_reference_id": "char_fashion_001"
}
```

**Expected Output**:
```json
{
  "content_url": "s3://chimera-content/images/fashion_001.jpg",
  "metadata": {
    "platform": "instagram",
    "format": "jpg",
    "dimensions": {
      "width": 1080,
      "height": 1080
    },
    "file_size": 456789,
    "thumbnail_url": "s3://chimera-content/thumbnails/fashion_001_thumb.jpg"
  },
  "confidence": 0.87
}
```

### Example 3: Video Content Generation

**Input**:
```json
{
  "content_type": "video",
  "prompt": "Create a 15-second TikTok video about morning routines, fast-paced editing, upbeat music",
  "style": "energetic",
  "character_reference_id": "char_lifestyle_001"
}
```

**Expected Output**:
```json
{
  "content_url": "s3://chimera-content/videos/morning_routine_001.mp4",
  "metadata": {
    "platform": "tiktok",
    "format": "mp4",
    "dimensions": {
      "width": 1080,
      "height": 1920
    },
    "duration": 15.2,
    "file_size": 3145728,
    "has_audio": true,
    "has_captions": true
  },
  "confidence": 0.83
}
```

---

## Testing Requirements

See `specs/functional.md` US-006, US-007, US-008 for acceptance criteria:

- ✅ Generate content aligned with content plans
- ✅ Follow brand voice and style guidelines
- ✅ Include relevant hashtags and mentions
- ✅ Generate multiple variations for A/B testing
- ✅ Validate content for quality and safety
- ✅ Log all content generation actions

---

## References

- **Contract Schema**: `contract.json` (this directory)
- **Functional Specs**: `specs/functional.md` (US-006, US-007, US-008, US-009)
- **Technical Specs**: `specs/technical.md` (Content Generation API)
- **Database Schema**: `specs/database/schema.sql` (content table)
- **Tooling Strategy**: `research/tooling_strategy.md` (MCP vs Skills)

---

**This skill enables agents to generate multimodal content, serving as the creative engine of the Chimera system.**

# Executable Skill Contracts

**Prepared By**: habeneyasu  
**Repository**: [https://github.com/habeneyasu/chimera-factory](https://github.com/habeneyasu/chimera-factory)

## Overview

This directory contains executable Pydantic models for all skill contracts. These models provide:

1. **Type Safety**: Python type hints for IDE support
2. **Validation**: Automatic input/output validation
3. **Documentation**: Self-documenting via Pydantic's schema generation
4. **Code Generation**: Can be used to generate client/server code

## Usage

```python
from specs.skills import (
    TrendResearchInput,
    TrendResearchOutput,
    ContentGenerateInput,
    ContentGenerateOutput,
    EngagementManageInput,
    EngagementManageOutput
)

# Validate input
input_data = TrendResearchInput(
    topic="AI influencers",
    sources=["twitter", "news"],
    timeframe="24h"
)

# Execute skill (implementation in Task 2.3)
output = execute_trend_research(input_data)

# Output is automatically validated
assert isinstance(output, TrendResearchOutput)
assert 0.0 <= output.confidence <= 1.0
```

## Contract Alignment

Each Pydantic model in this directory corresponds to a `contract.json` file in `skills/`:

- `TrendResearchInput/Output` ↔ `skills/skill_trend_research/contract.json`
- `ContentGenerateInput/Output` ↔ `skills/skill_content_generate/contract.json`
- `EngagementManageInput/Output` ↔ `skills/skill_engagement_manage/contract.json`

## Validation

Contracts are validated using:

```bash
# Validate Pydantic models
python -m pytest specs/skills/ -v

# Validate JSON Schema alignment
make spec-check
```

"""
Skills module for Project Chimera.

Skills are modular agent capabilities that follow input/output contracts.

Reference: 
- specs/functional.md (User Stories)
- skills/skill_*/README.md (Skill documentation)
- skills/skill_*/contract.json (Skill contracts)
"""

from . import skill_trend_research
from . import skill_content_generate
from . import skill_engagement_manage

__all__ = [
    "skill_trend_research",
    "skill_content_generate",
    "skill_engagement_manage",
]

# Specifications: Project Chimera

**Prepared By**: habeneyasu  
**Repository**: [https://github.com/habeneyasu/chimera-factory](https://github.com/habeneyasu/chimera-factory)

## Overview

This directory contains executable specifications for Project Chimera. All specs are defined using formal schemas (Pydantic models, JSON Schema) to ensure machine-readability and validation.

## Spec Structure

- **`technical.md`**: Technical architecture and API specifications
- **`api/`**: OpenAPI/JSON Schema definitions for all APIs
- **`database/`**: Database schemas and ERD
- **`skills/`**: Skill contract definitions (Pydantic models)

## Spec Fidelity Principles

1. **Executable**: All specs must be parseable by tools (Pydantic, JSON Schema validators)
2. **Versioned**: Specs are version-controlled and changes require review
3. **Validated**: Code must align with specs (enforced via `make spec-check`)
4. **Traceable**: All implementation must reference spec sections

## Usage

```bash
# Validate specs
make spec-check

# Generate code from specs (future)
make spec-generate
```

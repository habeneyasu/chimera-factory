# Repository Size Optimization Guide

**Issue**: Submission exceeds maximum size limit.

## Current Repository Size

- **Git Repository**: ~2.21 MiB (normal)
- **Largest File**: `uv.lock` (192KB) - **Required** for explicit dependency locking
- **Tracked Files**: 110 files

## Optimization Options

### Option 1: Remove Research Files (Recommended)

Research files are documentation of the research process but may not be required for submission:

```bash
# Remove research directory from git (keeps local files)
git rm -r --cached research/
echo "research/" >> .gitignore
git commit -m "chore: remove research files to reduce repository size"
```

**Size Reduction**: ~112KB

**Note**: Research findings are already incorporated into specs and ADRs.

### Option 2: Exclude uv.lock (Not Recommended)

`uv.lock` is required for explicit dependency locking (containerization requirement). However, if absolutely necessary:

```bash
# Remove uv.lock from git
git rm --cached uv.lock
echo "uv.lock" >> .gitignore
git commit -m "chore: exclude uv.lock to reduce size (use requirements.txt instead)"
```

**Size Reduction**: ~192KB

**Warning**: This breaks the explicit dependency locking requirement. Use only if absolutely necessary.

### Option 3: Clean Git History

If repository has large history:

```bash
# Create a fresh repository with current state only
git checkout --orphan fresh-start
git add .
git commit -m "Initial commit: Project Chimera submission"
git branch -D main
git branch -m main
```

**Warning**: This removes all git history. Only use if necessary.

### Option 4: Remove Large Documentation Files

Some documentation files might be consolidated:

- `docs/TEST_CRITERIA.md` (35KB) - Could be summarized
- `research/submission_report_feb5_task_2.md` (37KB) - Research documentation
- `research/submission_report_feb4_task_1.md` (28KB) - Research documentation

## Recommended Action

**Remove research files** (Option 1) as they're not required for submission:

1. Research findings are already in specs and ADRs
2. Reduces size by ~112KB
3. Keeps all required functionality intact

## Verification

After optimization, verify size:

```bash
# Check repository size
git count-objects -vH

# Check largest files
git ls-files | xargs ls -lh | awk '{print $5, $9}' | sort -h | tail -10
```

## Required Files (Do Not Remove)

- ✅ `specs/` - All specification files (required)
- ✅ `src/` - Source code (required)
- ✅ `tests/` - Test files (required)
- ✅ `skills/` - Skill contracts (required)
- ✅ `static/` - Frontend files (required)
- ✅ `uv.lock` - Dependency lock file (required for containerization)
- ✅ `.cursor/rules` - Agent rules (required)
- ✅ `README.md`, `CONTRIBUTING.md`, `docs/` - Documentation (required)

---

**Reference**: Challenge requirements focus on specs, tests, skills, Dockerfile, Makefile, workflows, and .cursor/rules.

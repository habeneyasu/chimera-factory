#!/bin/bash
# Create a clean submission repository without git history
# This reduces repository size by removing all commit history

set -e

echo "=========================================="
echo "Creating Clean Submission Repository"
echo "=========================================="
echo ""
echo "⚠️  WARNING: This will create a NEW repository without git history"
echo "   Original repository will be backed up to ../chimera-factory-backup"
echo ""

read -p "Continue? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 1
fi

# Get current directory
CURRENT_DIR=$(pwd)
BACKUP_DIR="../chimera-factory-backup-$(date +%Y%m%d-%H%M%S)"
CLEAN_DIR="${CURRENT_DIR}-clean"

echo ""
echo "Step 1: Creating backup..."
cp -r "$CURRENT_DIR" "$BACKUP_DIR"
echo "✅ Backup created: $BACKUP_DIR"

echo ""
echo "Step 2: Creating clean repository..."
cd "$CURRENT_DIR"

# Create a temporary directory for clean repo
TEMP_DIR=$(mktemp -d)
echo "   Working in: $TEMP_DIR"

# Copy all files except .git
rsync -av --exclude='.git' --exclude='.venv' --exclude='node_modules' \
    --exclude='__pycache__' --exclude='*.pyc' --exclude='.coverage' \
    --exclude='.pytest_cache' --exclude='.mypy_cache' --exclude='.ruff_cache' \
    "$CURRENT_DIR/" "$TEMP_DIR/"

cd "$TEMP_DIR"

# Initialize new git repository
git init
git add .
git commit -m "Initial commit: Project Chimera submission

- Spec-driven development framework
- OpenClaw integration with local sovereign runtime
- TDD with failing tests
- Full CI/CD pipeline
- Security containment policy
- HITL review interface"

# Calculate size
CLEAN_SIZE=$(du -sh .git | cut -f1)
TRACKED_FILES=$(git ls-files | wc -l)

echo ""
echo "=========================================="
echo "Clean Repository Created"
echo "=========================================="
echo "Git size: $CLEAN_SIZE"
echo "Tracked files: $TRACKED_FILES"
echo ""
echo "Repository location: $TEMP_DIR"
echo ""
echo "Next steps:"
echo "1. Review the clean repository: cd $TEMP_DIR"
echo "2. If satisfied, replace current repo:"
echo "   cd $CURRENT_DIR"
echo "   rm -rf .git"
echo "   cp -r $TEMP_DIR/.git ."
echo "   git checkout ."
echo ""
echo "Or create a zip for submission:"
echo "   cd $TEMP_DIR"
echo "   zip -r ../chimera-factory-submission.zip . -x '*.git*'"
echo ""

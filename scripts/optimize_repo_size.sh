#!/bin/bash
# Repository Size Optimization Script
# Removes non-essential files to reduce submission size

set -e

echo "=========================================="
echo "Repository Size Optimization"
echo "=========================================="
echo ""

# Check current size
echo "Current repository size:"
git count-objects -vH
echo ""

# Option 1: Remove research files (recommended)
echo "Option 1: Remove research files (~112KB reduction)"
echo "Research findings are already in specs/ and docs/adr/"
read -p "Remove research/ directory? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    git rm -r --cached research/ 2>/dev/null || echo "Research files not tracked"
    echo "research/" >> .gitignore
    echo "✅ Research files removed from git"
fi

# Option 2: Clean cache files (if accidentally committed)
echo ""
echo "Cleaning cache files..."
git rm -r --cached .pytest_cache .mypy_cache .ruff_cache 2>/dev/null || true
echo "✅ Cache files cleaned"

# Option 3: Remove large log files
echo ""
echo "Checking for large log files..."
find . -type f -name "*.log" -size +10k -exec git rm --cached {} \; 2>/dev/null || true
echo "✅ Log files cleaned"

# Final size check
echo ""
echo "=========================================="
echo "Optimization Complete"
echo "=========================================="
echo ""
echo "New repository size:"
git count-objects -vH
echo ""
echo "Largest tracked files:"
git ls-files | xargs ls -lh 2>/dev/null | awk '{print $5, $9}' | sort -h | tail -10
echo ""
echo "Next steps:"
echo "1. Review changes: git status"
echo "2. Commit: git commit -m 'chore: optimize repository size'"
echo "3. Verify: git count-objects -vH"

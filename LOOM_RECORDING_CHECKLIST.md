# Loom Video Recording Checklist

## ✅ Pre-Recording Setup

- [ ] Loom app installed and ready
- [ ] Cursor IDE open with project loaded
- [ ] Terminal open in project directory
- [ ] Browser/editor closed (clean screen)
- [ ] Audio/microphone tested
- [ ] Screen resolution set (1080p recommended)

---

## 📹 Recording Sections

### Section 1: Spec Structure & OpenClaw (2:00)
- [ ] Show `specs/` directory structure
- [ ] Open `specs/_meta.md` (briefly)
- [ ] Open `specs/functional.md` (briefly)
- [ ] Open `specs/technical.md` (briefly)
- [ ] Open `specs/database/schema.sql` (briefly)
- [ ] Open `specs/api/orchestrator.yaml` (briefly)
- [ ] Open `specs/openclaw_integration.md` (scroll through)
- [ ] Show `.cursor/rules` file (head -60)
- [ ] Mention OpenClaw integration points

### Section 2: Failing Tests / TDD (1:30)
- [ ] Navigate to `tests/` directory
- [ ] Show test structure (contracts, integration, unit)
- [ ] Run contract test command:
  ```bash
  uv run pytest tests/contracts/test_skills_interface.py -v --tb=short
  ```
- [ ] Explain TDD cycle (RED → GREEN → REFACTOR)
- [ ] Run integration test (optional):
  ```bash
  uv run pytest tests/integration/ -v --tb=short -k "trend" | head -30
  ```
- [ ] Show test results/output

### Section 3: IDE Agent Context (1:30)
- [ ] Open Cursor chat panel
- [ ] Ask Question 1: "What is the database architecture for this project?"
  - [ ] Show agent response
  - [ ] Verify it references specs
- [ ] Ask Question 2: "How does the trend research skill work? What are its inputs and outputs?"
  - [ ] Show agent response
  - [ ] Open `skills/skill_trend_research/contract.json` to verify
- [ ] Ask Question 3: "What should I do before implementing a new feature? What's the Prime Directive?"
  - [ ] Show agent response
  - [ ] Open `.cursor/rules` to show source

---

## 🎬 Recording Tips

- [ ] Speak clearly and at moderate pace
- [ ] Use cursor to highlight important parts
- [ ] Pause briefly when showing key files
- [ ] Keep total time under 5 minutes
- [ ] Don't rush through sections

---

## ✅ Post-Recording

- [ ] Review video for clarity
- [ ] Check audio quality
- [ ] Verify all sections are covered
- [ ] Ensure video is under 5 minutes
- [ ] Upload to Loom
- [ ] Set appropriate title and privacy
- [ ] Copy Loom link for submission

---

## 📝 Quick Commands Reference

```bash
# Show specs
find specs/ -type f | head -15

# Show OpenClaw
head -50 specs/openclaw_integration.md

# Run tests
uv run pytest tests/contracts/ -v --tb=short

# Show rules
head -60 .cursor/rules

# Show contract
cat skills/skill_trend_research/contract.json
```

---

## 💬 Sample Questions for Agent

1. "What is the database architecture for this project? Explain the hybrid approach."
2. "How does the trend research skill work? What are its inputs and outputs according to the contract?"
3. "What should I do before implementing a new feature? What's the Prime Directive?"
4. (Optional) "What API endpoints are available and what do they do?"

---

**Ready to record!** 🎥

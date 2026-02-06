# Loom Video Quick Guide - 5 Minute Demo

## 🎯 Three Sections (5 Minutes Total)

### 1️⃣ Spec Structure & OpenClaw (2 min)
### 2️⃣ Failing Tests / TDD (1.5 min)  
### 3️⃣ IDE Agent Context (1.5 min)

---

## 📋 Section 1: Spec Structure & OpenClaw (2:00)

### What to Show:
1. **Open `specs/` folder** → Show structure
2. **Quick tour of key files**:
   - `specs/_meta.md` - Development principles
   - `specs/functional.md` - User stories
   - `specs/technical.md` - Architecture
   - `specs/database/schema.sql` - Database
   - `specs/api/orchestrator.yaml` - API spec
3. **Show `specs/openclaw_integration.md`** → Scroll through, highlight key points
4. **Show `.cursor/rules`** → "This enables our IDE agent to understand the project"

**Script**: 
> "Our specs directory provides a single source of truth. The OpenClaw integration plan outlines how we'll integrate agent patterns and MCP protocols."

---

## 🧪 Section 2: Failing Tests / TDD (1:30)

### What to Show:
1. **Navigate to `tests/`** → Show structure (contracts, integration, unit)
2. **Run contract test**:
   ```bash
   uv run pytest tests/contracts/test_skills_interface.py -v --tb=short
   ```
3. **Show test output** → Explain TDD: RED (fail) → GREEN (pass) → REFACTOR
4. **Run integration test** (may show failures/skips):
   ```bash
   uv run pytest tests/integration/ -v --tb=short -k "trend" | head -30
   ```

**Script**:
> "We follow TDD: write tests first, then implement. These tests serve as living documentation and ensure our code matches specifications."

---

## 🤖 Section 3: IDE Agent Context (1:30)

### What to Show:
**Open Cursor chat and ask these questions:**

1. **Question 1** (0:15 - 0:45):
   ```
   "What is the database architecture for this project? Explain the hybrid approach."
   ```
   - Show agent response
   - Highlight it references specs

2. **Question 2** (0:45 - 1:15):
   ```
   "How does the trend research skill work? What are its inputs and outputs?"
   ```
   - Show agent response
   - Open `skills/skill_trend_research/contract.json` to verify

3. **Question 3** (1:15 - 1:30):
   ```
   "What should I do before implementing a new feature? What's the Prime Directive?"
   ```
   - Show agent response
   - Open `.cursor/rules` to show where answer comes from

**Script**:
> "Our IDE agent has full project context through rules and specs, enabling accurate, context-aware assistance."

---

## ⚡ Quick Commands Reference

```bash
# Show specs
find specs/ -type f | grep -E "\.(md|yaml|sql)$" | head -15

# Show OpenClaw plan
head -80 specs/openclaw_integration.md

# Run tests
uv run pytest tests/contracts/ -v --tb=short

# Show rules
head -60 .cursor/rules
```

---

## ✅ Pre-Recording Checklist

- [ ] Cursor IDE open
- [ ] Terminal ready in project directory
- [ ] Specs files visible/accessible
- [ ] Tests ready to run
- [ ] Screen clean (close extra windows)
- [ ] Loom recording app ready

---

## 🎬 Recording Tips

1. **Start recording** → Introduce yourself and project
2. **Keep it under 5 minutes** → Practice timing
3. **Speak clearly** → Explain what you're showing
4. **Use cursor to highlight** → Point at important parts
5. **Don't rush** → Pause briefly on key files

---

## 📝 Script Template

**Opening** (0:00):
> "Hi, I'm [Name]. This is Project Chimera Factory. I'll show you our spec structure, TDD approach, and IDE agent integration."

**Section 1** (0:15):
> "First, our specs directory..." [Show files]

**Section 2** (1:00):
> "Now, our TDD approach..." [Run tests]

**Section 3** (2:30):
> "Finally, our IDE agent..." [Ask questions]

**Closing** (4:30):
> "This demonstrates our structured approach with specs, tests, and AI assistance. Thanks for watching!"

---

**Ready to record!** 🎥

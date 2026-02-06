# Loom Video Script - Project Chimera Factory

**Duration**: Maximum 5 minutes  
**Purpose**: Demonstrate Spec Structure, OpenClaw Integration, TDD Approach, and IDE Agent Context

---

## Video Structure (5 Minutes)

### **Section 1: Spec Structure & OpenClaw Integration Plan** (2 minutes)
### **Section 2: Failing Tests (TDD Approach)** (1.5 minutes)
### **Section 3: IDE Agent Context Demonstration** (1.5 minutes)

---

## Section 1: Spec Structure & OpenClaw Integration Plan (2:00)

### **Opening (0:00 - 0:15)**
**Script**: 
> "Hi, I'm [Your Name], and this is Project Chimera Factory. I'll walk you through our spec structure and OpenClaw integration plan."

**Actions**:
- Show project root directory
- Navigate to `specs/` folder

### **Spec Structure Overview (0:15 - 1:00)**
**Script**:
> "Our specs directory follows a structured approach with clear separation of concerns."

**Actions**:
1. **Show `specs/` directory structure**:
   ```bash
   tree specs/ -L 2
   # or
   ls -la specs/
   ```

2. **Open key files in order**:
   - `specs/_meta.md` - "This is our meta specification that defines our development principles"
   - `specs/functional.md` - "Functional requirements and user stories"
   - `specs/technical.md` - "Technical architecture and API contracts"
   - `specs/database/schema.sql` - "Database schema definitions"
   - `specs/api/orchestrator.yaml` - "API specifications in OpenAPI format"

3. **Show skills structure**:
   ```bash
   ls -la specs/skills/
   ls -la skills/
   ```
   - "Each skill has a contract defined in the specs, and implementation in the skills directory"

### **OpenClaw Integration Plan (1:00 - 2:00)**
**Script**:
> "Now let me show you our OpenClaw integration plan."

**Actions**:
1. **Open `specs/openclaw_integration.md`**:
   - Scroll through the document
   - Highlight key sections:
     - Integration architecture
     - Agent patterns
     - MCP integration points
     - Workflow definitions

2. **Show OpenClaw-specific files**:
   ```bash
   cat .cursor/rules | head -50
   ```
   - "Our `.cursor/rules` file contains OpenClaw-specific rules and agent instructions"

3. **Show MCP configuration**:
   ```bash
   cat .cursor/mcp.json
   ```
   - "MCP configuration for external integrations"

**Closing for Section 1**:
> "This structured approach ensures consistency and enables our IDE agent to understand the project context."

---

## Section 2: Failing Tests (TDD Approach) (1:30)

### **Introduction (0:00 - 0:15)**
**Script**:
> "Now I'll demonstrate our Test-Driven Development approach by showing failing tests."

**Actions**:
- Navigate to `tests/` directory
- Show test structure

### **Show Contract Tests (0:15 - 0:45)**
**Script**:
> "We start with contract tests that define the expected behavior before implementation."

**Actions**:
1. **Show contract test file**:
   ```bash
   cat tests/contracts/test_skills_interface.py | head -80
   ```

2. **Run a specific contract test that should fail or show TDD pattern**:
   ```bash
   uv run pytest tests/contracts/test_skills_interface.py::TestTrendResearchSkill::test_trend_research_skill_import -v
   ```

3. **Explain the TDD cycle**:
   - "We write tests first (RED)"
   - "Then implement to make them pass (GREEN)"
   - "Then refactor (REFACTOR)"

### **Show Integration Tests (0:45 - 1:15)**
**Script**:
> "Our integration tests verify end-to-end functionality."

**Actions**:
1. **Show integration test structure**:
   ```bash
   ls -la tests/integration/
   ```

2. **Run integration tests (may show some failures or skipped tests)**:
   ```bash
   uv run pytest tests/integration/ -v --tb=short -k "test_trend_research" | head -30
   ```

3. **Show test output**:
   - Point out test results
   - Explain how tests drive implementation

### **Demonstrate TDD Workflow (1:15 - 1:30)**
**Script**:
> "This TDD approach ensures we build exactly what's specified and catch issues early."

**Actions**:
- Show test coverage or test results summary
- Highlight how tests are organized by type (contract, integration, unit)

**Closing for Section 2**:
> "Our tests serve as living documentation and ensure our implementation matches our specifications."

---

## Section 3: IDE Agent Context Demonstration (1:30)

### **Introduction (0:00 - 0:15)**
**Script**:
> "Finally, let me demonstrate how our IDE agent uses the rules and context to answer questions about the project."

**Actions**:
- Open Cursor IDE
- Show `.cursor/rules` file briefly

### **Ask Question 1: Architecture (0:15 - 0:45)**
**Script**:
> "Let me ask the agent about our architecture."

**Question to ask in Cursor chat**:
```
"What is the database architecture for this project? Explain the hybrid database approach."
```

**Expected Response Points**:
- Should mention PostgreSQL, Weaviate, Redis, On-Chain
- Should reference `specs/technical.md` or `specs/database/schema.sql`
- Should show understanding of the architecture

**Actions**:
- Type the question
- Show the agent's response
- Highlight how it references specs

### **Ask Question 2: Skill Implementation (0:45 - 1:15)**
**Script**:
> "Now let me ask about a specific skill implementation."

**Question to ask in Cursor chat**:
```
"How does the trend research skill work? What are its inputs and outputs according to the contract?"
```

**Expected Response Points**:
- Should reference `skills/skill_trend_research/contract.json`
- Should mention input/output structure
- Should reference `specs/technical.md` or skill documentation

**Actions**:
- Type the question
- Show the agent's response
- Navigate to the contract file to verify accuracy

### **Ask Question 3: Development Rules (1:15 - 1:30)**
**Script**:
> "Let me verify the agent follows our development rules."

**Question to ask in Cursor chat**:
```
"What should I do before implementing a new feature? What's the Prime Directive?"
```

**Expected Response Points**:
- Should mention checking specs first
- Should reference the Prime Directive from `.cursor/rules`
- Should mention TDD approach

**Actions**:
- Type the question
- Show the agent's response
- Open `.cursor/rules` to show where the answer comes from

**Closing for Section 3**:
> "As you can see, our IDE agent has full context of the project through our rules and specifications, enabling it to provide accurate, context-aware assistance."

---

## Final Closing (0:15)

**Script**:
> "Thank you for watching. This demonstrates our structured approach to building Project Chimera Factory with clear specifications, test-driven development, and AI-assisted development through OpenClaw integration."

---

## Pre-Recording Checklist

### **Before Recording**:
- [ ] All specs are up to date
- [ ] Test suite is ready (some tests may fail to show TDD)
- [ ] `.cursor/rules` file is current
- [ ] Cursor IDE is open and ready
- [ ] Terminal is ready with project directory
- [ ] Screen is clean (close unnecessary windows)
- [ ] Audio is working (if doing voiceover)

### **Test Commands Ready**:
```bash
# Show specs structure
tree specs/ -L 2 || find specs/ -type f -name "*.md" -o -name "*.yaml" -o -name "*.sql"

# Show skills structure
ls -la skills/

# Run contract tests
uv run pytest tests/contracts/ -v --tb=short

# Run integration tests (may show failures)
uv run pytest tests/integration/ -v --tb=short -k "test_trend" | head -40

# Show rules file
head -100 .cursor/rules
```

### **Questions to Prepare for Agent**:
1. "What is the database architecture for this project?"
2. "How does the trend research skill work? What are its inputs and outputs?"
3. "What should I do before implementing a new feature? What's the Prime Directive?"
4. (Optional) "What API endpoints are available and what do they do?"

---

## Recording Tips

1. **Screen Recording Setup**:
   - Use Loom desktop app or browser extension
   - Record at 1080p if possible
   - Enable system audio if doing voiceover

2. **Screen Layout**:
   - Terminal on left/right side
   - Cursor IDE in main area
   - Keep specs/docs visible when needed

3. **Pacing**:
   - Don't rush through sections
   - Pause briefly when showing important files
   - Speak clearly and at moderate pace

4. **Highlights**:
   - Use cursor to point at important sections
   - Zoom in on key code snippets if needed
   - Show file paths clearly

5. **Practice Run**:
   - Do a practice run first
   - Time each section
   - Adjust script if needed to fit 5 minutes

---

## Post-Recording

1. **Review the video**:
   - Check audio quality
   - Verify all sections are clear
   - Ensure it's under 5 minutes

2. **Upload to Loom**:
   - Upload the recording
   - Add title: "Project Chimera Factory - Spec Structure, TDD, and IDE Agent Demo"
   - Set appropriate privacy settings

3. **Share the link**:
   - Copy the Loom video link
   - Include in your submission

---

## Quick Reference Commands

```bash
# 1. Show specs structure
find specs/ -type f | head -20

# 2. Show OpenClaw integration
cat specs/openclaw_integration.md | head -50

# 3. Run tests (TDD demonstration)
uv run pytest tests/contracts/test_skills_interface.py::TestTrendResearchSkill -v

# 4. Show rules
head -50 .cursor/rules

# 5. Show skill contract
cat skills/skill_trend_research/contract.json | jq .
```

---

**Good luck with your recording!** 🎥

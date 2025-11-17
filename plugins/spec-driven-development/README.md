# Spec-Driven Development Plugin

A comprehensive development workflow plugin for Claude Code that follows a specification-first approach: **Clarify Requirements**, **Design Architecture**, **Create Plan**, and **Implement** with rigorous testing.

## Overview

This plugin enhances your development workflow with a structured approach:

- **Requirements Definition**: Interactive Q&A or quick creation with review
- **Design Specification**: Technical design and architecture based on requirements
- **Implementation Planning**: UI-first planning for early visual feedback
- **Plan Execution**: Systematic implementation with testing and phase-by-phase validation

## Commands

The plugin provides six commands - choose between quick and thorough modes for requirements and design:

### Quick Mode Commands

#### `/sdd.create_requirements`

Creates requirements document from brief description with review cycle.

**Workflow:**
1. Provide brief project description (1-3 paragraphs)
2. AI generates complete `spec/requirements.md`
3. Review and request adjustments as needed
4. AI guides toward completion

**Best for:** Experienced developers, clear vision, want to move fast

**Output:** Complete requirements document with user stories and acceptance criteria

#### `/sdd.create_design`

Creates design document with AI filling in tech stack gaps.

**Workflow:**
1. Provide tech preferences (specific like "React, TypeScript" or "you decide")
2. AI fills gaps and generates `spec/design.md`
3. AI explicitly states decisions made
4. Review and request adjustments as needed
5. AI guides toward completion

**Best for:** Know your tech stack or trust AI decisions, want to move fast

**Output:** Comprehensive design document with tech stack and architecture

### Thorough Mode Commands

#### `/sdd.clarify_requirements`

Helps clarify project requirements by asking focused questions and documenting user needs.

**Workflow:**
1. Describe what you want to build
2. Answer clarifying questions about user needs, goals, use cases, and edge cases
3. Generates `spec/requirements.md` with user stories and acceptance criteria

**Best for:** Complex projects, want guided exploration, prefer answering questions

**Output:** Complete requirements document with user stories, functional requirements, and success criteria

#### `/sdd.clarify_design`

Clarifies technical design and architecture based on requirements.

**Workflow:**
1. Reads your requirements from `spec/requirements.md`
2. Asks about tech stack, architecture patterns, data storage, UI approach, and testing preferences
3. Generates `spec/design.md` with complete technical specifications

**Best for:** Want to think through architecture decisions, unfamiliar with options

**Output:** Comprehensive design document with tech stack, component breakdown, data models, and testing strategy

### Shared Commands

#### `/sdd.create_plan`

Creates detailed implementation plan based on requirements and design specifications.

**Workflow:**
1. Reads `spec/requirements.md` and `spec/design.md`
2. Auto-detects if project has UI and uses UI-first planning approach
3. Generates `spec/plan.md` with 3-5 phases of concrete tasks
4. Each task includes file paths, test requirements, verification steps, and success criteria

**Output:** Detailed implementation plan ready for execution (UI-first when applicable)

#### `/sdd.implement_plan`

Implements the project based on the approved implementation plan with rigorous testing.

**Workflow:**
1. Reads all spec documents (`plan.md`, `requirements.md`, `design.md`)
2. For each task:
   - Implement the code
   - Write tests
   - Run tests (max 3 attempts)
   - Manual verification if required
   - Update checkboxes in plan.md
3. Stops at end of each phase for human review

**Output:** Working implementation with all tests passing and checkboxes marked in plan.md

## Usage

### Choosing Your Workflow

**Quick Workflow (Create Mode)**
- You have a clear vision of what to build
- Experienced with your tech stack
- Want to move fast with one or two review rounds
- Trust AI to make reasonable assumptions

**Thorough Workflow (Clarify Mode)**
- Complex or unfamiliar project
- Want AI to guide you through considerations
- Prefer answering questions over reviewing assumptions
- Learning or exploring the problem space

Both workflows produce the same spec documents and lead to the same planning and implementation.

### Quick Workflow Example

```bash
# 1. Create requirements from brief description
/sdd.create_requirements
> "Build a personal task manager with tags and due dates..."
> [AI generates requirements.md] → Review → Adjust if needed

# 2. Create design with tech preferences
/sdd.create_design
> "React, TypeScript, local storage"
> [AI fills gaps, generates design.md] → Review → Adjust if needed

# 3. Generate implementation plan (UI-first when applicable)
/sdd.create_plan

# 4. Build it
/sdd.implement_plan
```

### Thorough Workflow Example

```bash
# 1. Interactive requirements clarification
/sdd.clarify_requirements
> [Answer 5-10 questions about needs, goals, edge cases]

# 2. Interactive design clarification
/sdd.clarify_design
> [Answer questions about tech stack, architecture, testing]

# 3. Generate implementation plan (UI-first when applicable)
/sdd.create_plan

# 4. Build it
/sdd.implement_plan
```

### Key Features

#### Documentation-First Philosophy

All commands follow a specification-first approach:
- Requirements drive design
- Design drives planning
- Plan drives implementation
- Every decision is documented and traceable

#### Early UI Visibility (UI-First Planning)

When your project has a user interface, plans automatically use UI-first approach:
- Phase 1: Project setup + basic UI shell
- Phase 2: Complete UI with mock/hardcoded data (fully interactive)
- Phase 3: Backend and data layer
- Phase 4: Integration (replace mocks with real data)
- Phase 5: Polish and testing

**Why UI-First?**
- See and interact with UI early (Phase 2) before investing in backend complexity
- Catch design misalignments when they're easy to fix
- Validate direction with working prototype using fake data
- UI with mocks is cheap to change; backend with real data is expensive to change
- Maintains momentum with tangible, visual progress

For projects without UI (APIs, CLIs, libraries), plans use appropriate structure.

#### Rigorous Testing

Implementation includes mandatory testing:
- Every task must have test requirements
- Tests must pass before moving to next task
- Max 3 test attempts before stopping for guidance
- Manual verification for UI/UX concerns

#### Phase-Based Execution

Implementation proceeds phase-by-phase:
- Each phase has clear boundaries
- Stop at end of each phase for human review
- Update checkboxes as tasks complete
- Never skip ahead without approval

#### Clear Verification

Every task includes:
- Specific verification steps
- Success criteria
- Test commands to run
- Manual checks if needed

## File Structure

The plugin creates a `spec/` directory with three documents:

```
spec/
├── requirements.md  (from /sdd.create_requirements or /sdd.clarify_requirements)
├── design.md        (from /sdd.create_design or /sdd.clarify_design)
└── plan.md          (from /sdd.create_plan, updated by /sdd.implement_plan)
```

## Best Practices

1. **Choose the Right Mode**: Use quick mode when you have a clear vision, thorough mode when exploring
2. **Don't Skip Steps**: Follow the workflow in order - each command builds on the previous
3. **Review Specs**: Check each spec document before moving to the next phase (adjust as needed)
4. **Trust UI-First**: For UI projects, seeing the interface with mock data first validates direction early
5. **Test Continuously**: Verify each task before proceeding
6. **Stop Between Phases**: Human review prevents mistakes and scope creep

## When to Use

This plugin is ideal for:
- Starting new projects or features from scratch
- Projects with clear or explorable scope
- When you want to see UI early (mock data before backend)
- Teams that value documentation
- Both quick iteration and thorough exploration
- Projects requiring rigorous testing

## Requirements

- Claude Code installed
- Basic understanding of software development concepts
- Clear project idea (for quick mode) or willingness to explore (for thorough mode)

## Philosophy

Spec-Driven Development emphasizes:
- **Clarity before code**: Understand requirements before designing
- **Design before implementation**: Plan architecture before coding
- **UI before backend**: When applicable, validate UI with mocks before building expensive backend
- **Testing as verification**: Every task must be verified
- **Phase-by-phase progress**: Stop for review, prevent mistakes
- **Documentation as communication**: Specs are the source of truth
- **Flexibility in approach**: Choose quick or thorough based on your needs

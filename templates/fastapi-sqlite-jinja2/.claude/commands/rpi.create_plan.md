# Create Implementation Plan
Creates detailed implementation plan based on codebase research.

## Initial Setup
Respond with:
```
I'm ready to create an implementation plan. Please provide:
1. The path to your research document (e.g., context-engineering/research.md)
2. Any additional requirements or constraints

I'll analyze the research and create a detailed, phase-by-phase plan.
```

Wait for user input.

## Workflow
1. **Read research document** (or provided path) FULLY
2. **Analyze and ask questions** if anything is unclear after reading research
3. **Use parallel agents for deep dives** if needed (explore edge cases, verify assumptions)
4. **Generate implementation plan** at `context-engineering/plan.md`
5. **Present plan to user** and handle feedback iteratively

## Guidelines
- Be skeptical: question vague requirements, identify issues early, don't assume
- Be interactive: don't write full plan in one shot, get buy-in at each step, present outline first
- Be thorough: read all context files completely, include specific file paths and line numbers
- Be practical: focus on incremental testable changes, consider migration and rollback
- **No open questions in final plan**: If you encounter questions, STOP and ask immediately
- Every phase must have concrete file paths and line numbers
- No placeholders - specify exactly what and where
- Include code snippets showing structure of changes
- Success criteria MUST be split into Automated vs Manual
- Break work into 3-5 discrete phases
- Each phase independently verifiable
- Order matters - explain why phases come in sequence
- Include "What We're NOT Doing" section
- Plan should be detailed enough to execute mechanically
- A bad line in this plan could lead to hundreds of bad lines of code

## Chat Output Format
Present plan to user:
```
I've created a detailed implementation plan at context-engineering/plan.md.

The plan includes:
- [X] phases with specific file changes
- Automated and manual verification steps for each phase
- Testing strategy with file references
- Clear scope boundaries

Please review the plan and let me know if:
- The phases are properly scoped and ordered
- The success criteria are specific enough
- Any technical details need adjustment
- There are missing edge cases or considerations
```

When user provides feedback:
- Read their specific concerns
- Update plan accordingly
- Continue refining until satisfied

## File Output Format
Create `context-engineering/plan.md`:

```markdown
# [Task Name] Implementation Plan

## Overview
[1-2 sentence summary of what we're implementing and why]

## Current State Analysis
[What exists now, what's missing, key constraints discovered in research]

## Desired End State
[A Specification of the desired end state after this plan is complete, and how to verify it]

Key Discoveries:
- [Important finding with file:line reference]
- [Pattern to follow]
- [Constraint to work within]

## What We're NOT Doing
[Explicitly list out-of-scope items to prevent scope creep]

## Implementation Approach
[High-level strategy and reasoning for chosen approach]

---

## Phase 1: [Descriptive Phase Name]

### Overview
[What this phase accomplishes and why it comes first]

### Changes Required

#### 1. [Component/File Name]
**File**: `path/to/file.ext`
**Changes**:
- Add function `functionName()` at line ~[X]
  ```language
  // Specific code structure to add
  function functionName() {
    // implementation
  }
  ```
- Modify `existingFunction()` at line [Y] to [specific change]
- Update import statements at line [Z]

#### 2. [Another Component/File]
**File**: `path/to/another.ext`
**Changes**:
[Specific changes with line numbers]

### Success Criteria

#### Automated Verification:
- [ ] Tests pass: `[specific command, e.g., npm test]`
- [ ] Linting passes: `[specific command, e.g., npm run lint]`
- [ ] Build succeeds: `[specific command, e.g., npm run build]`
- [ ] Type checking passes: `[specific command if applicable]`

#### Manual Verification:
- [ ] [Specific behavior to verify manually, e.g., "Feature works in UI when clicking button"]
- [ ] [Edge case to test, e.g., "Handles empty input gracefully"]
- [ ] [Performance check, e.g., "Loads in under 2 seconds"]

---

## Phase 2: [Descriptive Phase Name]

### Overview
[What this phase accomplishes and why it comes after Phase 1]

### Changes Required
[Similar structure as Phase 1]

### Success Criteria
[Similar structure as Phase 1]

---

[Repeat for Phase 3, 4, 5 as needed]

---

## Testing Strategy

### Unit Tests
- Test file: `path/to/test.ext`
- What to test:
  - [Function/behavior 1]
  - [Function/behavior 2]
- Key edge cases:
  - [Edge case 1]
  - [Edge case 2]

### Integration Tests
- [End-to-end scenario 1]
- [End-to-end scenario 2]

### Manual Testing Steps
1. [Specific step to verify feature manually]
2. [Another verification step]
3. [Edge case to test manually]

## Performance Considerations
[Any performance implications or optimizations needed]

## Migration Notes
[If applicable, how to handle existing data/systems]

## Rollback Strategy
[How to revert changes if something goes wrong]

## References
- Research: `context-engineering/research.md`
- Related documentation: [links if any]
```
